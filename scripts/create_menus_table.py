"""创建menus表"""
import sys
sys.path.insert(0, '.')

from admin_service.app.database import engine, Base
from admin_service.app.menus.models import Menu
from utils.logger import setup_logger

logger = setup_logger("create_menus_table", "scripts")

def create_menus_table():
    """创建menus表"""
    try:
        # 创建表
        Base.metadata.create_all(bind=engine, tables=[Menu.__table__])
        print("✅ menus表创建成功！")
        logger.info("menus表创建成功")
    except Exception as e:
        print(f"❌ 创建失败: {str(e)}")
        logger.error(f"创建失败: {str(e)}")

if __name__ == "__main__":
    create_menus_table()
