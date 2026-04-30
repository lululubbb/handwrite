"""
用户和历史记录模型
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import db


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(100), unique=True, nullable=False, comment='邮箱')
    password_hash = db.Column(db.String(200), nullable=False, comment='密码哈希')
    avatar = db.Column(db.String(200), default='default.png', comment='头像')
    role = db.Column(db.String(20), default='user', comment='角色：user/admin')
    status = db.Column(db.String(20), default='active', comment='状态：active/inactive')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    last_login = db.Column(db.DateTime, comment='最后登录时间')
    total_uploads = db.Column(db.Integer, default=0, comment='总上传次数')
    total_characters = db.Column(db.Integer, default=0, comment='总识别字符数')
    
    # 关联历史记录
    records = db.relationship('HistoryRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码（加密存储）"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'role': self.role,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None,
            'total_uploads': self.total_uploads,
            'total_characters': self.total_characters
        }


class HistoryRecord(db.Model):
    """历史记录模型"""
    __tablename__ = 'history_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    original_filename = db.Column(db.String(200), nullable=False, comment='原始文件名')
    processed_filename = db.Column(db.String(200), nullable=False, comment='处理后文件名')
    upload_time = db.Column(db.DateTime, default=datetime.now, comment='上传时间')
    ocr_result = db.Column(db.Text, comment='OCR识别结果（JSON格式）')
    formatted_text = db.Column(db.Text, comment='排版还原后的文本')
    character_count = db.Column(db.Integer, default=0, comment='识别字符数')
    confidence = db.Column(db.Float, default=0.0, comment='平均置信度')
    processing_time = db.Column(db.Float, default=0.0, comment='处理耗时（秒）')
    status = db.Column(db.String(20), default='completed', comment='状态：processing/completed/failed')
    notes = db.Column(db.Text, comment='备注')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'processed_filename': self.processed_filename,
            'upload_time': self.upload_time.strftime('%Y-%m-%d %H:%M:%S') if self.upload_time else None,
            'ocr_result': self.ocr_result,
            'formatted_text': self.formatted_text,
            'character_count': self.character_count,
            'confidence': self.confidence,
            'processing_time': self.processing_time,
            'status': self.status,
            'notes': self.notes
        }
