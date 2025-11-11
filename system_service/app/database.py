"""系统监控服务数据库模块"""

from motor.motor_asyncio import AsyncIOMotorClient
import redis
from typing import Optional
from utils.logger import setup_logger
from utils.config import MONGODB_URL, MONGODB_CONFIG, REDIS_CONFIG

# 设置日志记录器
logger = setup_logger("system_database", "system_database")

# 创建MongoDB客户端
client = AsyncIOMotorClient(MONGODB_URL)

# 获取数据库
db = client[MONGODB_CONFIG["database"]]

# 获取集合
metrics = db.metrics
alerts = db.alerts
devices = db.devices  # 设备信息集合

# Redis客户端配置
redis_client = None

def get_redis() -> redis.Redis:
    """获取Redis客户端实例"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis(
                host=REDIS_CONFIG["host"],
                port=REDIS_CONFIG["port"],
                password=REDIS_CONFIG["password"],
                db=REDIS_CONFIG["db"],
                decode_responses=True  # 自动解码响应
            )
            logger.info("Redis连接已建立")
        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
            raise
    return redis_client

def close_redis():
    """关闭Redis连接"""
    global redis_client
    if redis_client:
        redis_client.close()
        redis_client = None
        logger.info("Redis连接已关闭")

async def init_db():
    """初始化数据库"""
    try:
        # 创建索引
        await metrics.create_index([("timestamp", -1)])
        await alerts.create_index([("timestamp", -1)])
        await devices.create_index([("device_id", 1)], unique=True)
        await devices.create_index([("last_seen", -1)])
        await devices.create_index([("hostname", 1)])
        logger.info("MongoDB索引创建成功")
    except Exception as e:
        logger.error(f"MongoDB索引创建失败: {str(e)}")
        raise 