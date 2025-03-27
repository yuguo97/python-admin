"""后台管理服务主应用"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from . import models, schemas
from .database import SessionLocal, engine, init_db, Base
from utils.logger import setup_logger
from utils.response import (
    success_response, error_response, unauthorized_error,
    forbidden_error, server_error, not_found_error
)
from utils.auth import verify_token
from utils.tracing import init_tracing, create_span, add_span_attribute, set_span_status, end_span
from opentelemetry.trace import StatusCode

# 设置日志记录器
logger = setup_logger("admin_service", "admin")

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="后台管理服务",
    description="""
    提供系统后台管理功能的服务。
    
    ## 功能特点
    * 用户认证与授权
    * 用户管理
    * 角色管理
    * 权限管理
    * 系统配置管理
    """,
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# 初始化链路追踪
init_tracing(app, "admin-service")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 自定义API文档路由
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
    )

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"全局异常: {str(exc)}")
    return server_error(f"服务器内部错误: {str(exc)}")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    return error_response(
        message=str(exc.detail),
        status_code=exc.status_code
    )

@app.on_event("startup")
async def startup_event():
    """服务启动时初始化"""
    logger.info("初始化后台管理服务...")
    init_db()
    logger.info("后台管理服务初始化完成")

@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时清理资源"""
    logger.info("关闭后台管理服务...")
    logger.info("后台管理服务已关闭")

# 依赖项
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 用户认证相关路由
@app.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    with create_span("user_login") as span:
        logger.info(f"用户登录: {form_data.username}")
        add_span_attribute(span, "username", form_data.username)
        
        try:
            user = models.User.authenticate(db, form_data.username, form_data.password)
            if not user:
                logger.warning(f"登录失败: 用户名或密码错误 - {form_data.username}")
                add_span_attribute(span, "login.status", "failed")
                set_span_status(span, StatusCode.ERROR, "用户名或密码错误")
                return unauthorized_error("用户名或密码错误")
            
            access_token = models.User.create_access_token(user)
            logger.info(f"用户登录成功: {form_data.username}")
            add_span_attribute(span, "login.status", "success")
            set_span_status(span, StatusCode.OK)
            return success_response({
                "access_token": access_token,
                "token_type": "bearer"
            })
        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error("登录失败")

# 用户管理相关路由
@app.post("/users")
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """创建用户"""
    with create_span("create_user") as span:
        logger.info(f"创建用户: {user.username}")
        add_span_attribute(span, "username", user.username)
        
        try:
            db_user = models.User.get_by_username(db, user.username)
            if db_user:
                logger.warning(f"创建用户失败: 用户名已存在 - {user.username}")
                add_span_attribute(span, "user.exists", "true")
                set_span_status(span, StatusCode.ERROR, "用户名已存在")
                return error_response("用户名已存在", status_code=400)
            
            new_user = models.User.create(db, user)
            logger.info(f"用户创建成功: {user.username}")
            add_span_attribute(span, "user.id", str(new_user.id))
            set_span_status(span, StatusCode.OK)
            return success_response(new_user)
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error("创建用户失败")

