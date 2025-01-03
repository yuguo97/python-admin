from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from . import schemas
from .security import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from utils.logger import setup_logger
from utils.response import success_response, error_response
from utils.auth import verify_token

router = APIRouter()
logger = setup_logger("auth_router", "auth")

@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    
    参数:
        - form_data: OAuth2密码表单
            - username: 用户名
            - password: 密码
    
    返回:
        - access_token: JWT访问令牌
        - token_type: 令牌类型 (Bearer)
    
    错误:
        - 401: 用户名或密码错误
        - 500: 服务器内部错误
    
    示例:
        ```
        POST /auth/login
        Content-Type: application/x-www-form-urlencoded
        
        username=admin&password=123456
        ```
    """
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"登录失败: 用户名或密码错误 - {form_data.username}")
            return error_response(
                "用户名或密码错误",
                status.HTTP_401_UNAUTHORIZED
            )
        
        # 创建访问令牌
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"用户登录成功: {user.username}")
        return success_response({
            "access_token": access_token,
            "token_type": "bearer"
        })
        
    except Exception as e:
        logger.error(f"登录过程出错: {str(e)}")
        return error_response(f"登录失败: {str(e)}")

@router.post("/refresh-token", response_model=schemas.Token)
async def refresh_token(
    current_token: dict = Depends(verify_token)
):
    """
    刷新访问令牌
    
    参数:
        - current_token: 当前的有效令牌（从Authorization header获取）
    
    返回:
        - access_token: 新的JWT访问令牌
        - token_type: 令牌类型 (Bearer)
    
    错误:
        - 401: 令牌无效或已过期
        - 500: 服务器内部错误
    
    说明:
        使用当前有效的令牌获取新的访问令牌，可用于令牌即将过期时刷新
    
    示例:
        ```
        POST /auth/refresh-token
        Authorization: Bearer <current_token>
        ```
    """
    try:
        username = current_token.get("sub")
        if not username:
            return error_response(
                "无效的令牌",
                status.HTTP_401_UNAUTHORIZED
            )
        
        # 创建新的访问令牌
        new_token = create_access_token(
            data={"sub": username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"令牌刷新成功: {username}")
        return success_response({
            "access_token": new_token,
            "token_type": "bearer"
        })
        
    except Exception as e:
        logger.error(f"令牌刷新失败: {str(e)}")
        return error_response(f"令牌刷新失败: {str(e)}") 