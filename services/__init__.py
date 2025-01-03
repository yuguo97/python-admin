from utils.logger import setup_logger

# 服务配置
SERVICES = {
    "admin": {
        "name": "后台管理服务",
        "module": "admin_service.app.main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "logger": setup_logger("admin_service", "admin")
    },
    "crawler": {
        "name": "爬虫服务",
        "module": "crawler_service.app.main:app",
        "host": "0.0.0.0",
        "port": 8001,
        "logger": setup_logger("crawler_service", "crawler")
    },
    "system": {
        "name": "系统监控服务",
        "module": "system_service.app.main:app",
        "host": "0.0.0.0",
        "port": 8002,
        "logger": setup_logger("system_service", "system")
    }
} 