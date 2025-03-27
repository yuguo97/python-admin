"""后台管理服务数据模型"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from typing import Optional

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希值"""
        return pwd_context.hash(password)

    @classmethod
    def authenticate(cls, db, username: str, password: str) -> Optional["User"]:
        """用户认证"""
        user = cls.get_by_username(db, username)
        if not user:
            return None
        if not cls.verify_password(password, user.hashed_password):
            return None
        return user

    @classmethod
    def get_by_username(cls, db, username: str) -> Optional["User"]:
        """根据用户名获取用户"""
        return db.query(cls).filter(cls.username == username).first()

    @classmethod
    def get(cls, db, user_id: int) -> Optional["User"]:
        """根据ID获取用户"""
        return db.query(cls).filter(cls.id == user_id).first()

    @classmethod
    def get_list(cls, db, skip: int = 0, limit: int = 10):
        """获取用户列表"""
        return db.query(cls).offset(skip).limit(limit).all()

    @classmethod
    def get_count(cls, db) -> int:
        """获取用户总数"""
        return db.query(cls).count()

    @classmethod
    def create(cls, db, user_data):
        """创建用户"""
        db_user = cls(
            username=user_data.username,
            email=user_data.email,
            hashed_password=cls.get_password_hash(user_data.password),
            is_active=user_data.is_active if hasattr(user_data, "is_active") else True,
            is_superuser=user_data.is_superuser if hasattr(user_data, "is_superuser") else False
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @classmethod
    def update(cls, db, user_id: int, user_data):
        """更新用户"""
        db_user = cls.get(db, user_id)
        if not db_user:
            return None

        update_data = user_data.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = cls.get_password_hash(update_data.pop("password"))

        for key, value in update_data.items():
            setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)
        return db_user

    @classmethod
    def delete(cls, db, user_id: int):
        """删除用户"""
        db_user = cls.get(db, user_id)
        if db_user:
            db.delete(db_user)
            db.commit()

    def create_access_token(self) -> str:
        """创建访问令牌"""
        to_encode = {
            "sub": str(self.id),
            "username": self.username,
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(to_encode, "your-secret-key", algorithm="HS256") 