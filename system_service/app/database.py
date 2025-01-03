import redis
from typing import Optional
from utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger("system_database", "system_db")

# Redis客户端配置
redis_client = None

def get_redis() -> redis.Redis:
    """获取Redis客户端实例"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(
                host='localhost',  # Redis服务器地址
                port=6379,        # Redis端口
                db=0,            # 使用的数据库编号
                decode_responses=True  # 自动解码响应
            )
            logger.info("Redis连接已建立")
        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
            raise
    return redis_client 