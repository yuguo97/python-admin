"""更新菜单数据,添加code和component"""
import sys
sys.path.insert(0, '.')

from admin_service.app.database import SessionLocal
from admin_service.app.menus.models import Menu
from utils.logger import setup_logger

logger = setup_logger("update_menu_data", "scripts")

def update_menu_data():
    """更新菜单数据"""
    db = SessionLocal()
    try:
        # 更新应用管理父菜单
        app_parent = db.query(Menu).filter(Menu.path == "/app").first()
        if app_parent:
            app_parent.code = "app"
            app_parent.component = None
            print("✅ 更新应用管理父菜单")
        
        # 更新服务管理菜单
        services = db.query(Menu).filter(Menu.path == "/app/services").first()
        if services:
            services.code = "app:services"
            services.component = "app/Services"
            print("✅ 更新服务管理菜单")
        
        # 更新系统信息菜单
        systeminfo = db.query(Menu).filter(Menu.path == "/app/systeminfo").first()
        if systeminfo:
            systeminfo.code = "app:systeminfo"
            systeminfo.component = "app/SystemInfo"
            print("✅ 更新系统信息菜单")
        
        db.commit()
        print("\n✅ 菜单数据更新完成！")
        logger.info("菜单数据更新完成")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 更新失败: {str(e)}")
        logger.error(f"更新失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    update_menu_data()
