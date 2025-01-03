from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient, ASCENDING, IndexModel
from pymongo.errors import OperationFailure
from utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger("crawler_database", "crawler_db")

MONGO_URL = "mongodb://localhost:27017"
DATABASE_NAME = "crawler_service"

try:
    # 异步MongoDB客户端
    async_client = AsyncIOMotorClient(
        MONGO_URL,
        maxPoolSize=50,
        waitQueueTimeoutMS=1000,
        connectTimeoutMS=2000,
    )
    async_db = async_client[DATABASE_NAME]
    logger.info("MongoDB异步连接已创建")

    # 同步MongoDB客户端（用于初始化）
    sync_client = MongoClient(MONGO_URL)
    sync_db = sync_client[DATABASE_NAME]
    logger.info("MongoDB同步连接已创建")
except Exception as e:
    logger.error(f"MongoDB连接失败: {str(e)}")
    raise

def drop_all_indexes(collection):
    """删除集合的所有索引（保留_id索引）"""
    try:
        collection.drop_indexes()
        logger.info(f"已删除集合 {collection.name} 的所有索引")
    except Exception as e:
        logger.error(f"删除索引失败: {str(e)}")
        raise

def create_indexes(collection, indexes):
    """创建多个索引
    
    Args:
        collection: MongoDB集合
        indexes: 索引配置列表，每个配置包含 fields 和 options
    """
    try:
        # 先删除所有现有索引
        drop_all_indexes(collection)
        
        # 创建新索引
        for index_config in indexes:
            collection.create_index(
                index_config['fields'],
                **index_config.get('options', {})
            )
            logger.info(f"创建索引成功: {collection.name} - {index_config['options'].get('name', 'unnamed')}")
    except Exception as e:
        logger.error(f"创建索引失败: {str(e)}")
        raise

def init_indexes():
    """初始化MongoDB索引"""
    try:
        logger.info("开始创建MongoDB索引")
        
        # 小说集合索引配置
        novel_indexes = [
            {
                'fields': [("title", ASCENDING)],
                'options': {
                    'unique': True,
                    'name': 'idx_novels_title'
                }
            },
            {
                'fields': [("source_url", ASCENDING)],
                'options': {
                    'unique': True,
                    'name': 'idx_novels_source_url'
                }
            },
            {
                'fields': [("status", ASCENDING)],
                'options': {
                    'name': 'idx_novels_status'
                }
            },
            {
                'fields': [("created_at", ASCENDING)],
                'options': {
                    'name': 'idx_novels_created_at'
                }
            }
        ]
        
        # 章节集合索引配置
        chapter_indexes = [
            {
                'fields': [
                    ("novel_id", ASCENDING),
                    ("chapter_number", ASCENDING)
                ],
                'options': {
                    'unique': True,
                    'name': 'idx_chapters_novel_chapter'
                }
            },
            {
                'fields': [("source_url", ASCENDING)],
                'options': {
                    'unique': True,
                    'name': 'idx_chapters_source_url'
                }
            }
        ]
        
        # 创建索引
        create_indexes(sync_db.novels, novel_indexes)
        create_indexes(sync_db.chapters, chapter_indexes)
        
        logger.info("MongoDB索引创建成功")
    except Exception as e:
        logger.error(f"创建MongoDB索引失败: {str(e)}")
        raise

async def close_mongo_connection():
    """关闭MongoDB连接"""
    logger.info("关闭MongoDB连接")
    async_client.close()
    sync_client.close() 