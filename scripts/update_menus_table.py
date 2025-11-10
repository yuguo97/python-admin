"""更新menus表结构,添加code、component、visible字段"""
import sys
sys.path.insert(0, '.')

from admin_service.app.database import SessionLocal
from sqlalchemy import text
from utils.logger import setup_logger

logger = setup_logger("update_menus_table", "scripts")

def update_menus_table():
    """更新menus表结构"""
    db = SessionLocal()
    try:
        # 添加code字段
        try:
            db.execute(text("ALTER TABLE menus ADD COLUMN code VARCHAR(100) UNIQUE COMMENT '菜单编码'"))
            print("✅ 添加code字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("ℹ️  code字段已存在")
            else:
                raise
        
        # 添加component字段
        try:
            db.execute(text("ALTER TABLE menus ADD COLUMN component VARCHAR(200) COMMENT '组件路径'"))
            print("✅ 添加component字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("ℹ️  component字段已存在")
            else:
                raise
        
        # 添加visible字段
        try:
            db.execute(text("ALTER TABLE menus ADD COLUMN visible INT DEFAULT 1 COMMENT '是否可见: 1-是 0-否'"))
            print("✅ 添加visible字段")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("ℹ️  visible字段已存在")
            else:
                raise
        
        db.commit()
        print("\n✅ menus表结构更新完成！")
        logger.info("menus表结构更新完成")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 更新失败: {str(e)}")
        logger.error(f"更新失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    update_menus_table()
