"""后台管理服务数据模式"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class PermissionBase(BaseModel):
    """权限基础模型"""
    name: str
    code: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    """权限创建模型"""
    role_id: int

class PermissionUpdate(BaseModel):
    """权限更新模型"""
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    role_id: Optional[int] = None

class Permission(PermissionBase):
    """权限响应模型"""
    id: int
    role_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    """角色基础模型"""
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    """角色创建模型"""
    pass

class RoleUpdate(BaseModel):
    """角色更新模型"""
    name: Optional[str] = None
    description: Optional[str] = None

class Role(RoleBase):
    """角色响应模型"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    permissions: List[Permission] = []

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

class UserCreate(UserBase):
    """用户创建模型"""
    password: str
    role_ids: Optional[List[int]] = None

class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    role_ids: Optional[List[int]] = None

class User(UserBase):
    """用户响应模型"""
    id: int
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    roles: List[Role] = []

    class Config:
        from_attributes = True 