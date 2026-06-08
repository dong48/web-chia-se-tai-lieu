from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    
    # MỚI THÊM: Cột phân quyền (mặc định ai đăng ký cũng là 'user' thường)
    role = db.Column(db.String(50), default='user') 
    
    documents = db.relationship('Document', backref='author', lazy=True)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Khóa ngoại liên kết tới bảng User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)