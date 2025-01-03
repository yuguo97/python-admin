from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger("admin_database", "admin_db")

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/admin_service"

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=5,  # 连接池大小
        max_overflow=10,  # 超过连接池大小外最多创建的连接数
        pool_timeout=30,  # 池中没有连接最多等待的时间
        pool_recycle=1800,  # 多久之后对连接池中的连接进行一次回收
    )
    logger.info("MySQL数据库连接已创建")
except Exception as e:
    logger.error(f"MySQL数据库连接失败: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        logger.debug("创建新的数据库会话")
        yield db
    finally:
        logger.debug("关闭数据库会话")
        db.close() 