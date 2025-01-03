from models.user import User, db
from utils.error_codes import ErrorCode
from datetime import datetime
from utils.jwt_utils import generate_token
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

class AuthService:
    @staticmethod
    def login(username, password):
        """用户登录"""
        try:
            # 添加调试日志
            current_app.logger.info(f"Attempting login for user: {username}")
            
            user = User.query.filter_by(username=username).first()
            if not user:
                current_app.logger.warning(f"User not found: {username}")
                return False, ErrorCode.USER_NOT_FOUND
            
            # 添加密码验证调试日志
            current_app.logger.info(f"Checking password for user: {username}")
            if not user.check_password(password):
                current_app.logger.warning(f"Invalid password for user: {username}")
                return False, ErrorCode.WRONG_PASSWORD
            
            if user.status == 0:
                current_app.logger.warning(f"Account disabled: {username}")
                return False, ErrorCode.ACCOUNT_DISABLED
            
            # 更新最后登录时间
            user.last_login = datetime.now()
            db.session.commit()
            
            # 生成token
            token = generate_token(user.id)
            
            current_app.logger.info(f"Login successful for user: {username}")
            
            return True, {
                "token": token,
                "user": user
            }
        except Exception as e:
            current_app.logger.error(f"Login error: {str(e)}")
            db.session.rollback()
            raise e 

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'code': 401,
                'message': '请先登录'
            }), 401
    return wrapper 