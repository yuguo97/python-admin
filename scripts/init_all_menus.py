"""初始化所有菜单数据"""
import sys
sys.path.insert(0, '.')

from admin_service.app.database import SessionLocal
from admin_service.app.menus.models import Menu
from utils.logger import setup_logger

logger = setup_logger("init_all_menus", "scripts")

def init_all_menus():
    """初始化所有菜单"""
    db = SessionLocal()
    try:
        # 首页
        dashboard = db.query(Menu).filter(Menu.code == "dashboard").first()
        if not dashboard:
            dashboard = Menu(
                name="首页",
                code="dashboard",
                path="/dashboard",
                component="Dashboard",
                icon="HomeFilled",
                parent_id=None,
                sort_order=1,
                visible=1
            )
            db.add(dashboard)
            print("✅ 创建首页菜单")
        
        # 应用管理父菜单
        app_parent = db.query(Menu).filter(Menu.code == "app").first()
        if not app_parent:
            app_parent = Menu(
                name="应用管理",
                code="app",
                path="/app",
                component=None,
                icon="Monitor",
                parent_id=None,
                sort_order=2,
                visible=1
            )
            db.add(app_parent)
            db.flush()
            print("✅ 创建应用管理父菜单")
        
        # 服务管理
        services = db.query(Menu).filter(Menu.code == "app:services").first()
        if not services:
            services = Menu(
                name="服务管理",
                code="app:services",
                path="/app/services",
                component="app/Services",
                icon="Monitor",
                parent_id=app_parent.id,
                sort_order=1,
                visible=1
            )
            db.add(services)
            print("✅ 创建服务管理菜单")
        
        # 系统信息
        systeminfo = db.query(Menu).filter(Menu.code == "app:systeminfo").first()
        if not systeminfo:
            systeminfo = Menu(
                name="系统信息",
                code="app:systeminfo",
                path="/app/systeminfo",
                component="app/SystemInfo",
                icon="DataAnalysis",
                parent_id=app_parent.id,
                sort_order=2,
                visible=1
            )
            db.add(systeminfo)
            print("✅ 创建系统信息菜单")
        
        # 系统管理父菜单
        system_parent = db.query(Menu).filter(Menu.code == "system").first()
        if not system_parent:
            system_parent = Menu(
                name="系统管理",
                code="system",
                path="/system",
                component=None,
                icon="Setting",
                parent_id=None,
                sort_order=3,
                visible=1
            )
            db.add(system_parent)
            db.flush()
            print("✅ 创建系统管理父菜单")
        
        # 用户管理
        users = db.query(Menu).filter(Menu.code == "system:user").first()
        if not users:
            users = Menu(
                name="用户管理",
                code="system:user",
                path="/system/users",
                component="system/Users",
                icon="User",
                parent_id=system_parent.id,
                sort_order=1,
                visible=1
            )
            db.add(users)
            print("✅ 创建用户管理菜单")
        
        # 角色管理
        roles = db.query(Menu).filter(Menu.code == "system:role").first()
        if not roles:
            roles = Menu(
                name="角色管理",
                code="system:role",
                path="/system/roles",
                component="system/Roles",
                icon="UserFilled",
                parent_id=system_parent.id,
                sort_order=2,
                visible=1
            )
            db.add(roles)
            print("✅ 创建角色管理菜单")
        
        # 权限管理
        permissions = db.query(Menu).filter(Menu.code == "system:permission").first()
        if not permissions:
            permissions = Menu(
                name="权限管理",
                code="system:permission",
                path="/system/permissions",
                component="system/Permissions",
                icon="Lock",
                parent_id=system_parent.id,
                sort_order=3,
                visible=1
            )
            db.add(permissions)
            print("✅ 创建权限管理菜单")
        
        # 菜单管理
        menus = db.query(Menu).filter(Menu.code == "system:menu").first()
        if not menus:
            menus = Menu(
                name="菜单管理",
                code="system:menu",
                path="/system/menus",
                component="system/Menus",
                icon="Menu",
                parent_id=system_parent.id,
                sort_order=4,
                visible=1
            )
            db.add(menus)
            print("✅ 创建菜单管理菜单")
        
        db.commit()
        print("\n✅ 所有菜单初始化完成！")
        logger.info("所有菜单初始化完成")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败: {str(e)}")
        logger.error(f"初始化失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    init_all_menus()
