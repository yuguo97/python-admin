from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Menu(Base):
    """菜单模型"""
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    code = Column(String(100), unique=True, index=True, comment="菜单编码")
    path = Column(String(100))
    component = Column(String(200), comment="组件路径")
    icon = Column(String(50))
    parent_id = Column(Integer, ForeignKey("menus.id"))
    sort_order = Column(Integer, default=0)
    visible = Column(Integer, default=1, comment="是否可见: 1-是 0-否")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系定义
    children = relationship("Menu", backref="parent", remote_side=[id])