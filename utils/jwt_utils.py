from flask_jwt_extended import create_access_token, verify_jwt_in_request, get_jwt_identity
from datetime import timedelta
from functools import wraps
from utils.response import APIResponse
from models.user import User
from flask import current_app

def generate_token(user_id):
    """生成JWT token"""
    return create_access_token(
        identity=str(user_id),
        expires_delta=timedelta(days=1)
    ) 

def admin_required():
    """管理员权限装饰器"""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            try:
                # 获取当前用户
                user = User.query.get(int(current_user_id))
                
                # 检查用户是否存在且是管理员
                if not user or user.username != 'admin':
                    current_app.logger.warning(f"Unauthorized admin access attempt by user {current_user_id}")
                    return APIResponse.error('需要管理员权限'), 403
                
                return fn(*args, **kwargs)
                
            except Exception as e:
                current_app.logger.error(f"Admin authorization error: {str(e)}")
                return APIResponse.error('权限验证失败'), 500
                
        return decorator
    return wrapper