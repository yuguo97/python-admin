"""重置管理员密码"""
import sys
sys.path.insert(0, '.')

from admin_service.app.database import SessionLocal
from admin_service.app.users.models import User
from admin_service.app.models import Role
from admin_service.app.auth.security import get_password_hash
from utils.logger import setup_logger

logger = setup_logger("reset_admin", "scripts")

def reset_admin():
    """重置管理员密码"""
    db = SessionLocal()
    try:
        # 查找admin用户
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            # 重置密码为123456
            admin_user.hashed_password = get_password_hash("123456")
            db.commit()
            print("✅ 管理员密码已重置为: 123456")
            logger.info("管理员密码已重置")
        else:
            print("❌ 未找到admin用户")
            logger.error("未找到admin用户")
    except Exception as e:
        db.rollback()
        print(f"❌ 重置失败: {str(e)}")
        logger.error(f"重置失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
