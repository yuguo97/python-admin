"""统一配置管理模块"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any
from utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger("config", "config")

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 加载主目录下的.env文件
env_path = BASE_DIR / '.env'
if not env_path.exists():
    logger.error("未找到 .env 文件，请确保配置文件存在")
    raise FileNotFoundError("未找到 .env 文件")

load_dotenv(env_path)

def get_env_value(key: str, default: Any = None, required: bool = False) -> Any:
    """获取环境变量值，支持类型转换和必填验证
    
    Args:
        key: 环境变量名
        default: 默认值
        required: 是否必填
    
    Returns:
        环境变量值
    
    Raises:
        ValueError: 当必填项未设置时
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"环境变量 {key} 未设置")
    return value

# 数据库配置
DB_CONFIG = {
    "host": get_env_value("DB_HOST", "localhost"),
    "port": int(get_env_value("DB_PORT", "3306")),
    "user": get_env_value("DB_USER", "root"),
    "password": get_env_value("DB_PASSWORD", "123456"),
    "database": get_env_value("DB_NAME", "admin_service"),
    "pool_size": int(get_env_value("DB_POOL_SIZE", "5")),
    "max_overflow": int(get_env_value("DB_MAX_OVERFLOW", "10")),
    "pool_timeout": int(get_env_value("DB_POOL_TIMEOUT", "30")),
    "pool_recycle": int(get_env_value("DB_POOL_RECYCLE", "1800")),
}

# MongoDB配置
MONGODB_CONFIG = {
    "host": get_env_value("MONGODB_HOST", "localhost"),
    "port": int(get_env_value("MONGODB_PORT", "27017")),
    "username": get_env_value("MONGODB_USER", ""),
    "password": get_env_value("MONGODB_PASSWORD", ""),
    "database": get_env_value("MONGODB_DB", "novel_db"),
    "auth_source": get_env_value("MONGODB_AUTH_SOURCE", "admin"),
}

# Redis配置
REDIS_CONFIG = {
    "host": get_env_value("REDIS_HOST", "localhost"),
    "port": int(get_env_value("REDIS_PORT", "6379")),
    "password": get_env_value("REDIS_PASSWORD", ""),
    "db": int(get_env_value("REDIS_DB", "0")),
}

# 服务配置
SERVICE_CONFIG = {
    "admin_host": get_env_value("ADMIN_HOST", "0.0.0.0"),
    "admin_port": int(get_env_value("ADMIN_PORT", "8000")),
    "crawler_host": get_env_value("CRAWLER_HOST", "0.0.0.0"),
    "crawler_port": int(get_env_value("CRAWLER_PORT", "8001")),
    "system_host": get_env_value("SYSTEM_HOST", "0.0.0.0"),
    "system_port": int(get_env_value("SYSTEM_PORT", "8002")),
    "ai_host": get_env_value("AI_HOST", "0.0.0.0"),
    "ai_port": int(get_env_value("AI_PORT", "8003")),
    "gateway_host": get_env_value("GATEWAY_HOST", "0.0.0.0"),
    "gateway_port": int(get_env_value("GATEWAY_PORT", "8999")),
    "enable_tracing": get_env_value("ENABLE_TRACING", "false").lower() == "true",
}

# 构建数据库URL
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# 构建MongoDB URL
MONGODB_URL = (
    f"mongodb://{MONGODB_CONFIG['username']}:{MONGODB_CONFIG['password']}"
    f"@{MONGODB_CONFIG['host']}:{MONGODB_CONFIG['port']}/{MONGODB_CONFIG['database']}"
    f"?authSource={MONGODB_CONFIG['auth_source']}"
) if MONGODB_CONFIG['username'] and MONGODB_CONFIG['password'] else (
    f"mongodb://{MONGODB_CONFIG['host']}:{MONGODB_CONFIG['port']}/{MONGODB_CONFIG['database']}"
)

def validate_config() -> None:
    """验证配置是否有效"""
    try:
        # 验证数据库配置
        if not all([DB_CONFIG["host"], DB_CONFIG["user"], DB_CONFIG["password"], DB_CONFIG["database"]]):
            raise ValueError("数据库配置不完整")
            
        # 验证MongoDB配置
        if not all([MONGODB_CONFIG["host"], MONGODB_CONFIG["database"]]):
            raise ValueError("MongoDB配置不完整")
            
        # 验证Redis配置
        if not all([REDIS_CONFIG["host"]]):
            raise ValueError("Redis配置不完整")
            
        # 验证服务配置
        if not all([SERVICE_CONFIG["admin_host"], SERVICE_CONFIG["admin_port"]]):
            raise ValueError("服务配置不完整")
            
        logger.info("配置验证通过")
    except Exception as e:
        logger.error(f"配置验证失败: {str(e)}")
        raise

# 验证配置
validate_config() 