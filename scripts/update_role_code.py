"""更新角色编码为fcadmin"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from admin_service.app.database import SessionLocal
from admin_service.app.models import Role
from utils.logger import setup_logger

logger = setup_logger("update_role_code", "scripts")

def update_role_code():
    """更新超级管理员角色编码为fcadmin"""
    db = SessionLocal()
    try:
        # 查找超级管理员角色
        admin_role = db.query(Role).filter(Role.name == "超级管理员").first()
        
        if admin_role:
            old_code = admin_role.code
            admin_role.code = "fcadmin"
            db.commit()
            logger.info(f"角色编码已更新: {old_code} -> fcadmin")
            print(f"✅ 角色编码已更新: {old_code} -> fcadmin")
        else:
            logger.warning("未找到超级管理员角色")
            print("⚠️  未找到超级管理员角色")
            
    except Exception as e:
        db.rollback()
        logger.error(f"更新角色编码失败: {str(e)}")
        print(f"❌ 更新失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_role_code()
