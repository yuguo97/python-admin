from flask import Blueprint, request, current_app
from flask_jwt_extended import create_access_token
from models.user import User
from utils import APIResponse
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        # 添加请求数据日志
        current_app.logger.info("Received login request")
        data = request.get_json()
        current_app.logger.debug(f"Login data: {data}")
        
        username = data.get('username')
        password = data.get('password')
        
        # 参数验证
        if not username or not password:
            current_app.logger.warning("Missing username or password")
            return APIResponse.error('用户名和密码不能为空', code=400)
        
        # 查询用户
        current_app.logger.info(f"Querying user: {username}")
        user = User.query.filter_by(username=username).first()
        
        # 用户不存在
        if not user:
            current_app.logger.warning(f"User not found: {username}")
            return APIResponse.error('用户名或密码错误', code=401)
        
        # 检查用户状态
        if user.status != 1:
            current_app.logger.warning(f"User {username} is disabled")
            return APIResponse.error('账号已被禁用', code=403)
        
        # 验证密码
        current_app.logger.debug(f"Verifying password for user: {username}")
        if not user.check_password(password):
            current_app.logger.warning(f"Invalid password for user: {username}")
            return APIResponse.error('用户名或密码错误', code=401)
        
        # 生成token
        try:
            access_token = create_access_token(
                identity=str(user.id),
                expires_delta=timedelta(days=7)
            )
            current_app.logger.info(f"Created access token for user: {username}")
            
            # 构造响应数据
            response_data = {
                'token': access_token,
                'user': user.to_dict()
            }
            
            current_app.logger.info(f"User {username} logged in successfully")
            return APIResponse.success(data=response_data, message='登录成功')
            
        except Exception as e:
            current_app.logger.error(f"Token creation error: {str(e)}")
            return APIResponse.error('Token生成失败', code=500)
            
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return APIResponse.error('登录失败', code=500)

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """刷新token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return APIResponse.error('用户不存在'), 401
        
        # 创建新的访问令牌
        new_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=7)
        )
        
        return APIResponse.success({
            'token': new_token
        })
        
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return APIResponse.error('刷新token失败'), 500