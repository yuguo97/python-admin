import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from pythonjsonlogger import jsonlogger

# 创建日志目录
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logger(name: str, log_file: str) -> logging.Logger:
    """设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件名（不含扩展名）
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 日志格式
    log_format = {
        "time": "%(asctime)s",
        "name": "%(name)s",
        "level": "%(levelname)s",
        "message": "%(message)s",
    }
    
    # JSON格式处理器
    json_formatter = jsonlogger.JsonFormatter(
        json_ensure_ascii=False,
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    today = datetime.now().strftime("%Y-%m-%d")
    file_handler = RotatingFileHandler(
        f"logs/{log_file}_{today}.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)
    
    return logger 