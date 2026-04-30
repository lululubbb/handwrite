"""
管理员路由模块
包含用户管理、使用统计等功能
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models import db
from models.user import User, HistoryRecord
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def admin_required(func):
    """管理员权限装饰器"""
    def wrapper(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({
                'status': 'error',
                'code': 401,
                'message': '未授权'
            }), 401
        
        user = User.query.get(int(user_id))
        if not user or user.role != 'admin':
            return jsonify({
                'status': 'error',
                'code': 403,
                'message': '需要管理员权限'
            }), 403
        
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_statistics():
    """
    获取系统使用统计信息
    """
    try:
        # 用户统计
        total_users = User.query.count()
        active_users = User.query.filter_by(status='active').count()
        admin_users = User.query.filter_by(role='admin').count()
        
        # 今日统计
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_uploads = HistoryRecord.query.filter(
            HistoryRecord.upload_time >= today_start
        ).count()
        today_characters = db.session.query(func.sum(HistoryRecord.character_count)).filter(
            HistoryRecord.upload_time >= today_start
        ).scalar() or 0
        
        # 本周统计
        week_start = datetime.now() - timedelta(days=7)
        week_uploads = HistoryRecord.query.filter(
            HistoryRecord.upload_time >= week_start
        ).count()
        week_characters = db.session.query(func.sum(HistoryRecord.character_count)).filter(
            HistoryRecord.upload_time >= week_start
        ).scalar() or 0
        
        # 总体统计
        total_uploads = HistoryRecord.query.count()
        total_characters = db.session.query(func.sum(HistoryRecord.character_count)).scalar() or 0
        total_processing_time = db.session.query(func.sum(HistoryRecord.processing_time)).scalar() or 0
        
        # 用户活跃度（按上传次数排序）
        user_activity = db.session.query(
            User.id,
            User.username,
            User.total_uploads,
            User.total_characters
        ).order_by(User.total_uploads.desc()).limit(10).all()
        
        activity_list = [{
            'user_id': u.id,
            'username': u.username,
            'uploads': u.total_uploads,
            'characters': u.total_characters
        } for u in user_activity]
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'data': {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'admins': admin_users
                },
                'today': {
                    'uploads': today_uploads,
                    'characters': today_characters
                },
                'week': {
                    'uploads': week_uploads,
                    'characters': week_characters
                },
                'total': {
                    'uploads': total_uploads,
                    'characters': total_characters,
                    'processing_time': round(total_processing_time, 2)
                },
                'top_users': activity_list
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """
    获取所有用户列表（分页）
    """
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        status = request.args.get('status', None)
        role = request.args.get('role', None)
        
        query = User.query
        
        if status:
            query = query.filter_by(status=status)
        
        if role:
            query = query.filter_by(role=role)
        
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=page_size, error_out=False
        )
        
        users = [user.to_dict() for user in pagination.items]
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'data': {
                'users': users,
                'total': pagination.total,
                'page': page,
                'page_size': page_size,
                'total_pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'获取用户列表失败: {str(e)}'
        }), 500


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """
    更新用户状态（启用/禁用）
    请求体: status
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '请求数据不能为空'
            }), 400
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        new_status = data.get('status')
        if new_status:
            if new_status not in ['active', 'inactive']:
                return jsonify({
                    'status': 'error',
                    'code': 400,
                    'message': '状态只能为: active 或 inactive'
                }), 400
            user.status = new_status
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '用户状态更新成功',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'更新用户状态失败: {str(e)}'
        }), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    删除用户（级联删除历史记录）
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '用户不存在'
            }), 404
        
        # 不能删除自己
        current_user_id = request.headers.get('X-User-ID')
        if int(current_user_id) == user_id:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '不能删除自己'
            }), 400
        
        # 删除用户（级联删除历史记录）
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '用户删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'删除用户失败: {str(e)}'
        }), 500


@admin_bp.route('/records', methods=['GET'])
@admin_required
def get_all_records():
    """
    获取所有历史记录（分页）
    """
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        status = request.args.get('status', None)
        
        query = HistoryRecord.query
        
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.order_by(HistoryRecord.upload_time.desc()).paginate(
            page=page, per_page=page_size, error_out=False
        )
        
        records = []
        for record in pagination.items:
            record_dict = record.to_dict()
            record_dict['username'] = record.user.username if record.user else '未知'
            records.append(record_dict)
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'data': {
                'records': records,
                'total': pagination.total,
                'page': page,
                'page_size': page_size,
                'total_pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'获取历史记录失败: {str(e)}'
        }), 500


@admin_bp.route('/records/<int:record_id>', methods=['DELETE'])
@admin_required
def delete_record(record_id):
    """
    删除历史记录
    """
    try:
        record = HistoryRecord.query.get(record_id)
        
        if not record:
            return jsonify({
                'status': 'error',
                'code': 404,
                'message': '记录不存在'
            }), 404
        
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '记录删除成功'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'删除记录失败: {str(e)}'
        }), 500


@admin_bp.route('/logs', methods=['GET'])
@admin_required
def get_system_logs():
    """
    获取系统日志
    """
    try:
        log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'app.log')
        
        if not os.path.exists(log_file):
            return jsonify({
                'status': 'success',
                'code': 200,
                'data': {
                    'logs': [],
                    'message': '日志文件不存在'
                }
            }), 200
        
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-100:]  # 最后100行
        
        logs = [line.strip() for line in lines if line.strip()]
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'data': {
                'total_lines': len(logs),
                'logs': logs
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'获取日志失败: {str(e)}'
        }), 500
