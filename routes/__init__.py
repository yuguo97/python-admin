from flask import Blueprint
from .auth import auth_bp
from .menu import menu_bp
from .user import user_bp

def register_routes(app):
    """注册所有路由"""
    
    # 创建API蓝图
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    
    # 注册子蓝图
    api_bp.register_blueprint(auth_bp, url_prefix='/auth')  # /api/auth/login
    api_bp.register_blueprint(menu_bp, url_prefix='/menus')  # /api/menus
    api_bp.register_blueprint(user_bp, url_prefix='/users')  # /api/users
    
    # 注册API蓝图到应用
    app.register_blueprint(api_bp)

# 确保导出 register_routes 函数
__all__ = ['register_routes'] 