"""创建管理员用户脚本"""

from sqlalchemy.orm import Session
from admin_service.app.database import SessionLocal
from admin_service.app.models import User, Role, Permission
from utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger("create_admin", "scripts")

def create_admin_user():
    """创建管理员用户"""
    db = SessionLocal()
    try:
        # 创建超级管理员角色
        admin_role = Role(
            name="超级管理员",
            description="系统超级管理员，拥有所有权限"
        )
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)
        logger.info("超级管理员角色创建成功")

        # 创建基本权限
        permissions = [
            Permission(
                name="用户管理",
                code="user:manage",
                description="用户管理权限",
                role_id=admin_role.id
            ),
            Permission(
                name="角色管理",
                code="role:manage",
                description="角色管理权限",
                role_id=admin_role.id
            ),
            Permission(
                name="权限管理",
                code="permission:manage",
                description="权限管理权限",
                role_id=admin_role.id
            )
        ]
        
        for permission in permissions:
            db.add(permission)
        db.commit()
        logger.info("基本权限创建成功")

        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=User.get_password_hash("admin123"),
            full_name="系统管理员",
            is_active=True,
            is_superuser=True
        )
        admin_user.roles.append(admin_role)
        
        db.add(admin_user)
        db.commit()
        logger.info("管理员用户创建成功")
        
        print("管理员用户创建成功！")
        print("用户名: admin")
        print("密码: admin123")
        print("请登录后立即修改密码！")
        
    except Exception as e:
        logger.error(f"创建管理员用户失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user() 