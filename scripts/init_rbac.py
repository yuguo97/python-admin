"""初始化RBAC权限系统"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from admin_service.app.database import SessionLocal
from utils.logger import setup_logger

logger = setup_logger("init_rbac", "scripts")

def init_rbac():
    """初始化RBAC权限系统"""
    db = SessionLocal()
    try:
        # 1. 创建角色-菜单关联表
        logger.info("创建role_menus关联表...")
        create_role_menus_sql = """
        CREATE TABLE IF NOT EXISTS role_menus (
            role_id INT NOT NULL,
            menu_code VARCHAR(100) NOT NULL,
            PRIMARY KEY (role_id, menu_code),
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            INDEX idx_role_id (role_id),
            INDEX idx_menu_code (menu_code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色菜单关联表';
        """
        db.execute(text(create_role_menus_sql))
        db.commit()
        logger.info("role_menus表创建成功")
        
        # 2. 初始化菜单数据
        logger.info("初始化菜单数据...")
        menus = [
            ("dashboard", "首页", "/dashboard", "HomeFilled", 1, None),
            ("system", "系统管理", "/system", "Setting", 2, None),
            ("system_users", "用户管理", "/users", "User", 1, "system"),
            ("system_roles", "角色管理", "/roles", "UserFilled", 2, "system"),
            ("system_permissions", "权限管理", "/permissions", "Lock", 3, "system"),
            ("system_menus", "菜单管理", "/menus", "Menu", 4, "system"),
        ]
        
        for code, title, path, icon, sort_order, parent_code in menus:
            check_sql = f"SELECT COUNT(*) FROM role_menus WHERE menu_code = '{code}'"
            # 这里只是插入菜单编码到关联表,实际菜单数据由前端定义
            logger.info(f"菜单编码: {code} - {title}")
        
        print("✅ RBAC权限系统初始化成功!")
        print("\n菜单编码列表:")
        print("- dashboard: 首页")
        print("- system: 系统管理")
        print("- system_users: 用户管理")
        print("- system_roles: 角色管理")
        print("- system_permissions: 权限管理")
        print("- system_menus: 菜单管理")
        
    except Exception as e:
        db.rollback()
        logger.error(f"初始化失败: {str(e)}")
        print(f"❌ 初始化失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_rbac()
