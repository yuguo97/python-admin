"""添加应用管理菜单"""
import sys
sys.path.insert(0, '.')

from admin_service.app.database import SessionLocal
from admin_service.app.menus.models import Menu
from utils.logger import setup_logger

logger = setup_logger("add_app_menus", "scripts")

def add_app_menus():
    """添加应用管理菜单"""
    db = SessionLocal()
    try:
        # 检查是否已存在应用管理父菜单
        app_parent = db.query(Menu).filter(Menu.path == "/app").first()
        
        if not app_parent:
            # 创建应用管理父菜单
            app_parent = Menu(
                name="应用管理",
                path="/app",
                icon="Monitor",
                parent_id=None,
                sort_order=2
            )
            db.add(app_parent)
            db.flush()
            print("✅ 创建应用管理父菜单")
            logger.info("创建应用管理父菜单")
        else:
            print("ℹ️  应用管理父菜单已存在")
        
        # 检查服务管理菜单
        services_menu = db.query(Menu).filter(Menu.path == "/app/services").first()
        if not services_menu:
            services_menu = Menu(
                name="服务管理",
                path="/app/services",
                icon="Monitor",
                parent_id=app_parent.id,
                sort_order=1
            )
            db.add(services_menu)
            print("✅ 创建服务管理菜单")
            logger.info("创建服务管理菜单")
        else:
            print("ℹ️  服务管理菜单已存在")
        
        # 检查系统信息菜单
        systeminfo_menu = db.query(Menu).filter(Menu.path == "/app/systeminfo").first()
        if not systeminfo_menu:
            systeminfo_menu = Menu(
                name="系统信息",
                path="/app/systeminfo",
                icon="DataAnalysis",
                parent_id=app_parent.id,
                sort_order=2
            )
            db.add(systeminfo_menu)
            print("✅ 创建系统信息菜单")
            logger.info("创建系统信息菜单")
        else:
            print("ℹ️  系统信息菜单已存在")
        
        db.commit()
        print("\n✅ 应用管理菜单添加完成！")
        logger.info("应用管理菜单添加完成")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 添加失败: {str(e)}")
        logger.error(f"添加失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    add_app_menus()
