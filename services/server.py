"""服务启动模块"""

import os
import sys
import signal
import multiprocessing
from typing import Dict, List
from utils.logger import setup_logger
from utils.config import SERVICE_CONFIG

# 设置日志记录器
logger = setup_logger("server", "server")

# 服务映射
SERVICES = {
    "admin": ("admin_service.app.main:app", SERVICE_CONFIG["admin_port"]),
    "crawler": ("crawler_service.app.main:app", SERVICE_CONFIG["crawler_port"]),
    "system": ("system_service.app.main:app", SERVICE_CONFIG["system_port"]),
    "ai": ("ai_service.app.main:app", SERVICE_CONFIG["ai_port"]),
    "gateway": ("gateway_service.app.main:app", SERVICE_CONFIG["gateway_port"]),
}

def run_service(service_name: str) -> None:
    """运行单个服务
    
    Args:
        service_name: 服务名称
    """
    if service_name not in SERVICES:
        logger.error(f"未知的服务名称: {service_name}")
        sys.exit(1)
        
    app_path, port = SERVICES[service_name]
    logger.info(f"启动服务: {service_name}, 端口: {port}")
    
    try:
        import uvicorn
        uvicorn.run(
            app_path,
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=True
        )
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        sys.exit(1)

def run_all() -> None:
    """运行所有服务"""
    processes: Dict[str, multiprocessing.Process] = {}
    
    def signal_handler(signum, frame):
        """信号处理函数"""
        logger.info("收到终止信号，正在关闭所有服务...")
        for name, process in processes.items():
            if process.is_alive():
                logger.info(f"正在关闭服务: {name}")
                process.terminate()
                process.join()
        sys.exit(0)
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 启动所有服务
        for name, (app_path, port) in SERVICES.items():
            logger.info(f"启动服务: {name}, 端口: {port}")
            process = multiprocessing.Process(
                target=run_service,
                args=(name,)
            )
            process.start()
            processes[name] = process
            
        # 等待所有进程结束
        for process in processes.values():
            process.join()
            
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        # 关闭所有已启动的服务
        for name, process in processes.items():
            if process.is_alive():
                logger.info(f"正在关闭服务: {name}")
                process.terminate()
                process.join()
        sys.exit(1)

if __name__ == "__main__":
    try:
        # 设置多进程启动方式
        if sys.platform == "win32":
            multiprocessing.set_start_method("spawn", force=True)
        else:
            multiprocessing.set_start_method("fork", force=True)
        run_all()
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        sys.exit(1) 