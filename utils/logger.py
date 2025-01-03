import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(app):
    """配置日志"""
    # 确保日志目录存在
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志文件名（按日期）
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    
    # 设置日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # 文件处理器 - 详细日志
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器 - 简单日志
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # 移除默认处理器
    app.logger.handlers = []
    
    # 添加自定义处理器
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    # 设置日志级别
    app.logger.setLevel(logging.INFO)
    
    # 设置 Werkzeug 日志
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.handlers = []
    werkzeug_logger.addHandler(file_handler)
    werkzeug_logger.addHandler(console_handler)
    
    # 记录启动日志
    app.logger.info('Logger initialized')

def log_info(message):
    """记录信息日志"""
    logging.getLogger('flask.app').info(message)

def log_error(message):
    """记录错误日志"""
    logging.getLogger('flask.app').error(message)

def log_warning(message):
    """记录警告日志"""
    logging.getLogger('flask.app').warning(message)

def log_debug(message):
    """记录调试日志"""
    logging.getLogger('flask.app').debug(message) 