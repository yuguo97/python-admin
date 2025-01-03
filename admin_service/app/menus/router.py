from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..auth.security import get_current_user
from . import models, schemas
from ..users.models import User
from utils.logger import setup_logger
from utils.response import (
    success_response, error_response,
    forbidden_error, server_error, not_found_error
)

router = APIRouter()
logger = setup_logger("menus", "menus")

@router.post("", response_model=schemas.Menu)
async def create_menu(
    menu: schemas.MenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建菜单"""
    if not current_user.is_admin:
        return forbidden_error()
    
    try:
        db_menu = models.Menu(**menu.dict())
        db.add(db_menu)
        db.commit()
        db.refresh(db_menu)
        return success_response(schemas.Menu.from_orm(db_menu))
    except Exception as e:
        logger.error(f"创建菜单失败: {str(e)}")
        return server_error("创建菜单失败")

@router.get("", response_model=List[schemas.MenuTree])
async def get_menus(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取菜单树"""
    try:
        menus = db.query(models.Menu).filter(models.Menu.parent_id.is_(None)).all()
        return success_response([schemas.MenuTree.from_orm(menu) for menu in menus])
    except Exception as e:
        logger.error(f"获取菜单列表失败: {str(e)}")
        return server_error("获取菜单列表失败")

@router.get("/{menu_id}", response_model=schemas.Menu)
async def get_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定菜单"""
    try:
        menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
        if not menu:
            return not_found_error(f"菜单不存在: {menu_id}")
        return success_response(schemas.Menu.from_orm(menu))
    except Exception as e:
        logger.error(f"获取菜单失败: {str(e)}")
        return server_error("获取菜单失败")

@router.put("/{menu_id}", response_model=schemas.Menu)
async def update_menu(
    menu_id: int,
    menu_update: schemas.MenuUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新菜单"""
    if not current_user.is_admin:
        return forbidden_error()
    
    try:
        db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
        if not db_menu:
            return not_found_error(f"菜单不存在: {menu_id}")
        
        for key, value in menu_update.dict(exclude_unset=True).items():
            setattr(db_menu, key, value)
        
        db.commit()
        db.refresh(db_menu)
        return success_response(schemas.Menu.from_orm(db_menu))
    except Exception as e:
        logger.error(f"更新菜单失败: {str(e)}")
        return server_error("更新菜单失败")

@router.delete("/{menu_id}")
async def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除菜单"""
    if not current_user.is_admin:
        return forbidden_error()
    
    try:
        db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
        if not db_menu:
            return not_found_error(f"菜单不存在: {menu_id}")
        
        # 检查是否有子菜单
        children = db.query(models.Menu).filter(models.Menu.parent_id == menu_id).all()
        if children:
            return error_response("无法删除含有子菜单的菜单项", status.HTTP_400_BAD_REQUEST)
        
        db.delete(db_menu)
        db.commit()
        return success_response(message=f"菜单已删除: {menu_id}")
    except Exception as e:
        logger.error(f"删除菜单失败: {str(e)}")
        return server_error("删除菜单失败") 