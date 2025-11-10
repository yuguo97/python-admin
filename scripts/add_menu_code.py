"""为菜单表添加code字段"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from admin_service.app.database import SessionLocal
from utils.logger import setup_logger

logger = setup_logger("add_menu_code", "scripts")

def add_menu_code_column():
    """为menus表添加code字段"""
    db = SessionLocal()
    try:
        # 检查code列是否已存在
        check_sql = """
        SELECT COUNT(*) as count
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'menus'
        AND COLUMN_NAME = 'code'
        """
        
        result = db.execute(text(check_sql)).fetchone()
        
        if result[0] == 0:
            logger.info("开始添加code列...")
            alter_sql = """
            ALTER TABLE menus
            ADD COLUMN code VARCHAR(100) UNIQUE COMMENT '菜单编码'
            AFTER title
            """
            db.execute(text(alter_sql))
            
            # 为现有菜单生成code (基于path)
            logger.info("为现有菜单生成编码...")
            update_sql = """
            UPDATE menus
            SET code = REPLACE(REPLACE(path, '/', '_'), '-', '_')
            WHERE code IS NULL
            """
            db.execute(text(update_sql))
            
            # 添加索引
            logger.info("添加索引...")
            index_sql = """
            CREATE INDEX ix_menus_code ON menus(code)
            """
            db.execute(text(index_sql))
            
            db.commit()
            logger.info("code列添加成功!")
            print("✅ 菜单表code字段添加成功!")
        else:
            logger.info("code列已存在，跳过")
            print("ℹ️  菜单表code字段已存在")
            
    except Exception as e:
        db.rollback()
        logger.error(f"添加code列失败: {str(e)}")
        print(f"❌ 添加失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_menu_code_column()
