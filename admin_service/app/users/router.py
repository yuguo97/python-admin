from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..auth.security import get_current_user, get_password_hash
from . import models, schemas
from utils.logger import setup_logger
from utils.response import (
    success_response, error_response,
    forbidden_error, server_error, not_found_error
)

router = APIRouter()
logger = setup_logger("users", "users")

@router.post("", response_model=schemas.User)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """创建用户"""
    if not current_user.is_admin:
        return forbidden_error()
    
    try:
        # 检查用户名是否已存在
        if db.query(models.User).filter(models.User.username == user.username).first():
            return error_response("用户名已存在", status.HTTP_400_BAD_REQUEST)
        
        # 检查邮箱是否已存在
        if db.query(models.User).filter(models.User.email == user.email).first():
            return error_response("邮箱已存在", status.HTTP_400_BAD_REQUEST)
        
        # 创建新用户
        db_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(user.password),
            is_active=user.is_active,
            is_admin=user.is_admin
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"创建用户成功: {user.username}")
        return success_response(schemas.User.from_orm(db_user))
    except Exception as e:
        logger.error(f"创建用户失败: {str(e)}")
        return server_error("创建用户失败")

@router.get("", response_model=List[schemas.User])
async def get_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    获取用户列表
    
    参数:
        - skip: 跳过的记录数（分页用）
        - limit: 返回的最大记录数（分页用）
        - current_user: 当前登录用户（自动获取）
    
    返回:
        用户列表，每个用户包含:
        - id: 用户ID
        - username: 用户名
        - email: 邮箱
        - is_active: 是否激活
        - is_admin: 是否管理员
        - created_at: 创建时间
    
    权限:
        - 管理员可以查看所有用户
        - 普通用户只能查看自己的信息
    
    错误:
        - 401: 未授权访问
        - 403: 权限不足
        - 500: 服务器内部错误
    """
    try:
        if current_user.is_admin:
            users = db.query(models.User).offset(skip).limit(limit).all()
        else:
            users = [current_user]
        return success_response(users)
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}")
        return error_response(f"获取用户列表失败: {str(e)}")

@router.get("/me", response_model=schemas.User)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return success_response(schemas.User.from_orm(current_user))

@router.get("/{user_id}", response_model=schemas.User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """获取指定用户信息"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return not_found_error(f"用户不存在: {user_id}")
        return success_response(schemas.User.from_orm(user))
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return server_error("获取用户信息失败")

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """更新用户信息"""
    if not current_user.is_admin and current_user.id != user_id:
        return forbidden_error()
    
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not db_user:
            return not_found_error(f"用户不存在: {user_id}")
        
        # 检查用户名是否已存在
        if user_update.username and user_update.username != db_user.username:
            if db.query(models.User).filter(models.User.username == user_update.username).first():
                return error_response("用户名已存在", status.HTTP_400_BAD_REQUEST)
        
        # 检查邮箱是否已存在
        if user_update.email and user_update.email != db_user.email:
            if db.query(models.User).filter(models.User.email == user_update.email).first():
                return error_response("邮箱已存在", status.HTTP_400_BAD_REQUEST)
        
        # 更新用户信息
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        # 非管理员不能修改管理员权限
        if not current_user.is_admin and "is_admin" in update_data:
            update_data.pop("is_admin")
        
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        logger.info(f"更新用户成功: {user_id}")
        return success_response(schemas.User.from_orm(db_user))
    except Exception as e:
        logger.error(f"更新用户失败: {str(e)}")
        return server_error("更新用户失败")

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """删除用户"""
    if not current_user.is_admin:
        return forbidden_error()
    
    try:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not db_user:
            return not_found_error(f"用户不存在: {user_id}")
        
        # 不能删除自己
        if db_user.id == current_user.id:
            return error_response("不能删除当前用户", status.HTTP_400_BAD_REQUEST)
        
        db.delete(db_user)
        db.commit()
        logger.info(f"删除用户成功: {user_id}")
        return success_response(message=f"用户已删除: {user_id}")
    except Exception as e:
        logger.error(f"删除用户失败: {str(e)}")
        return server_error("删除用户失败") 