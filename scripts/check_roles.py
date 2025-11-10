"""检查数据库中的角色"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from admin_service.app.database import SessionLocal
from admin_service.app.models import Role

def check_roles():
    """检查所有角色"""
    db = SessionLocal()
    try:
        roles = db.query(Role).all()
        print(f"\n数据库中共有 {len(roles)} 个角色:\n")
        print(f"{'ID':<5} {'名称':<15} {'编码':<20} {'描述':<30}")
        print("-" * 70)
        for role in roles:
            print(f"{role.id:<5} {role.name:<15} {role.code or 'NULL':<20} {role.description or '':<30}")
    finally:
        db.close()

if __name__ == "__main__":
    check_roles()