@app.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """获取用户列表"""
    with create_span("list_users") as span:
        logger.info(f"获取用户列表: skip={skip}, limit={limit}")
        add_span_attribute(span, "skip", str(skip))
        add_span_attribute(span, "limit", str(limit))
        
        try:
            users = models.User.get_list(db, skip=skip, limit=limit)
            total = models.User.get_count(db)
            logger.info(f"获取到 {len(users)} 个用户")
            add_span_attribute(span, "users.count", str(len(users)))
            set_span_status(span, StatusCode.OK)
            return success_response({
                "items": users,
                "total": total,
                "skip": skip,
                "limit": limit
            })
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error("获取用户列表失败")

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """获取用户详情"""
    with create_span("get_user") as span:
        logger.info(f"获取用户详情: {user_id}")
        add_span_attribute(span, "user.id", str(user_id))
        
        try:
            user = models.User.get(db, user_id)
            if not user:
                logger.warning(f"用户不存在: {user_id}")
                add_span_attribute(span, "user.exists", "false")
                set_span_status(span, StatusCode.ERROR, "用户不存在")
                return not_found_error(f"用户不存在: {user_id}")
            
            logger.info(f"获取用户详情成功: {user.username}")
            add_span_attribute(span, "username", user.username)
            set_span_status(span, StatusCode.OK)
            return success_response(user)
        except Exception as e:
            logger.error(f"获取用户详情失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error("获取用户详情失败")

@app.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """更新用户信息"""
    with create_span("update_user") as span:
        logger.info(f"更新用户信息: {user_id}")
        add_span_attribute(span, "user.id", str(user_id))
        
        try:
            db_user = models.User.get(db, user_id)
            if not db_user:
                logger.warning(f"用户不存在: {user_id}")
                add_span_attribute(span, "user.exists", "false")
                set_span_status(span, StatusCode.ERROR, "用户不存在")
                return not_found_error(f"用户不存在: {user_id}")
            
            updated_user = models.User.update(db, user_id, user)
            logger.info(f"用户信息更新成功: {updated_user.username}")
            add_span_attribute(span, "username", updated_user.username)
            set_span_status(span, StatusCode.OK)
            return success_response(updated_user)
        except Exception as e:
            logger.error(f"更新用户信息失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error("更新用户信息失败")

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token)
):
    """删除用户"""
    with create_span("delete_user") as span:
        logger.info(f"删除用户: {user_id}")
        add_span_attribute(span, "user.id", str(user_id))
        
        try:
            db_user = models.User.get(db, user_id)
            if not db_user:
                logger.warning(f"用户不存在: {user_id}")
                add_span_attribute(span, "user.exists", "false")
                set_span_status(span, StatusCode.ERROR, "用户不存在")
                return not_found_error(f"用户不存在: {user_id}")
            
            models.User.delete(db, user_id)
            logger.info(f"用户删除成功: {user_id}")
            add_span_attribute(span, "delete.status", "success")
            set_span_status(span, StatusCode.OK)
            return success_response({"message": "用户删除成功"})
        except Exception as e:
            logger.error(f"删除用户失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error("删除用户失败")

# 角色相关路由
@app.post("/roles/", response_model=schemas.Role)
@create_span("create_role")
async def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    """创建角色"""
    try:
        db_role = models.Role(**role.dict())
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        add_span_attribute("role_id", db_role.id)
        set_span_status("success")
        return db_role
    except Exception as e:
        set_span_status("error")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/roles/", response_model=List[schemas.Role])
@create_span("list_roles")
async def list_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取角色列表"""
    try:
        roles = db.query(models.Role).offset(skip).limit(limit).all()
        add_span_attribute("count", len(roles))
        set_span_status("success")
        return roles
    except Exception as e:
        set_span_status("error")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/roles/{role_id}", response_model=schemas.Role)
@create_span("get_role")
async def get_role(role_id: int, db: Session = Depends(get_db)):
    """获取角色详情"""
    try:
        role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        add_span_attribute("role_id", role_id)
        set_span_status("success")
        return role
    except Exception as e:
        set_span_status("error")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/roles/{role_id}", response_model=schemas.Role)
@create_span("update_role")
async def update_role(role_id: int, role: schemas.RoleUpdate, db: Session = Depends(get_db)):
    """更新角色"""
    try:
        db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if not db_role:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        for key, value in role.dict(exclude_unset=True).items():
            setattr(db_role, key, value)
        
        db_role.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_role)
        add_span_attribute("role_id", role_id)
        set_span_status("success")
        return db_role
    except Exception as e:
        set_span_status("error")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/roles/{role_id}")
@create_span("delete_role")
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    """删除角色"""
    try:
        db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if not db_role:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        db.delete(db_role)
        db.commit()
        add_span_attribute("role_id", role_id)
        set_span_status("success")
        return {"message": "角色已删除"}
    except Exception as e:
        set_span_status("error")
        raise HTTPException(status_code=400, detail=str(e))

# 权限相关路由
@app.post("/permissions/", response_model=schemas.Permission)
@create_span("create_permission")
async def create_permission(permission: schemas.PermissionCreate, db: Session = Depends(get_db)):
    """创建权限"""
    try:
        db_permission = models.Permission(**permission.dict())
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)
        add_span_attribute("permission_id", db_permission.id)
        set_span_status("success")
        return db_permission
    except Exception as e:
        set_span_status("error")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/permissions/", response_model=List[schemas.Permission])
@create_span("list_permissions")
async def list_permissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取权限列表"""
    try:
        permissions = db.query(models.Permission).offset(skip).limit(limit).all()
        add_span_attribute("count", len(permissions))
        set_span_status("success")
        return permissions
    except Exception as e:
        set_span_status("error")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/permissions/{permission_id}", response_model=schemas.Permission)
@create_span("get_permission")
async def get_permission(permission_id: int, db: Session = Depends(get_db)):
    """获取权限详情"""
    try:
        permission = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
        if not permission:
            raise HTTPException(status_code=404, detail="权限不存在")
        add_span_attribute("permission_id", permission_id)
        set_span_status("success")
        return permission
    except Exception as e:
        set_span_status("error")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/permissions/{permission_id}", response_model=schemas.Permission)
@create_span("update_permission")
async def update_permission(permission_id: int, permission: schemas.PermissionUpdate, db: Session = Depends(get_db)):
    """更新权限"""
    try:
        db_permission = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
        if not db_permission:
            raise HTTPException(status_code=404, detail="权限不存在")
        
        for key, value in permission.dict(exclude_unset=True).items():
            setattr(db_permission, key, value)
        
        db_permission.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_permission)
        add_span_attribute("permission_id", permission_id)
        set_span_status("success")
        return db_permission
    except Exception as e:
        set_span_status("error")
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/permissions/{permission_id}")
@create_span("delete_permission")
async def delete_permission(permission_id: int, db: Session = Depends(get_db)):
    """删除权限"""
    try:
        db_permission = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
        if not db_permission:
            raise HTTPException(status_code=404, detail="权限不存在")
        
        db.delete(db_permission)
        db.commit()
        add_span_attribute("permission_id", permission_id)
        set_span_status("success")
        return {"message": "权限已删除"}
    except Exception as e:
        set_span_status("error")
        raise HTTPException(status_code=400, detail=str(e)) 