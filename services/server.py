import uvicorn
import multiprocessing
import signal
import sys
import os
import time
from typing import Dict
from . import SERVICES
from utils.logger import setup_logger

logger = setup_logger("server", "server")

class ServiceManager:
    """服务管理器"""
    def __init__(self):
        self.processes: Dict[str, multiprocessing.Process] = {}
        self.should_exit = False
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

    def handle_signal(self, signum, frame):
        """处理终止信号"""
        logger.info("接收到终止信号，准备关闭服务...")
        self.should_exit = True
        self.stop_all()

    def start_service(self, name: str, config: dict):
        """启动服务进程"""
        logger.info(f"启动 {config['name']}...")
        
        process = multiprocessing.Process(
            target=uvicorn.run,
            kwargs={
                "app": config["module"],
                "host": config["host"],
                "port": config["port"],
                "reload": True
            }
        )
        process.start()
        self.processes[name] = process
        logger.info(f"{config['name']}已启动，进程ID: {process.pid}")

    def start_all(self):
        """启动所有服务"""
        try:
            # 确保日志目录存在
            os.makedirs("logs", exist_ok=True)
            
            # 启动所有服务
            for name, config in SERVICES.items():
                self.start_service(name, config)

            # 持续监控进程状态
            while not self.should_exit:
                all_running = True
                for name, process in list(self.processes.items()):
                    if not process.is_alive():
                        logger.error(f"{SERVICES[name]['name']}已停止，正在重启...")
                        # 重启服务
                        self.start_service(name, SERVICES[name])
                        all_running = False
                
                if not all_running:
                    logger.info("部分服务已重启")
                
                time.sleep(5)  # 每5秒检查一次

        except KeyboardInterrupt:
            logger.info("接收到终止信号")
            self.stop_all()
        except Exception as e:
            logger.error(f"服务启动失败: {str(e)}")
            self.stop_all()

    def stop_all(self):
        """停止所有服务"""
        for name, process in self.processes.items():
            if process.is_alive():  # 进程仍在运行
                logger.info(f"正在停止 {SERVICES[name]['name']}...")
                process.terminate()
                process.join(timeout=5)  # 等待最多5秒
                logger.info(f"{SERVICES[name]['name']}已停止")

def run_all():
    """运行所有服务"""
    manager = ServiceManager()
    manager.start_all()

def run_service(service_name: str):
    """运行单个服务"""
    if service_name not in SERVICES:
        logger.error(f"服务 {service_name} 不存在")
        return
    
    service = SERVICES[service_name]
    logger.info(f"启动 {service['name']}...")
    
    uvicorn.run(
        app=service["module"],
        host=service["host"],
        port=service["port"],
        reload=True
    )

if __name__ == "__main__":
    run_all() 