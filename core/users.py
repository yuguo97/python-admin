from models.user import User, db
from utils.error_codes import ErrorCode
from utils.validators import validate_email, validate_phone
from datetime import datetime

class UserService:
    @staticmethod
    def create_user(data):
        """创建用户"""
        try:
            # 验证必要参数
            if not all(k in data for k in ["username", "password", "email"]):
                return False, ErrorCode.MISSING_PARAMS
            
            # 验证邮箱格式
            if not validate_email(data["email"]):
                return False, ErrorCode.INVALID_EMAIL
            
            # 验证手机号格式
            if "phone" in data and not validate_phone(data["phone"]):
                return False, ErrorCode.INVALID_PHONE
            
            # 检查用户名是否已存在
            if User.query.filter_by(username=data["username"]).first():
                return False, ErrorCode.USER_ALREADY_EXISTS
            
            # 创建新用户
            new_user = User(
                username=data["username"],
                email=data["email"],
                phone=data.get("phone")
            )
            new_user.set_password(data["password"])
            
            db.session.add(new_user)
            db.session.commit()
            
            return True, new_user
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update_user(user_id, data):
        """更新用户信息"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, ErrorCode.USER_NOT_FOUND
            
            if "email" in data:
                if not validate_email(data["email"]):
                    return False, ErrorCode.INVALID_EMAIL
                user.email = data["email"]
            
            if "phone" in data:
                if not validate_phone(data["phone"]):
                    return False, ErrorCode.INVALID_PHONE
                user.phone = data["phone"]
            
            if "password" in data:
                user.set_password(data["password"])
            
            if "status" in data:
                user.status = data["status"]
            
            db.session.commit()
            return True, user
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_user(user_id):
        """删除用户"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, ErrorCode.USER_NOT_FOUND
            
            db.session.delete(user)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_users(page=1, per_page=10):
        """获取用户列表"""
        try:
            pagination = User.query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            return True, pagination
        except Exception as e:
            raise e 