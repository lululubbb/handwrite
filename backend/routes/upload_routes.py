"""
文件上传和预处理路由模块
"""

import os
import uuid
import cv2
import numpy as np
from flask import Blueprint, request, jsonify, send_from_directory
import re
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db
from models.user import User, HistoryRecord

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')

# 配置上传目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# 允许的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def adjust_brightness(image, alpha=1.2, beta=20):
    """
    调整图像亮度
    alpha: 亮度增益（>1增加亮度，<1降低亮度）
    beta: 亮度偏移
    """
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


def enhance_sharpness(image):
    """
    增强图像清晰度
    使用拉普拉斯算子进行锐化
    """
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    return cv2.filter2D(image, -1, kernel)


def correct_skew(image):
    """
    图像倾斜校正
    使用形态学操作检测文本行并进行旋转校正
    """
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 二值化
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY_INV, 11, 2)
    
    # 形态学操作
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    # 霍夫线变换检测直线
    lines = cv2.HoughLinesP(morph, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
    
    if lines is not None:
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            angles.append(angle)
        
        # 计算平均角度
        avg_angle = np.median(angles)
        
        # 如果角度较大，进行旋转校正
        if avg_angle > 1:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
            corrected = cv2.warpAffine(image, rotation_matrix, (w, h), 
                                       flags=cv2.INTER_CUBIC, 
                                       borderMode=cv2.BORDER_REPLICATE)
            return corrected
    
    return image


def preprocess_image(image_path):
    """
    综合图像预处理
    """
    # 读取图像
    image = cv2.imread(image_path)
    
    if image is None:
        return None
    
    # 1. 调整亮度
    image = adjust_brightness(image, alpha=1.3, beta=30)
    
    # 2. 增强清晰度
    image = enhance_sharpness(image)
    
    # 3. 倾斜校正
    image = correct_skew(image)
    
    return image


def clean_markdown_content(md_text):
    """删除所有 HTML 标签与图片占位，用于存储/返回给前端前的清理。"""
    if not md_text:
        return md_text
    md_text = re.sub(r'<[^>]+>', '', md_text)
    md_text = md_text.replace('Image', '').replace('image', '')
    md_text = re.sub(r'\n+', '\n\n', md_text).strip()
    return md_text


@upload_bp.route('/check', methods=['GET'])
def check_upload():
    """检查上传目录"""
    return jsonify({
        'status': 'success',
        'code': 200,
        'data': {
            'upload_folder': UPLOAD_FOLDER,
            'processed_folder': PROCESSED_FOLDER,
            'allowed_extensions': list(ALLOWED_EXTENSIONS)
        }
    })


@upload_bp.route('/preprocess', methods=['POST'])
def preprocess():
    """
    图像预处理接口
    上传原始图像并进行预处理
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '未找到文件'
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '文件名不能为空'
            }), 400
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '不支持的文件格式，仅支持: ' + ', '.join(ALLOWED_EXTENSIONS)
            }), 400

        # 生成唯一文件名
        original_filename = secure_filename(file.filename)
        # 🔥 修复无后缀名报错
        file_parts = original_filename.rsplit('.', 1)
        file_ext = file_parts[1].lower() if len(file_parts) == 2 else 'jpg'

        unique_id = uuid.uuid4().hex[:8]
        # 重要：使用统一的unique_id生成所有文件名
        disk_original_filename = f'original_{unique_id}.{file_ext}'
        disk_processed_filename = f'processed_{unique_id}.{file_ext}'

        # 保存原始文件
        original_path = os.path.join(UPLOAD_FOLDER, disk_original_filename)
        file.save(original_path)

        # 图像预处理
        processed_image = preprocess_image(original_path)

        if processed_image is None:
            return jsonify({
                'status': 'error',
                'code': 500,
                'message': '图像处理失败'
            }), 500

        # 保存预处理后的图像
        processed_path = os.path.join(PROCESSED_FOLDER, disk_processed_filename)
        cv2.imwrite(processed_path, processed_image)

        # 返回预处理结果（返回真实的磁盘文件名）
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '预处理成功',
            'data': {
                'display_filename': original_filename,
                'original_filename': disk_original_filename,
                'processed_filename': disk_processed_filename,
                'original_path': original_path,
                'processed_path': processed_path,
                'preprocess_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'预处理失败: {str(e)}'
        }), 500


@upload_bp.route('/preview/<filename>', methods=['GET'])
def get_preview(filename):
    """获取图像预览"""
    try:
        # 尝试从预处理目录获取
        processed_path = os.path.join(PROCESSED_FOLDER, filename)
        if os.path.exists(processed_path):
            return send_from_directory(PROCESSED_FOLDER, filename)
        
        # 尝试从上传目录获取
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(upload_path):
            return send_from_directory(UPLOAD_FOLDER, filename)
        
        return jsonify({
            'status': 'error',
            'code': 404,
            'message': '文件不存在'
        }), 404
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'获取预览失败: {str(e)}'
        }), 500


@upload_bp.route('/save-record', methods=['POST'])
def save_record():
    """
    保存识别记录到数据库
    请求体: user_id, original_filename, processed_filename, ocr_result, 
           formatted_text, character_count, confidence, processing_time
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '请求数据不能为空'
            }), 400
        
        user_id = data.get('user_id')
        original_filename = data.get('original_filename', '')
        processed_filename = data.get('processed_filename', '')
        ocr_result = data.get('ocr_result', '{}')
        formatted_text = data.get('formatted_text', '')
        character_count = data.get('character_count', 0)
        confidence = data.get('confidence', 0.0)
        processing_time = data.get('processing_time', 0.0)
        notes = data.get('notes', '')
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'code': 400,
                'message': '用户ID不能为空'
            }), 400
        
        # 存储前清理 HTML/图片占位，避免把 <img> 等标签保存并回显
        formatted_text = clean_markdown_content(formatted_text)

        # 创建历史记录
        record = HistoryRecord(
            user_id=user_id,
            original_filename=original_filename,
            processed_filename=processed_filename,
            ocr_result=str(ocr_result),
            formatted_text=formatted_text,
            character_count=character_count,
            confidence=confidence,
            processing_time=processing_time,
            status='completed',
            notes=notes
        )
        
        db.session.add(record)
        db.session.commit()
        
        # 更新用户统计
        user = User.query.get(user_id)
        if user:
            user.total_uploads += 1
            user.total_characters += character_count
            db.session.commit()
        
        return jsonify({
            'status': 'success',
            'code': 200,
            'message': '记录保存成功',
            'data': {
                'record_id': record.id,
                'upload_time': record.upload_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': f'保存记录失败: {str(e)}'
        }), 500
