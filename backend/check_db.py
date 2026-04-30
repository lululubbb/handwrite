from app import app, db

with app.app_context():
    from models.user import User, HistoryRecord
    print('User table exists:', db.engine.has_table('users'))
    print('HistoryRecord table exists:', db.engine.has_table('history_records'))