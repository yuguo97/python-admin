import os
import sys
from pathlib import Path
from getpass import getpass

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from admin_service.app.database import SessionLocal
from admin_service.app.models import User
from admin_service.app.auth.security import get_password_hash
from utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger("create_admin", "create_admin")

def create_admin_user():
    """创建管理员用户"""
    try:
        # 获取用户输入
        username = input("请输入管理员用户名: ")
        email = input("请输入管理员邮箱: ")
        password = getpass("请输入管理员密码: ")
        confirm_password = getpass("请再次输入密码: ")
        
        # 验证密码
        if password != confirm_password:
            logger.error("两次输入的密码不一致")
            return
        
        # 验证密码强度
        if len(password) < 8:
            logger.error("密码长度必须大于8位")
            return
            
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 检查用户是否已存在
            existing_user = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                logger.error("用户名或邮箱已存在")
                return
            
            # 创建新用户
            admin_user = User(
                username=username,
                email=email,
                hashed_password=get_password_hash(password),
                is_active=True,
                is_superuser=True
            )
            
            # 保存到数据库
            db.add(admin_user)
            db.commit()
            logger.info(f"管理员用户 {username} 创建成功")
            
        except Exception as e:
            db.rollback()
            logger.error(f"创建管理员用户失败: {str(e)}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"创建管理员用户失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_admin_user() 