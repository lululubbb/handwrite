"""
数据库模型初始化
"""

from models.user import User, HistoryRecord
from models.db import db

__all__ = ['User', 'HistoryRecord', 'db']
