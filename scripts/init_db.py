import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from admin_service.app.database import engine as admin_engine, Base as AdminBase
from crawler_service.app.database import init_indexes as init_mongo_indexes
from system_service.app.database import get_redis
from utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger("init_db", "init_db")

def init_mysql():
    """初始化MySQL数据库"""
    try:
        # 创建所有表
        AdminBase.metadata.create_all(bind=admin_engine)
        logger.info("MySQL数据库表创建成功")
    except Exception as e:
        logger.error(f"MySQL数据库初始化失败: {str(e)}")
        raise

def init_mongodb():
    """初始化MongoDB数据库"""
    try:
        # 创建索引
        init_mongo_indexes()
        logger.info("MongoDB索引创建成功")
    except Exception as e:
        logger.error(f"MongoDB初始化失败: {str(e)}")
        raise

def init_redis():
    """初始化Redis数据库"""
    try:
        # 测试Redis连接
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