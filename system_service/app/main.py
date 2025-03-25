""" 系统监控服务主应用 """

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from . import system_info
from utils.logger import setup_logger
from utils.response import (
    success_response, error_response, server_error
)
from utils.auth import verify_token

# 设置日志记录器
logger = setup_logger("system_service", "system")

app = FastAPI(
    title="系统监控服务",
    description="""
    提供系统硬件和软件信息的监控服务。
    
    ## 功能特点
    * CPU信息监控
    * 内存使用监控
    * 磁盘使用监控
    * 网络状态监控
    * 进程监控
    * 服务状态监控
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
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
    )

monitor = system_info.SystemMonitor()

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"全局异常: {str(exc)}")
    return server_error(f"服务器内部错误: {str(exc)}")

@app.on_event("startup")
async def startup_event():
    """服务启动时初始化"""
    logger.info("初始化系统监控服务...")
    monitor.init_redis()
    logger.info("系统监控服务初始化完成")

@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时清理资源"""
    logger.info("关闭系统监控服务...")
    monitor.close_redis()
    logger.info("系统监控服务已关闭")

@app.get("/system")
async def get_system_info(_: dict = Depends(verify_token)):
    """获取完整的系统信息"""
    logger.info("获取系统完整信息")
    try:
        info = monitor.get_system_info()
        logger.info("系统信息获取成功")
        return success_response(info)
    except Exception as e:
        logger.error(f"获取系统信息失败: {str(e)}")
        return server_error("获取系统信息失败")

@app.get("/system/cpu")
async def get_cpu_info(_: dict = Depends(verify_token)):
    """获取CPU信息"""
    logger.info("获取CPU信息")
    try:
        info = monitor.get_cpu_info()
        logger.info(f"CPU使用率: {info['total_cpu_usage']}%")
        return success_response(info)
    except Exception as e:
        logger.error(f"获取CPU信息失败: {str(e)}")
        return server_error("获取CPU信息失败")

@app.get("/system/memory")
async def get_memory_info(_: dict = Depends(verify_token)):
    """获取内存信息"""
    logger.info("获取内存信息")
    try:
        info = monitor.get_memory_info()
        logger.info(f"内存使用率: {info['percentage']}%")
        return success_response(info)
    except Exception as e:
        logger.error(f"获取内存信息失败: {str(e)}")
        return server_error("获取内存信息失败")

@app.get("/system/disk")
async def get_disk_info(_: dict = Depends(verify_token)):
    """获取磁盘信息"""
    logger.info("获取磁盘信息")
    try:
        info = monitor.get_disk_info()
        logger.info(f"获取到 {len(info['partitions'])} 个分区信息")
        return success_response(info)
    except Exception as e:
        logger.error(f"获取磁盘信息失败: {str(e)}")
        return server_error("获取磁盘信息失败")

@app.get("/system/network")
async def get_network_info(_: dict = Depends(verify_token)):
    """获取网络信息"""
    logger.info("获取网络信息")
    try:
        info = monitor.get_network_info()
        logger.info(f"当前网络连接数: {info['connections']}")
        return success_response(info)
    except Exception as e:
        logger.error(f"获取网络信息失败: {str(e)}")
        return server_error("获取网络信息失败")

@app.get("/system/processes")
async def get_process_info(limit: int = 10, _: dict = Depends(verify_token)):
    """获取进程信息"""
    logger.info(f"获取进程信息, limit={limit}")
    try:
        info = monitor.get_process_info(limit)
        logger.info(f"获取到 {len(info['processes'])} 个进程信息")
        return success_response(info)
    except Exception as e:
        logger.error(f"获取进程信息失败: {str(e)}")
        return server_error("获取进程信息失败")

@app.get("/system/services")
async def get_service_status(_: dict = Depends(verify_token)):
    """获取服务状态"""
    logger.info("获取服务状态")
    try:
        info = {
            "admin_service": monitor.check_service_status("admin", 8000),
            "crawler_service": monitor.check_service_status("crawler", 8001),
            "system_service": monitor.check_service_status("system", 8002)
        }
        return success_response(info)
    except Exception as e:
        logger.error(f"获取服务状态失败: {str(e)}")
        return server_error("获取服务状态失败") 