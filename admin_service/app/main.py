from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .auth.router import router as auth_router
from .users.router import router as users_router
from .menus.router import router as menus_router
from utils.logger import setup_logger
from utils.response import server_error
from utils.auth import verify_token

# 设置日志记录器
logger = setup_logger("admin_service", "admin")

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="后台管理服务",
    description="""
    提供用户管理和菜单管理功能的后台服务。
    
    ## 功能模块
    * 认证管理 - 用户登录、令牌管理
    * 用户管理 - 用户的增删改查
    * 菜单管理 - 系统菜单配置
    """,
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

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
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"全局异常: {str(exc)}")
    return server_error(f"服务器内部错误: {str(exc)}")

# 注册路由
# 认证路由 - 不需要token验证
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["认证管理"]
)

# 需要token验证的路由
app.include_router(
    users_router,
    prefix="/users",
    tags=["用户管理"],
    dependencies=[Depends(verify_token)]
)

app.include_router(
    menus_router,
    prefix="/menus",
    tags=["菜单管理"],
    dependencies=[Depends(verify_token)]
) 