"""后台管理服务数据库模块"""

import os
from sqlalchemy import create_engine, inspect, text, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.logger import setup_logger
from utils.config import SQLALCHEMY_DATABASE_URL, DB_CONFIG

# 设置日志记录器
logger = setup_logger("admin_database", "admin_database")

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=DB_CONFIG["pool_size"],
    max_overflow=DB_CONFIG["max_overflow"],
    pool_timeout=DB_CONFIG["pool_timeout"],
    pool_recycle=DB_CONFIG["pool_recycle"],
    echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

def check_table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def get_table_columns(table_name: str) -> dict:
    """获取表的所有字段信息"""
    inspector = inspect(engine)
    return {col['name']: col for col in inspector.get_columns(table_name)}

def get_missing_columns(table_name: str, model_class) -> list:
    """获取缺失的字段列表"""
    # 获取当前表的字段
    existing_columns = get_table_columns(table_name)
    
    # 获取模型定义的字段
    model_columns = {}
    for column in model_class.__table__.columns:
        model_columns[column.name] = column
    
    # 找出缺失的字段
    missing_columns = []
    for col_name, column in model_columns.items():
        if col_name not in existing_columns:
            missing_columns.append(column)
    
    return missing_columns

def add_column(table_name: str, column):
    """添加单个字段"""
    try:
        # 构建 ALTER TABLE 语句
        column_type = column.type.compile(engine.dialect)
        nullable = "" if column.nullable else " NOT NULL"
        default = f" DEFAULT {column.default.arg}" if column.default is not None and column.default.arg is not None else ""
        
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {column_type}{nullable}{default}"
        
        # 执行 SQL
        with engine.connect() as conn:
            conn.execute(text(sql))
            
        logger.info(f"表 {table_name} 添加字段 {column.name} 成功")
    except Exception as e:
        logger.error(f"表 {table_name} 添加字段 {column.name} 失败: {str(e)}")
        raise

def create_table(table_name: str, table_class):
    """创建单个表"""
    try:
        if isinstance(table_class, Table):
            table_class.create(engine)
        else:
            table_class.__table__.create(engine)
        logger.info(f"表 {table_name} 创建成功")
    except Exception as e:
        logger.error(f"表 {table_name} 创建失败: {str(e)}")
        raise

def init_db():
    """初始化数据库"""
    try:
        # 导入模型以确保它们被注册到Base.metadata
        from . import models
        
        # 定义需要检查的表和它们的字段
        tables_to_check = {
            "users": {
                "class": models.User,
                "columns": ["id", "username", "email", "hashed_password", "full_name", "is_active", "is_superuser", "last_login", "created_at", "updated_at"]
            },
            "roles": {
                "class": models.Role,
                "columns": ["id", "name", "description", "created_at", "updated_at"]
            },
            "permissions": {
                "class": models.Permission,
                "columns": ["id", "name", "code", "description", "role_id", "created_at", "updated_at"]
            },
            "user_roles": {
                "class": models.user_roles,
                "columns": ["user_id", "role_id"]
            }
        }
        
        # 检查并创建/更新表
        for table_name, table_info in tables_to_check.items():
            if not check_table_exists(table_name):
                logger.info(f"表 {table_name} 不存在，开始创建...")
                create_table(table_name, table_info["class"])
            else:
                # 检查是否有缺失的字段
                if isinstance(table_info["class"], Table):
                    # 对于关联表，我们跳过字段检查
                    continue
                    
                missing_columns = get_missing_columns(table_name, table_info["class"])
                if missing_columns:
                    logger.info(f"表 {table_name} 存在 {len(missing_columns)} 个缺失字段，开始添加...")
                    for column in missing_columns:
                        add_column(table_name, column)
                else:
                    logger.info(f"表 {table_name} 已存在且字段完整")
        
        logger.info("数据库表检查完成")
    except Exception as e:
        logger.error(f"数据库表检查失败: {str(e)}")
        raise

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 