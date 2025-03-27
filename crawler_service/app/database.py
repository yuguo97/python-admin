"""爬虫服务数据库模块"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient, ASCENDING, IndexModel
from pymongo.errors import OperationFailure
from utils.logger import setup_logger
from utils.config import MONGODB_URL, MONGODB_CONFIG

# 设置日志记录器
logger = setup_logger("crawler_database", "crawler_database")

# 全局变量
async_client = None
sync_client = None
async_db = None
sync_db = None
novels = None
chapters = None
sync_novels = None
sync_chapters = None

async def init_db():
    """初始化数据库连接"""
    global async_client, sync_client, async_db, sync_db, novels, chapters, sync_novels, sync_chapters
    
    try:
        # 异步MongoDB客户端
        async_client = AsyncIOMotorClient(
            MONGODB_URL,
            maxPoolSize=50,
            waitQueueTimeoutMS=1000,
            connectTimeoutMS=2000,
        )
        async_db = async_client[MONGODB_CONFIG["database"]]
        logger.info("MongoDB异步连接已创建")

        # 同步MongoDB客户端（用于初始化）
        sync_client = MongoClient(MONGODB_URL)
        sync_db = sync_client[MONGODB_CONFIG["database"]]
        logger.info("MongoDB同步连接已创建")

        # 获取集合
        novels = async_db.novels
        chapters = async_db.chapters
        sync_novels = sync_db.novels
        sync_chapters = sync_db.chapters
        
        return True
    except Exception as e:
        logger.error(f"MongoDB连接失败: {str(e)}")
        raise

def create_indexes(collection, indexes):
    """创建索引"""
    try:
        collection.create_indexes(indexes)
    except OperationFailure as e:
        logger.error(f"创建索引失败: {str(e)}")
        raise

async def init_indexes():
    """初始化索引"""
    try:
        # 确保数据库已连接
        if not async_db or not sync_db:
            await init_db()
            
        # 小说索引
        novel_indexes = [
            IndexModel([("novel_id", ASCENDING)], unique=True),
            IndexModel([("title", ASCENDING)]),
            IndexModel([("author", ASCENDING)]),
            IndexModel([("category", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)]),
            IndexModel([("updated_at", ASCENDING)]),
        ]
        
        # 章节索引
        chapter_indexes = [
            IndexModel([("novel_id", ASCENDING), ("chapter_id", ASCENDING)], unique=True),
            IndexModel([("novel_id", ASCENDING), ("title", ASCENDING)]),
            IndexModel([("novel_id", ASCENDING), ("created_at", ASCENDING)]),
            IndexModel([("novel_id", ASCENDING), ("updated_at", ASCENDING)]),
        ]
        
        # 创建索引
        create_indexes(sync_novels, novel_indexes)
        create_indexes(sync_chapters, chapter_indexes)
        
        logger.info("MongoDB索引创建成功")
    except Exception as e:
        logger.error(f"MongoDB索引创建失败: {str(e)}")
        raise

async def close_db():
    """关闭MongoDB连接"""
    global async_client, sync_client, async_db, sync_db, novels, chapters, sync_novels, sync_chapters
    
    try:
        if async_client:
            async_client.close()
        if sync_client:
            sync_client.close()
            
        # 重置全局变量
        async_client = None
        sync_client = None
        async_db = None
        sync_db = None
        novels = None
        chapters = None
        sync_novels = None
        sync_chapters = None
        
        logger.info("MongoDB连接已关闭")
    except Exception as e:
        logger.error(f"关闭MongoDB连接失败: {str(e)}")
        raise 