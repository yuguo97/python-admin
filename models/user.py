from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    status = db.Column(db.Integer, default=1)  # 1: 正常, 0: 禁用
    remark = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs:
            self.set_password(kwargs['password'])

    def set_password(self, password):
        """设置密码"""
        try:
            if not password:
                raise ValueError('密码不能为空')
            self.password_hash = generate_password_hash(password)
        except Exception as e:
            logging.error(f"Set password error: {str(e)}")
            raise e

    def check_password(self, password):
        """验证密码"""
        try:
            if not password:
                return False
            if not self.password_hash:
                logging.error(f"No password hash found for user: {self.username}")
                return False
            return check_password_hash(self.password_hash, password)
        except Exception as e:
            logging.error(f"Check password error for user {self.username}: {str(e)}")
            return False
    
    def save(self):
        """保存用户"""
        try:
            if not self.username:
                raise ValueError('用户名不能为空')
            
            if not self.password_hash:
                raise ValueError('密码不能为空')
            
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'status': self.status,
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }