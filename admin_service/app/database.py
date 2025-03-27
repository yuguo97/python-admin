"""后台管理服务数据库模块"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger("admin_database", "admin")

# 数据库连接URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./admin.db"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # 仅用于SQLite
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

def init_db():
    """初始化数据库"""
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库表创建失败: {str(e)}")
        raise

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        logger.debug("创建新的数据库会话")
        yield db
    finally:
        logger.debug("关闭数据库会话")
        db.close() 