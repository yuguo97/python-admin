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
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from admin_service.app import schemas
from admin_service.app import models
from admin_service.app.users.models import User
from admin_service.app.database import SessionLocal, get_db, engine, Base, init_db
from admin_service.app.auth.security import create_access_token, verify_password, authenticate_user, get_password_hash
from utils.logger import setup_logger
from utils.response import success_response, error_response, unauthorized_error, not_found_error, server_error
from utils.auth import verify_token
from utils.tracing import init_tracing, create_span, add_span_attribute, set_span_status, end_span
from opentelemetry.trace import StatusCode

# 设置日志记录器
logger = setup_logger("admin_service", "admin")

# 导入所有模型以注册到 Base.metadata (避免重复定义)
from admin_service.app.users.models import User
from admin_service.app.menus.models import Menu
# 导入其他模型 (Role, Permission等)
from admin_service.app.models import Role, Permission, user_roles

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
            user = authenticate_user(db, form_data.username, form_data.password)
            if not user:
                logger.warning(f"登录失败: 用户名或密码错误 - {form_data.username}")
                add_span_attribute(span, "login.status", "failed")
                set_span_status(span, StatusCode.ERROR, "用户名或密码错误")
                return unauthorized_error("用户名或密码错误")
            
            access_token_expires = timedelta(days=7)
            access_token = create_access_token(
                data={"sub": str(user.id)}, expires_delta=access_token_expires
            )
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
@app.get("/users/me")
async def get_current_user_info(db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
    """获取当前用户信息"""
    try:
        user_id = token_data.get("sub")
        if not user_id:
            return unauthorized_error("无效的令牌")
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            return not_found_error("用户不存在")
        
        user_dict = user.to_dict()
        
        # 获取用户的菜单权限
        menu_codes = []
        for role in user.roles:
            if role.code == "fcadmin":
                # 超级管理员拥有所有菜单权限 - 从数据库动态查询
                from admin_service.app.menus.models import Menu
                all_menus = db.query(Menu).all()
                if all_menus:
                    menu_codes = [menu.code for menu in all_menus]
                else:
                    # 如果数据库没有菜单，使用默认菜单编码
                    menu_codes = ["dashboard", "system", "system:user", "system:role", "system:permission", "system:menu", "system:service"]
                break
            else:
                # 查询角色的菜单权限
                sql = text("SELECT menu_code FROM role_menus WHERE role_id = :role_id")
                result = db.execute(sql, {"role_id": role.id})
                menu_codes.extend([row[0] for row in result])
        
        # 去重
        menu_codes = list(set(menu_codes))
        user_dict["menu_codes"] = menu_codes
        
        # 从数据库读取所有可见菜单
        all_db_menus = db.query(Menu).filter(Menu.visible == 1, Menu.component.isnot(None)).order_by(Menu.sort_order).all()
        
        # 转换为前端需要的格式
        all_menus = []
        for menu in all_db_menus:
            # 生成路由名称 (首字母大写驼峰)
            name_parts = menu.code.replace(":", "_").split("_")
            route_name = "".join([part.capitalize() for part in name_parts])
            
            # 获取父级code
            parent_code = None
            if menu.parent_id:
                parent_menu = db.query(Menu).filter(Menu.id == menu.parent_id).first()
                if parent_menu:
                    parent_code = parent_menu.code
            
            menu_item = {
                "path": menu.path.lstrip("/"),  # 移除开头的/
                "name": route_name,
                "component": menu.component,
                "meta": {
                    "title": menu.name,
                    "icon": menu.icon or "Document",
                    "menuCode": menu.code
                }
            }
            
            if parent_code:
                menu_item["meta"]["parent"] = parent_code
            
            all_menus.append(menu_item)
        
        # 如果数据库没有菜单,使用默认菜单
        if not all_menus:
            all_menus = [
            {
                "path": "/dashboard",
                "name": "Dashboard",
                "component": "Dashboard",
                "meta": {
                    "title": "首页",
                    "icon": "HomeFilled",
                    "menuCode": "dashboard"
                }
            },
            {
                "path": "/system/users",
                "name": "SystemUsers",
                "component": "system/Users",
                "meta": {
                    "title": "用户管理",
                    "icon": "User",
                    "menuCode": "system:user",
                    "parent": "system"
                }
            },
            {
                "path": "/system/roles",
                "name": "SystemRoles",
                "component": "system/Roles",
                "meta": {
                    "title": "角色管理",
                    "icon": "UserFilled",
                    "menuCode": "system:role",
                    "parent": "system"
                }
            },
            {
                "path": "/system/permissions",
                "name": "SystemPermissions",
                "component": "system/Permissions",
                "meta": {
                    "title": "权限管理",
                    "icon": "Lock",
                    "menuCode": "system:permission",
                    "parent": "system"
                }
            },
            {
                "path": "/system/menus",
                "name": "SystemMenus",
                "component": "system/Menus",
                "meta": {
                    "title": "菜单管理",
                    "icon": "Menu",
                    "menuCode": "system:menu",
                    "parent": "system"
                }
            },
            {
                "path": "/system/services",
                "name": "SystemServices",
                "component": "system/Services",
                "meta": {
                    "title": "服务管理",
                    "icon": "Monitor",
                    "menuCode": "system:service",
                    "parent": "system"
                }
            }
        ]
        
        # 根据权限过滤菜单
        filtered_menus = [menu for menu in all_menus if menu["meta"]["menuCode"] in menu_codes]
        user_dict["menus"] = filtered_menus
        
        return success_response(user_dict)
    except Exception as e:
        logger.error(f"获取当前用户信息失败: {str(e)}")
        return server_error("获取当前用户信息失败")

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
            db_user = db.query(User).filter(User.username == user.username).first()
            if db_user:
                logger.warning(f"创建用户失败: 用户名已存在 - {user.username}")
                add_span_attribute(span, "user.exists", "true")
                set_span_status(span, StatusCode.ERROR, "用户名已存在")
                return error_response("用户名已存在", status_code=400)
            
            # 创建新用户
            new_user = User(
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                hashed_password=get_password_hash(user.password),
                is_active=user.is_active,
                is_superuser=user.is_superuser
            )
            db.add(new_user)
            db.flush()  # 获取用户ID但不提交
            
            # 关联角色
            if user.role_ids:
                for role_id in user.role_ids:
                    role = db.query(models.Role).filter(models.Role.id == role_id).first()
                    if role:
                        new_user.roles.append(role)
            
            db.commit()
            db.refresh(new_user)
            
            logger.info(f"用户创建成功: {user.username}")
            add_span_attribute(span, "user.id", str(new_user.id))
            set_span_status(span, StatusCode.OK)
            return success_response(new_user.to_dict())
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
            users = db.query(User).offset(skip).limit(limit).all()
            total = db.query(User).count()
            logger.info(f"获取到 {len(users)} 个用户")
            add_span_attribute(span, "users.count", str(len(users)))
            set_span_status(span, StatusCode.OK)
            return success_response({
                "items": [user.to_dict() for user in users],
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
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"用户不存在: {user_id}")
                add_span_attribute(span, "user.exists", "false")
                set_span_status(span, StatusCode.ERROR, "用户不存在")
                return not_found_error(f"用户不存在: {user_id}")
            
            logger.info(f"获取用户详情成功: {user.username}")
            add_span_attribute(span, "username", user.username)
            set_span_status(span, StatusCode.OK)
            return success_response(user.to_dict())
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
            db_user = db.query(User).filter(User.id == user_id).first()
            if not db_user:
                logger.warning(f"用户不存在: {user_id}")
                add_span_attribute(span, "user.exists", "false")
                set_span_status(span, StatusCode.ERROR, "用户不存在")
                return not_found_error(f"用户不存在: {user_id}")
            
            # 更新用户信息
            update_data = user.dict(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
            # 处理角色关联
            if "role_ids" in update_data:
                role_ids = update_data.pop("role_ids")
                db_user.roles.clear()
                if role_ids:
                    for role_id in role_ids:
                        role = db.query(models.Role).filter(models.Role.id == role_id).first()
                        if role:
                            db_user.roles.append(role)
            
            for key, value in update_data.items():
                setattr(db_user, key, value)
            
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"用户信息更新成功: {db_user.username}")
            add_span_attribute(span, "username", db_user.username)
            set_span_status(span, StatusCode.OK)
            return success_response(db_user.to_dict())
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
            db_user = db.query(User).filter(User.id == user_id).first()
            if not db_user:
                logger.warning(f"用户不存在: {user_id}")
                add_span_attribute(span, "user.exists", "false")
                set_span_status(span, StatusCode.ERROR, "用户不存在")
                return not_found_error(f"用户不存在: {user_id}")
            
            db.delete(db_user)
            db.commit()
            
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
@app.post("/roles/")
async def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    """创建角色"""
    try:
        # 禁止创建超级管理员角色
        if role.code == "fcadmin":
            return error_response("不能创建超级管理员角色", status_code=400)
        
        # 检查角色编码是否已存在
        existing_role = db.query(models.Role).filter(models.Role.code == role.code).first()
        if existing_role:
            return error_response("角色编码已存在", status_code=400)
        
        db_role = models.Role(**role.dict())
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return success_response(db_role.to_dict())
    except Exception as e:
        db.rollback()
        logger.error(f"创建角色失败: {str(e)}")
        return server_error(f"创建角色失败: {str(e)}")

@app.get("/roles/")
async def list_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取角色列表"""
    try:
        roles = db.query(models.Role).offset(skip).limit(limit).all()
        return success_response([role.to_dict() for role in roles])
    except Exception as e:
        logger.error(f"获取角色列表失败: {str(e)}")
        return server_error("获取角色列表失败")

@app.get("/roles/{role_id}")
async def get_role(role_id: int, db: Session = Depends(get_db)):
    """获取角色详情"""
    try:
        role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if not role:
            return not_found_error("角色不存在")
        return success_response(role.to_dict())
    except Exception as e:
        logger.error(f"获取角色详情失败: {str(e)}")
        return server_error("获取角色详情失败")

@app.put("/roles/{role_id}")
async def update_role(role_id: int, role: schemas.RoleUpdate, db: Session = Depends(get_db)):
    """更新角色"""
    try:
        db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if not db_role:
            return not_found_error("角色不存在")
        
        # 禁止修改超级管理员角色的编码
        if db_role.code == "fcadmin":
            update_data = role.dict(exclude_unset=True)
            if "code" in update_data and update_data["code"] != "fcadmin":
                return error_response("不能修改超级管理员角色编码", status_code=400)
        
        # 如果更新编码,检查是否重复
        update_data = role.dict(exclude_unset=True)
        if "code" in update_data and update_data["code"] != db_role.code:
            existing = db.query(models.Role).filter(models.Role.code == update_data["code"]).first()
            if existing:
                return error_response("角色编码已存在", status_code=400)
        
        for key, value in update_data.items():
            setattr(db_role, key, value)
        
        db_role.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_role)
        return success_response(db_role.to_dict())
    except Exception as e:
        db.rollback()
        logger.error(f"更新角色失败: {str(e)}")
        return server_error("更新角色失败")

@app.delete("/roles/{role_id}")
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    """删除角色"""
    try:
        db_role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if not db_role:
            return not_found_error("角色不存在")
        
        # 禁止删除超级管理员角色
        if db_role.code == "fcadmin":
            return error_response("不能删除超级管理员角色", status_code=400)
        
        db.delete(db_role)
        db.commit()
        return success_response({"message": "角色已删除"})
    except Exception as e:
        logger.error(f"删除角色失败: {str(e)}")
        return server_error("删除角色失败")

# 权限相关路由
@app.post("/permissions/")
async def create_permission(permission: schemas.PermissionCreate, db: Session = Depends(get_db)):
    """创建权限"""
    try:
        db_permission = models.Permission(**permission.dict())
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)
        return success_response(db_permission.to_dict())
    except Exception as e:
        db.rollback()
        logger.error(f"创建权限失败: {str(e)}")
        return server_error("创建权限失败")

@app.get("/permissions/")
async def list_permissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取权限列表"""
    try:
        permissions = db.query(models.Permission).offset(skip).limit(limit).all()
        return success_response([perm.to_dict() for perm in permissions])
    except Exception as e:
        logger.error(f"获取权限列表失败: {str(e)}")
        return server_error("获取权限列表失败")

@app.get("/permissions/{permission_id}")
async def get_permission(permission_id: int, db: Session = Depends(get_db)):
    """获取权限详情"""
    try:
        permission = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
        if not permission:
            return not_found_error("权限不存在")
        return success_response(permission.to_dict())
    except Exception as e:
        logger.error(f"获取权限详情失败: {str(e)}")
        return server_error("获取权限详情失败")

@app.put("/permissions/{permission_id}")
async def update_permission(permission_id: int, permission: schemas.PermissionUpdate, db: Session = Depends(get_db)):
    """更新权限"""
    try:
        db_permission = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
        if not db_permission:
            return not_found_error("权限不存在")
        
        for key, value in permission.dict(exclude_unset=True).items():
            setattr(db_permission, key, value)
        
        db_permission.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_permission)
        return success_response(db_permission.to_dict())
    except Exception as e:
        db.rollback()
        logger.error(f"更新权限失败: {str(e)}")
        return server_error("更新权限失败")

@app.delete("/permissions/{permission_id}")
async def delete_permission(permission_id: int, db: Session = Depends(get_db)):
    """删除权限"""
    try:
        db_permission = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
        if not db_permission:
            return not_found_error("权限不存在")
        
        db.delete(db_permission)
        db.commit()
        return success_response({"message": "权限已删除"})
    except Exception as e:
        logger.error(f"删除权限失败: {str(e)}")
        return server_error("删除权限失败")

# 角色菜单权限相关路由
@app.get("/roles/{role_id}/menus")
async def get_role_menus(role_id: int, db: Session = Depends(get_db)):
    """获取角色的菜单权限"""
    try:
        # 检查是否是超级管理员
        role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if role and role.code == "fcadmin":
            # 超级管理员拥有所有菜单权限 - 从数据库动态查询
            from admin_service.app.menus.models import Menu
            all_menus = db.query(Menu).all()
            if all_menus:
                # 从数据库获取所有菜单编码
                all_menu_codes = [menu.code for menu in all_menus]
            else:
                # 如果数据库没有菜单，使用默认菜单编码
                all_menu_codes = ["dashboard", "system", "system:user", "system:role", "system:permission", "system:menu", "system:service"]
            return success_response({"menu_codes": all_menu_codes, "is_super_admin": True})
        
        # 查询角色的菜单编码
        sql = text("SELECT menu_code FROM role_menus WHERE role_id = :role_id")
        result = db.execute(sql, {"role_id": role_id})
        menu_codes = [row[0] for row in result]
        return success_response({"menu_codes": menu_codes, "is_super_admin": False})
    except Exception as e:
        logger.error(f"获取角色菜单失败: {str(e)}")
        return server_error("获取角色菜单失败")

@app.post("/roles/{role_id}/menus")
async def update_role_menus(role_id: int, menu_data: dict, db: Session = Depends(get_db)):
    """更新角色的菜单权限"""
    try:
        # 检查是否是超级管理员
        role = db.query(models.Role).filter(models.Role.id == role_id).first()
        if role and role.code == "fcadmin":
            return error_response("超级管理员权限不可修改", status_code=400)
        
        menu_codes = menu_data.get("menu_codes", [])
        
        # 删除旧的权限
        delete_sql = text("DELETE FROM role_menus WHERE role_id = :role_id")
        db.execute(delete_sql, {"role_id": role_id})
        
        # 插入新的权限
        if menu_codes:
            for menu_code in menu_codes:
                insert_sql = text("INSERT INTO role_menus (role_id, menu_code) VALUES (:role_id, :menu_code)")
                db.execute(insert_sql, {"role_id": role_id, "menu_code": menu_code})
        
        db.commit()
        return success_response({"message": "权限更新成功"})
    except Exception as e:
        db.rollback()
        logger.error(f"更新角色菜单失败: {str(e)}")
        return server_error("更新角色菜单失败")

# 获取用户可见的菜单路由
@app.get("/user/menus")
async def get_user_menus(db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
    """获取当前用户可见的菜单路由"""
    try:
        user_id = token_data.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        # 获取用户的菜单权限
        menu_codes = []
        for role in user.roles:
            if role.code == "fcadmin":
                menu_codes = ["dashboard", "system", "system:user", "system:role", "system:permission", "system:menu"]
                break
            else:
                sql = text("SELECT menu_code FROM role_menus WHERE role_id = :role_id")
                result = db.execute(sql, {"role_id": role.id})
                menu_codes.extend([row[0] for row in result])
        
        menu_codes = list(set(menu_codes))
        
        # 返回菜单路由配置
        all_menus = [
            {
                "path": "/dashboard",
                "name": "Dashboard",
                "component": "Dashboard",
                "meta": {
                    "title": "首页",
                    "icon": "HomeFilled",
                    "menuCode": "dashboard"
                }
            },
            {
                "path": "/app/services",
                "name": "AppServices",
                "component": "app/Services",
                "meta": {
                    "title": "服务管理",
                    "icon": "Monitor",
                    "menuCode": "app:services",
                    "parent": "app"
                }
            },
            {
                "path": "/app/systeminfo",
                "name": "AppSystemInfo",
                "component": "app/SystemInfo",
                "meta": {
                    "title": "系统信息",
                    "icon": "DataAnalysis",
                    "menuCode": "app:systeminfo",
                    "parent": "app"
                }
            },
            {
                "path": "/system/users",
                "name": "SystemUsers",
                "component": "system/Users",
                "meta": {
                    "title": "用户管理",
                    "icon": "User",
                    "menuCode": "system:user",
                    "parent": "system"
                }
            },
            {
                "path": "/system/roles",
                "name": "SystemRoles",
                "component": "system/Roles",
                "meta": {
                    "title": "角色管理",
                    "icon": "UserFilled",
                    "menuCode": "system:role",
                    "parent": "system"
                }
            },
            {
                "path": "/system/permissions",
                "name": "SystemPermissions",
                "component": "system/Permissions",
                "meta": {
                    "title": "权限管理",
                    "icon": "Lock",
                    "menuCode": "system:permission",
                    "parent": "system"
                }
            },
            {
                "path": "/system/menus",
                "name": "SystemMenus",
                "component": "system/Menus",
                "meta": {
                    "title": "菜单管理",
                    "icon": "Menu",
                    "menuCode": "system:menu",
                    "parent": "system"
                }
            }
        ]
        
        # 根据权限过滤菜单
        filtered_menus = [menu for menu in all_menus if menu["meta"]["menuCode"] in menu_codes]
        
        return success_response(filtered_menus)
    except Exception as e:
        logger.error(f"获取用户菜单失败: {str(e)}")
        return server_error("获取用户菜单失败")

# 菜单相关路由
@app.get("/menus")
async def get_menus(db: Session = Depends(get_db), _: dict = Depends(verify_token)):
    """获取菜单列表"""
    try:
        # 从数据库读取菜单
        from admin_service.app.menus.models import Menu
        
        # 查询所有菜单
        all_menus = db.query(Menu).order_by(Menu.sort_order).all()
        
        # 构建菜单树
        menu_dict = {}
        root_menus = []
        
        # 第一遍：创建所有菜单项
        for menu in all_menus:
            menu_item = {
                "id": menu.id,
                "title": menu.name,
                "code": menu.code,
                "path": menu.path,
                "component": menu.component,
                "icon": menu.icon,
                "sort_order": menu.sort_order,
                "visible": bool(menu.visible),
                "parent_id": menu.parent_id,
                "created_at": menu.created_at.isoformat() if menu.created_at else None,
                "children": []
            }
            menu_dict[menu.id] = menu_item
            
            # 如果没有父菜单，加入根菜单列表
            if not menu.parent_id:
                root_menus.append(menu_item)
        
        # 第二遍：构建父子关系
        for menu in all_menus:
            if menu.parent_id and menu.parent_id in menu_dict:
                parent = menu_dict[menu.parent_id]
                parent["children"].append(menu_dict[menu.id])
        
        return success_response(root_menus)
    except Exception as e:
        logger.error(f"获取菜单列表失败: {str(e)}")
        return server_error("获取菜单列表失败")

# 服务管理相关路由
@app.get("/services")
async def get_services(_: dict = Depends(verify_token)):
    """获取所有服务状态"""
    try:
        import psutil
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        services = [
            {
                "id": 1,
                "name": "Admin Service",
                "service_name": "admin",
                "port": int(os.getenv("ADMIN_SERVICE_PORT", 8000)),
                "description": "后台管理服务",
                "status": "running"
            },
            {
                "id": 2,
                "name": "System Service",
                "service_name": "system",
                "port": int(os.getenv("SYSTEM_SERVICE_PORT", 8002)),
                "description": "系统信息服务",
                "status": "stopped"
            },
            {
                "id": 3,
                "name": "Crawler Service",
                "service_name": "crawler",
                "port": int(os.getenv("CRAWLER_SERVICE_PORT", 8001)),
                "description": "爬虫服务",
                "status": "stopped"
            },
            {
                "id": 4,
                "name": "AI Service",
                "service_name": "ai",
                "port": int(os.getenv("AI_SERVICE_PORT", 8003)),
                "description": "AI服务",
                "status": "stopped"
            }
        ]
        
        # 检查端口是否被占用来判断服务状态
        for service in services:
            port = service["port"]
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    service["status"] = "running"
                    break
        
        return success_response(services)
    except Exception as e:
        logger.error(f"获取服务列表失败: {str(e)}")
        return server_error("获取服务列表失败")

@app.post("/services/{service_name}/start")
async def start_service_endpoint(service_name: str, _: dict = Depends(verify_token)):
    """启动服务"""
    try:
        import subprocess
        import sys
        
        # 验证服务名称
        valid_services = ["admin", "system", "crawler", "ai", "gateway"]
        if service_name not in valid_services:
            return error_response(f"无效的服务名称: {service_name}", status_code=400)
        
        # 使用 manage.py 启动服务
        manage_py = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "manage.py")
        
        # 在后台启动服务
        if sys.platform == "win32":
            subprocess.Popen(
                [sys.executable, manage_py, "start", service_name],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            subprocess.Popen(
                [sys.executable, manage_py, "start", service_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        logger.info(f"服务启动命令已发送: {service_name}")
        return success_response({"message": f"服务 {service_name} 启动命令已发送"})
    except Exception as e:
        logger.error(f"启动服务失败: {str(e)}")
        return server_error(f"启动服务失败: {str(e)}")

@app.post("/services/{service_name}/stop")
async def stop_service_endpoint(service_name: str, _: dict = Depends(verify_token)):
    """停止服务"""
    try:
        import psutil
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # 验证服务名称
        valid_services = ["admin", "system", "crawler", "ai", "gateway"]
        if service_name not in valid_services:
            return error_response(f"无效的服务名称: {service_name}", status_code=400)
        
        # 不允许停止当前服务(admin)
        if service_name == "admin":
            return error_response("不能停止当前管理服务", status_code=400)
        
        # 获取服务端口
        port_map = {
            "system": int(os.getenv("SYSTEM_SERVICE_PORT", 8002)),
            "crawler": int(os.getenv("CRAWLER_SERVICE_PORT", 8001)),
            "ai": int(os.getenv("AI_SERVICE_PORT", 8003)),
            "gateway": int(os.getenv("GATEWAY_SERVICE_PORT", 8999))
        }
        
        port = port_map.get(service_name)
        if not port:
            return error_response(f"未找到服务端口: {service_name}", status_code=400)
        
        # 查找并终止占用该端口的进程
        killed = False
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                try:
                    process = psutil.Process(conn.pid)
                    process.terminate()
                    killed = True
                    logger.info(f"已终止服务进程: {service_name} (PID: {conn.pid})")
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.error(f"终止进程失败: {str(e)}")
        
        if killed:
            return success_response({"message": f"服务 {service_name} 已停止"})
        else:
            return error_response(f"服务 {service_name} 未运行", status_code=400)
    except Exception as e:
        logger.error(f"停止服务失败: {str(e)}")
        return server_error(f"停止服务失败: {str(e)}")