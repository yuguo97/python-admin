"""为角色表添加code字段的迁移脚本"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from admin_service.app.database import SessionLocal, engine
from utils.logger import setup_logger

logger = setup_logger("add_role_code", "scripts")

def add_role_code_column():
    """为roles表添加code字段"""
    db = SessionLocal()
    try:
        # 检查code列是否已存在
        check_sql = """
        SELECT COUNT(*) as count
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'roles'
        AND COLUMN_NAME = 'code'
        """
        
        result = db.execute(text(check_sql)).fetchone()
        
        if result[0] == 0:
            # 添加code列
            logger.info("开始添加code列...")
            alter_sql = """
            ALTER TABLE roles
            ADD COLUMN code VARCHAR(50) UNIQUE COMMENT '角色编码'
            AFTER name
            """
            db.execute(text(alter_sql))
            
            # 为现有角色生成code
            logger.info("为现有角色生成编码...")
            update_sql = """
            UPDATE roles
            SET code = LOWER(REPLACE(name, ' ', '_'))
            WHERE code IS NULL
            """
            db.execute(text(update_sql))
            
            # 添加索引
            logger.info("添加索引...")
            index_sql = """
            CREATE INDEX ix_roles_code ON roles(code)
            """
            db.execute(text(index_sql))
            
            db.commit()
            logger.info("code列添加成功!")
            print("✅ 角色表code字段添加成功!")
        else:
            logger.info("code列已存在，跳过")
            print("ℹ️  角色表code字段已存在")
            
    except Exception as e:
        db.rollback()
        logger.error(f"添加code列失败: {str(e)}")
        print(f"❌ 添加失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_role_code_column()
