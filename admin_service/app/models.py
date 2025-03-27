"""后台管理服务数据模型"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from typing import Optional, List

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 用户-角色关联表
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete='CASCADE')),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete='CASCADE'))
)

class Role(Base):
    """角色模型"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # 关联关系
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", back_populates="role", cascade="all, delete-orphan")

    @classmethod
    def get_by_name(cls, db, name: str) -> Optional["Role"]:
        """根据名称获取角色"""
        return db.query(cls).filter(cls.name == name).first()

    @classmethod
    def get_by_id(cls, db, id: int) -> Optional["Role"]:
        """根据ID获取角色"""
        return db.query(cls).filter(cls.id == id).first()

    @classmethod
    def list_roles(cls, db, skip: int = 0, limit: int = 100) -> List["Role"]:
        """获取角色列表"""
        return db.query(cls).offset(skip).limit(limit).all()

    @classmethod
    def get_count(cls, db) -> int:
        """获取角色总数"""
        return db.query(cls).count()

class Permission(Base):
    """权限模型"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    code = Column(String(50), unique=True, index=True)
    description = Column(String(200))
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # 关联关系
    role = relationship("Role", back_populates="permissions")

    @classmethod
    def get_by_code(cls, db, code: str) -> Optional["Permission"]:
        """根据编码获取权限"""
        return db.query(cls).filter(cls.code == code).first()

    @classmethod
    def get_by_id(cls, db, id: int) -> Optional["Permission"]:
        """根据ID获取权限"""
        return db.query(cls).filter(cls.id == id).first()

    @classmethod
    def list_permissions(cls, db, skip: int = 0, limit: int = 100) -> List["Permission"]:
        """获取权限列表"""
        return db.query(cls).offset(skip).limit(limit).all()

    @classmethod
    def get_count(cls, db) -> int:
        """获取权限总数"""
        return db.query(cls).count()

class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # 关联关系
    roles = relationship("Role", secondary=user_roles, back_populates="users")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希值"""
        return pwd_context.hash(password)

    def set_password(self, password: str):
        """设置密码"""
        self.hashed_password = self.get_password_hash(password)

    @classmethod
    def authenticate(cls, db, username: str, password: str) -> Optional["User"]:
        """用户认证"""
        user = cls.get_by_username(db, username)
        if not user or not cls.verify_password(password, user.hashed_password):
            return None
        return user

    @classmethod
    def get_by_username(cls, db, username: str) -> Optional["User"]:
        """根据用户名获取用户"""
        return db.query(cls).filter(cls.username == username).first()

    @classmethod
    def get_by_email(cls, db, email: str) -> Optional["User"]:
        """根据邮箱获取用户"""
        return db.query(cls).filter(cls.email == email).first()

    @classmethod
    def get_by_id(cls, db, id: int) -> Optional["User"]:
        """根据ID获取用户"""
        return db.query(cls).filter(cls.id == id).first()

    @classmethod
    def list_users(cls, db, skip: int = 0, limit: int = 100) -> List["User"]:
        """获取用户列表"""
        return db.query(cls).offset(skip).limit(limit).all()

    @classmethod
    def create_user(cls, db, user_data):
        """创建用户"""
        db_user = cls(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @classmethod
    def update_user(cls, db, user_id: int, user_data):
        """更新用户"""
        db_user = cls.get_by_id(db, user_id)
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
    def delete_user(cls, db, user_id: int):
        """删除用户"""
        db_user = cls.get_by_id(db, user_id)
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