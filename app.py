from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from models import db
from routes import register_routes
from utils.logger import setup_logger
import os

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 确保日志目录存在
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 设置日志
    setup_logger(app)
    app.logger.info('Application starting...')
    
    # 初始化扩展
    db.init_app(app)
    app.logger.info('Database initialized')
    
    # 配置 JWT
    jwt = JWTManager(app)
    app.logger.info('JWT configured')
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return str(user)
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        try:
            from models.user import User
            return User.query.filter_by(id=int(identity)).one_or_none()
        except:
            return None
    
    # 配置 CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": app.config['CORS_METHODS'],
            "allow_headers": app.config['CORS_ALLOW_HEADERS']
        }
    })
    app.logger.info('CORS configured')
    
    # 注册路由
    register_routes(app)
    app.logger.info('Routes registered')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        app.logger.info('Database tables created')
    
    app.logger.info('Application startup complete')
    return app