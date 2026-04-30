"""
用户路由模块
包含用户注册、登录、信息修改、历史记录查询、文本编辑保存等功能
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db
from models.user import User, HistoryRecord
from werkzeug.security import generate_password_hash, check_password_hash
import re
import logging

logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__, url_prefix='/api/user')


def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """验证密码强度"""
    if len(password) < 6:
        return False, '密码长度至少为6位'
    if not re.search(r'[a-zA-Z]', password):
        return False, '密码必须包含字母'
    if not re.search(r'[0-9]', password):
        return False, '密码必须包含数字'
    return True, ''


@user_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    try:
        logger.info('接收到用户注册请求')
        data = request.get_json()

        if not data:
            return jsonify({'status': 'error', 'code': 400, 'message': '请求数据不能为空'}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not username or not email or not password:
            return jsonify({'status': 'error', 'code': 400, 'message': '用户名、邮箱和密码不能为空'}), 400

        if not validate_email(email):
            return jsonify({'status': 'error', 'code': 400, 'message': '邮箱格式不正确'}), 400

        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'status': 'error', 'code': 400, 'message': error_msg}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'status': 'error', 'code': 400, 'message': '用户名已存在'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'status': 'error', 'code': 400, 'message': '邮箱已被注册'}), 400

        user = User(username=username, email=email, role='user', status='active')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        logger.info(f'用户注册成功: id={user.id}, username={user.username}')
        return jsonify({
            'status': 'success', 'code': 200, 'message': '注册成功',
            'data': {'id': user.id, 'username': user.username, 'email': user.email, 'role': user.role}
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f'注册失败: {e}')
        return jsonify({'status': 'error', 'code': 500, 'message': f'注册失败: {str(e)}'}), 500


@user_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'status': 'error', 'code': 400, 'message': '请求数据不能为空'}), 400

        identifier = (data.get('username', '') or data.get('email', '')).strip()
        password = data.get('password', '')

        if not identifier or not password:
            return jsonify({'status': 'error', 'code': 400, 'message': '用户名/邮箱和密码不能为空'}), 400

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

        if not user:
            return jsonify({'status': 'error', 'code': 401, 'message': '用户不存在'}), 401

        if user.status != 'active':
            return jsonify({'status': 'error', 'code': 403, 'message': '账户已被禁用'}), 403

        if not user.check_password(password):
            return jsonify({'status': 'error', 'code': 401, 'message': '密码错误'}), 401

        user.last_login = datetime.now()
        db.session.commit()

        return jsonify({
            'status': 'success', 'code': 200, 'message': '登录成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'avatar': user.avatar,
                'role': user.role,
                'status': user.status,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
                'total_uploads': user.total_uploads,
                'total_characters': user.total_characters,
                'token': f'token_{user.id}_{datetime.now().timestamp()}'
            }
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'code': 500, 'message': f'登录失败: {str(e)}'}), 500


@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """获取用户信息"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'status': 'error', 'code': 401, 'message': '未授权'}), 401

        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'status': 'error', 'code': 404, 'message': '用户不存在'}), 404

        return jsonify({'status': 'success', 'code': 200, 'data': user.to_dict()}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'code': 500, 'message': f'获取用户信息失败: {str(e)}'}), 500


