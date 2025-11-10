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
    code = Column(String(50), unique=True, index=True, comment="角色编码")
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

    @classmethod
    def get_list(cls, db, skip: int = 0, limit: int = 100) -> List["Role"]:
        """获取角色列表(别名)"""
        return cls.list_roles(db, skip, limit)

    @classmethod
    def get(cls, db, role_id: int) -> Optional["Role"]:
        """根据ID获取角色(别名)"""
        return cls.get_by_id(db, role_id)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

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

    @classmethod
    def get_list(cls, db, skip: int = 0, limit: int = 100) -> List["Permission"]:
        """获取权限列表(别名)"""
        return cls.list_permissions(db, skip, limit)

    @classmethod
    def get(cls, db, permission_id: int) -> Optional["Permission"]:
        """根据ID获取权限(别名)"""
        return cls.get_by_id(db, permission_id)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "role_id": self.role_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# User 模型已移至 users/models.py,避免重复定义