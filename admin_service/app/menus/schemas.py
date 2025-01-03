from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class MenuBase(BaseModel):
    """菜单基础模型"""
    name: str
    path: str
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = 0

class MenuCreate(MenuBase):
    """菜单创建模型"""
    pass

class MenuUpdate(BaseModel):
    """菜单更新模型"""
    name: Optional[str] = None
    path: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None

class Menu(MenuBase):
    """菜单返回模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MenuTree(Menu):
    """菜单树模型"""
    children: List['MenuTree'] = []

    class Config:
        from_attributes = True 