@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    """更新用户信息"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'status': 'error', 'code': 401, 'message': '未授权'}), 401

        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'status': 'error', 'code': 404, 'message': '用户不存在'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'code': 400, 'message': '请求数据不能为空'}), 400

        if 'email' in data:
            email = data['email'].strip()
            if not validate_email(email):
                return jsonify({'status': 'error', 'code': 400, 'message': '邮箱格式不正确'}), 400
            existing = User.query.filter((User.email == email) & (User.id != user.id)).first()
            if existing:
                return jsonify({'status': 'error', 'code': 400, 'message': '邮箱已被使用'}), 400
            user.email = email

        if 'avatar' in data:
            user.avatar = data['avatar'].strip()

        db.session.commit()
        return jsonify({'status': 'success', 'code': 200, 'message': '信息更新成功', 'data': user.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'code': 500, 'message': f'更新失败: {str(e)}'}), 500


@user_bp.route('/change-password', methods=['PUT'])
def change_password():
    """修改密码"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'status': 'error', 'code': 401, 'message': '未授权'}), 401

        user = User.query.get(int(user_id))
        if not user:
            return jsonify({'status': 'error', 'code': 404, 'message': '用户不存在'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'code': 400, 'message': '请求数据不能为空'}), 400

        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')

        if not old_password or not new_password:
            return jsonify({'status': 'error', 'code': 400, 'message': '原密码和新密码不能为空'}), 400

        if not user.check_password(old_password):
            return jsonify({'status': 'error', 'code': 401, 'message': '原密码错误'}), 401

        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'status': 'error', 'code': 400, 'message': error_msg}), 400

        user.set_password(new_password)
        db.session.commit()
        return jsonify({'status': 'success', 'code': 200, 'message': '密码修改成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'code': 500, 'message': f'修改密码失败: {str(e)}'}), 500


@user_bp.route('/history', methods=['GET'])
def get_history():
    """获取用户历史记录（分页）"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'status': 'error', 'code': 401, 'message': '未授权'}), 401

        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)

        pagination = HistoryRecord.query.filter_by(user_id=user_id).order_by(
            HistoryRecord.upload_time.desc()
        ).paginate(page=page, per_page=page_size, error_out=False)

        records = [r.to_dict() for r in pagination.items]

        return jsonify({
            'status': 'success', 'code': 200,
            'data': {
                'records': records,
                'total': pagination.total,
                'page': page,
                'page_size': page_size,
                'total_pages': pagination.pages
            }
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'code': 500, 'message': f'获取历史记录失败: {str(e)}'}), 500


@user_bp.route('/history/<int:record_id>', methods=['GET'])
def get_record_detail(record_id):
    """获取单条历史记录详情"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'status': 'error', 'code': 401, 'message': '未授权'}), 401

        record = HistoryRecord.query.filter_by(id=record_id, user_id=user_id).first()
        if not record:
            return jsonify({'status': 'error', 'code': 404, 'message': '记录不存在'}), 404

        return jsonify({'status': 'success', 'code': 200, 'data': record.to_dict()}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'code': 500, 'message': f'获取记录详情失败: {str(e)}'}), 500


@user_bp.route('/history/<int:record_id>/update-text', methods=['PUT'])
def update_record_text(record_id):
    """
    更新历史记录的排版文本（支持前端手动编辑后保存）
    请求体: formatted_text
    """
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'status': 'error', 'code': 401, 'message': '未授权'}), 401

        record = HistoryRecord.query.filter_by(id=record_id, user_id=user_id).first()
        if not record:
            return jsonify({'status': 'error', 'code': 404, 'message': '记录不存在'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'code': 400, 'message': '请求数据不能为空'}), 400

        formatted_text = data.get('formatted_text', '')
        record.formatted_text = formatted_text
        # 更新字符数
        record.character_count = len(formatted_text)
        db.session.commit()

        logger.info(f'记录 {record_id} 文本已更新，字符数: {record.character_count}')
        return jsonify({
            'status': 'success', 'code': 200, 'message': '文本更新成功',
            'data': {'record_id': record_id, 'character_count': record.character_count}
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'code': 500, 'message': f'更新文本失败: {str(e)}'}), 500


@user_bp.route('/history/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """删除历史记录"""
    try:
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'status': 'error', 'code': 401, 'message': '未授权'}), 401

        record = HistoryRecord.query.filter_by(id=record_id, user_id=user_id).first()
        if not record:
            return jsonify({'status': 'error', 'code': 404, 'message': '记录不存在'}), 404

        db.session.delete(record)
        db.session.commit()
        return jsonify({'status': 'success', 'code': 200, 'message': '删除成功'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'code': 500, 'message': f'删除失败: {str(e)}'}), 500