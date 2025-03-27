"""数据库初始化脚本"""

import os
import sys
from pathlib import Path
import pymysql
from pymysql.cursors import DictCursor
from utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger("init_db", "init_db")

# 数据库配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
DB_NAME = os.getenv("DB_NAME", "admin_service")

def create_database():
    """创建数据库"""
    try:
        # 连接到MySQL服务器
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )
        
        with conn.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info(f"数据库 {DB_NAME} 创建成功")
            
        conn.close()
    except Exception as e:
        logger.error(f"创建数据库失败: {str(e)}")
        raise

def init_mysql():
    """初始化MySQL数据库"""
    try:
        # 创建数据库
        create_database()
        
        # 导入数据库模型以创建表
        from admin_service.app.database import init_db
        init_db()
        logger.info("MySQL数据库表检查完成")
    except Exception as e:
        logger.error(f"MySQL数据库初始化失败: {str(e)}")
        raise

def init_mongodb():
    """初始化MongoDB数据库"""
    try:
        # 创建索引
        from crawler_service.app.database import init_indexes
        init_indexes()
        logger.info("MongoDB索引创建成功")
    except Exception as e:
        logger.error(f"MongoDB初始化失败: {str(e)}")
        raise

def init_redis():
    """初始化Redis数据库"""
    try:
        # 测试Redis连接
        from system_service.app.database import get_redis
        redis_client = get_redis()
        redis_client.ping()
        logger.info("Redis连接测试成功")
    except Exception as e:
        logger.error(f"Redis连接测试失败: {str(e)}")
        raise

def init_all():
    """初始化所有数据库"""
    try:
        # 初始化MySQL
        init_mysql()
        
        # 初始化MongoDB
        init_mongodb()
        
        # 初始化Redis
        init_redis()
        
        logger.info("所有数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_all() 