"""
智能手写笔记转录系统 - 后端主应用
Flask应用入口，包含核心配置和路由注册
"""

import os
os.environ['PADDLEX_HOME'] = r'E:\paddlex_data'
os.environ['PADDLE_HOME'] = r'E:\paddle_data'
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 初始化Flask应用
app = Flask(__name__)

# 配置跨域
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 配置数据库
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "database", "ocr_system.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB文件大小限制

# 初始化数据库
from models.db import db
db.init_app(app)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'logs', 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 导入并注册蓝图
from routes.user_routes import user_bp
from routes.ocr_routes import ocr_bp
from routes.upload_routes import upload_bp
from routes.admin_routes import admin_bp

app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(ocr_bp, url_prefix='/api/ocr')
app.register_blueprint(upload_bp, url_prefix='/api/upload')
app.register_blueprint(admin_bp, url_prefix='/api/admin')


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'success',
        'message': '智能手写笔记转录系统后端服务运行中',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'status': 'error',
        'code': 404,
        'message': '接口不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f'内部错误: {str(error)}')
    return jsonify({
        'status': 'error',
        'code': 500,
        'message': '服务器内部错误'
    }), 500


@app.errorhandler(405)
def method_not_allowed(error):
    """405错误处理"""
    return jsonify({
        'status': 'error',
        'code': 405,
        'message': '方法不允许'
    }), 405


def create_tables():
    """创建数据库表"""
    with app.app_context():
        from models.user import User, HistoryRecord
        db.create_all()
        logger.info('数据库表创建成功')


if __name__ == '__main__':
    create_tables()
    app.run(debug=False, host='0.0.0.0', port=5000)
