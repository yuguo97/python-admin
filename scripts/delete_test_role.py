"""删除测试角色"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin_service.app.database import SessionLocal
from admin_service.app.models import Role

def delete_test_role():
    """删除test角色"""
    db = SessionLocal()
    try:
        test_role = db.query(Role).filter(Role.code == "test").first()
        if test_role:
            db.delete(test_role)
            db.commit()
            print(f"✅ 已删除角色: {test_role.name} (编码: {test_role.code})")
        else:
            print("ℹ️  未找到test角色")
    except Exception as e:
        db.rollback()
        print(f"❌ 删除失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    delete_test_role()
