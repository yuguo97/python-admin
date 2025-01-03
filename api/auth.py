from flask import request
from core.auth import AuthService
from utils.response import APIResponse
from utils.error_codes import ErrorCode
import logging
from . import auth_bp

logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json(force=True)
        if not all(k in data for k in ["username", "password"]):
            return APIResponse.error(ErrorCode.MISSING_PARAMS)
        
        success, result = AuthService.login(
            username=data["username"],
            password=data["password"]
        )
        
        if success:
            return APIResponse.success(
                data={
                    "token": result["token"],
                    "user": result["user"].to_dict()
                },
                message="登录成功"
            )
        return APIResponse.error(result)
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        return APIResponse.error(ErrorCode.UNKNOWN_ERROR)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        from core.users import UserService
        success, result = UserService.create_user(request.get_json(force=True))
        if success:
            return APIResponse.success(
                data=result.to_dict(),
                message="注册成功",
                code=201
            )
        return APIResponse.error(result)
    except Exception as e:
        logger.error(f"注册失败: {str(e)}")
        return APIResponse.error(ErrorCode.UNKNOWN_ERROR)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    return APIResponse.success(message="登出成功") 