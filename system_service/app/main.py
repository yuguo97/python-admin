""" 系统监控服务主应用 """

from fastapi import FastAPI, Request, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from . import system_info
from .device_service import DeviceService
from .models import DeviceReportData, DeviceQuery
from .database import init_db
from utils.logger import setup_logger
from utils.response import (
    success_response, error_response, server_error
)
from utils.auth import verify_token
from utils.tracing import init_tracing, create_span, add_span_attribute, set_span_status, end_span
from opentelemetry.trace import StatusCode

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

# 初始化链路追踪
init_tracing(app, "system-service")

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
    await init_db()
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
    with create_span("get_system_info") as span:
        logger.info("获取系统完整信息")
        try:
            info = monitor.get_system_info()
            logger.info("系统信息获取成功")
            add_span_attribute(span, "system.info", "success")
            set_span_status(span, StatusCode.OK)
            return success_response(info)
        except Exception as e:
            logger.error(f"获取系统信息失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error("获取系统信息失败")


        # 健康检查端点（供网关或外部监控使用）
        @app.get("/health", include_in_schema=False)
        async def health_check():
            """简单的健康检查接口，返回服务可用状态"""
            return success_response({"status": "ok"})

@app.get("/system/cpu")
async def get_cpu_info(_: dict = Depends(verify_token)):
    """获取CPU信息"""
    with create_span("get_cpu_info") as span:
        logger.info("获取CPU信息")
        try:
            info = monitor.get_cpu_info()
            logger.info(f"CPU使用率: {info['total_cpu_usage']}%")
            add_span_attribute(span, "cpu.usage", f"{info['total_cpu_usage']}%")
            set_span_status(span, StatusCode.OK)
            return success_response(info)
        except Exception as e:
            logger.error(f"获取CPU信息失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error("获取CPU信息失败")

@app.get("/system/memory")
async def get_memory_info(_: dict = Depends(verify_token)):
    """获取内存信息"""
    with create_span("get_memory_info") as span:
        logger.info("获取内存信息")
        try:
            info = monitor.get_memory_info()
            logger.info(f"内存使用率: {info['percentage']}%")
            add_span_attribute(span, "memory.usage", f"{info['percentage']}%")
            set_span_status(span, StatusCode.OK)
            return success_response(info)
        except Exception as e:
            logger.error(f"获取内存信息失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error("获取内存信息失败")

@app.get("/system/disk")
async def get_disk_info(_: dict = Depends(verify_token)):
    """获取磁盘信息"""
    with create_span("get_disk_info") as span:
        logger.info("获取磁盘信息")
        try:
            info = monitor.get_disk_info()
            logger.info(f"获取到 {len(info['partitions'])} 个分区信息")
            add_span_attribute(span, "disk.partitions", str(len(info['partitions'])))
            set_span_status(span, StatusCode.OK)
            return success_response(info)
        except Exception as e:
            logger.error(f"获取磁盘信息失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error("获取磁盘信息失败")

@app.get("/system/network")
async def get_network_info(_: dict = Depends(verify_token)):
    """获取网络信息"""
    with create_span("get_network_info") as span:
        logger.info("获取网络信息")
        try:
            info = monitor.get_network_info()
            logger.info(f"当前网络连接数: {info['connections']}")
            add_span_attribute(span, "network.connections", str(info['connections']))
            set_span_status(span, StatusCode.OK)
            return success_response(info)
        except Exception as e:
            logger.error(f"获取网络信息失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error("获取网络信息失败")

@app.get("/system/processes")
async def get_process_info(limit: int = 10, _: dict = Depends(verify_token)):
    """获取进程信息"""
    with create_span("get_process_info") as span:
        logger.info(f"获取进程信息, limit={limit}")
        try:
            info = monitor.get_process_info(limit)
            logger.info(f"获取到 {len(info['processes'])} 个进程信息")
            add_span_attribute(span, "processes.count", str(len(info['processes'])))
            set_span_status(span, StatusCode.OK)
            return success_response(info)
        except Exception as e:
            logger.error(f"获取进程信息失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error("获取进程信息失败")

@app.get("/system/services")
async def get_service_status(_: dict = Depends(verify_token)):
    """获取服务状态"""
    with create_span("get_service_status") as span:
        logger.info("获取服务状态")
        try:
            info = {
                "admin_service": monitor.check_service_status("admin", 8000),
                "crawler_service": monitor.check_service_status("crawler", 8001),
                "system_service": monitor.check_service_status("system", 8002)
            }
            add_span_attribute(span, "services.status", str(info))
            set_span_status(span, StatusCode.OK)
            return success_response(info)
        except Exception as e:
            logger.error(f"获取服务状态失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error("获取服务状态失败")


# ==================== 设备管理API ====================

@app.post("/devices/report")
async def report_device(report: DeviceReportData, _: dict = Depends(verify_token)):
    """
    接收设备上报数据
    
    Agent脚本调用此接口上报设备配置信息
    """
    with create_span("report_device") as span:
        logger.info(f"接收设备上报: {report.device_id}")
        try:
            success = await DeviceService.save_device_report(report)
            
            if success:
                add_span_attribute(span, "device.id", report.device_id)
                add_span_attribute(span, "device.hostname", report.os.hostname)
                set_span_status(span, StatusCode.OK)
                return success_response({"message": "设备信息上报成功"})
            else:
                set_span_status(span, StatusCode.ERROR, "保存失败")
                return server_error("设备信息保存失败")
                
        except Exception as e:
            logger.error(f"处理设备上报失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error(f"处理设备上报失败: {str(e)}")


@app.post("/devices/query")
async def query_devices(query: DeviceQuery = Body(...), _: dict = Depends(verify_token)):
    """
    查询设备列表
    
    支持按设备ID、主机名、操作系统、IP地址等条件查询
    """
    with create_span("query_devices") as span:
        logger.info(f"查询设备列表: page={query.page}, page_size={query.page_size}")
        try:
            result = await DeviceService.query_devices(query)
            
            add_span_attribute(span, "devices.count", str(result["total"]))
            set_span_status(span, StatusCode.OK)
            return success_response(result)
            
        except Exception as e:
            logger.error(f"查询设备列表失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error(f"查询设备列表失败: {str(e)}")


@app.get("/devices/{device_id}")
async def get_device_detail(device_id: str, _: dict = Depends(verify_token)):
    """
    获取设备详情
    
    返回指定设备的完整配置信息
    """
    with create_span("get_device_detail") as span:
        logger.info(f"获取设备详情: {device_id}")
        try:
            device = await DeviceService.get_device_detail(device_id)
            
            if device:
                add_span_attribute(span, "device.found", "true")
                set_span_status(span, StatusCode.OK)
                return success_response(device)
            else:
                add_span_attribute(span, "device.found", "false")
                set_span_status(span, StatusCode.OK)
                return error_response("设备不存在", 404)
                
        except Exception as e:
            logger.error(f"获取设备详情失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error(f"获取设备详情失败: {str(e)}")


@app.get("/devices/statistics/summary")
async def get_device_statistics(_: dict = Depends(verify_token)):
    """
    获取设备统计信息
    
    包括总设备数、操作系统分布、CPU分布、内存分布、在线/离线设备数等
    """
    with create_span("get_device_statistics") as span:
        logger.info("获取设备统计信息")
        try:
            stats = await DeviceService.get_statistics()
            
            add_span_attribute(span, "total.devices", str(stats.total_devices))
            add_span_attribute(span, "online.devices", str(stats.online_devices))
            set_span_status(span, StatusCode.OK)
            return success_response(stats.dict())
            
        except Exception as e:
            logger.error(f"获取设备统计失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error(f"获取设备统计失败: {str(e)}")


@app.delete("/devices/{device_id}")
async def delete_device(device_id: str, _: dict = Depends(verify_token)):
    """
    删除设备记录
    
    从数据库中删除指定设备的记录
    """
    with create_span("delete_device") as span:
        logger.info(f"删除设备: {device_id}")
        try:
            success = await DeviceService.delete_device(device_id)
            
            if success:
                add_span_attribute(span, "device.deleted", "true")
                set_span_status(span, StatusCode.OK)
                return success_response({"message": "设备删除成功"})
            else:
                add_span_attribute(span, "device.deleted", "false")
                set_span_status(span, StatusCode.OK)
                return error_response("设备不存在", 404)
                
        except Exception as e:
            logger.error(f"删除设备失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error(f"删除设备失败: {str(e)}") 