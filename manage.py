import typer
import sys
from utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger("manage", "manage")

# 创建typer应用
app = typer.Typer(help="""
微服务管理工具

可用命令:
- start: 启动服务
- init-db: 初始化数据库
- create-admin: 创建管理员用户
""")

@app.command()
def start(
    service: str = typer.Option("all", help="服务名称 (admin/crawler/system/ai/all)")
):
    """启动服务"""
    try:
        from services.server import run_all, run_service
        
        if service == "all":
            run_all()
        else:
            run_service(service)
            
    except Exception as e:
        logger.error(f"启动服务失败: {str(e)}")
        sys.exit(1)

@app.command()
def init_db():
    """初始化数据库"""
    try:
        from scripts.init_db import init_all
        init_all()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        sys.exit(1)

@app.command()
def create_admin():
    """创建管理员用户"""
    try:
        from scripts.create_admin import create_admin_user
        create_admin_user()
    except Exception as e:
        logger.error(f"创建管理员用户失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    app() 