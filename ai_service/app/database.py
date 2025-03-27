"""AI服务数据库模块"""

from motor.motor_asyncio import AsyncIOMotorClient
from utils.logger import setup_logger
from utils.config import MONGODB_URL, MONGODB_CONFIG

# 设置日志记录器
logger = setup_logger("ai_database", "ai_database")

# 创建MongoDB客户端
client = AsyncIOMotorClient(MONGODB_URL)

# 获取数据库
db = client[MONGODB_CONFIG["database"]]

# 获取集合
chapters = db.chapters
summaries = db.summaries

async def init_db():
    """初始化数据库"""
    try:
        # 创建索引
        await chapters.create_index([("novel_id", 1), ("chapter_id", 1)], unique=True)
        await summaries.create_index([("novel_id", 1), ("chapter_id", 1)], unique=True)
        logger.info("MongoDB索引创建成功")
    except Exception as e:
        logger.error(f"MongoDB索引创建失败: {str(e)}")
        raise 