import uvicorn
import subprocess
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
        self.processes: Dict[str, subprocess.Popen] = {}
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
        cmd = [
            sys.executable,
            "-m", "uvicorn",
            config["module"],
            "--host", config["host"],
            "--port", str(config["port"]),
            "--reload",
            "--reload-dir", "./admin_service",
            "--reload-dir", "./crawler_service",
            "--reload-dir", "./system_service",
            "--reload-include", "*.py",
            "--log-level", "info"
        ]
        
        # 创建日志文件
        log_path = f"logs/{name}.log"
        log_file = open(log_path, "a", encoding="utf-8", buffering=1)  # 行缓冲
        
        # 使用 subprocess.Popen 捕获输出
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            universal_newlines=True,  # 使用文本模式
            bufsize=1,  # 行缓冲
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 设置工作目录为项目根目录
        )
        
        # 创建输出监控线程
        def monitor_output(pipe, log_file, prefix):
            try:
                for line in pipe:
                    # 写入日志文件
                    log_file.write(line)
                    log_file.flush()
                    # 输出到控制台
                    sys.stdout.write(f"[{name}] {line}")
                    sys.stdout.flush()
            except Exception as e:
                logger.error(f"输出监控错误: {str(e)}")

        import threading
        threading.Thread(target=monitor_output, args=(process.stdout, log_file, ""), daemon=True).start()
        threading.Thread(target=monitor_output, args=(process.stderr, log_file, "ERROR: "), daemon=True).start()

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
                    if process.poll() is not None:
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
            if process.poll() is None:  # 进程仍在运行
                logger.info(f"正在停止 {SERVICES[name]['name']}...")
                try:
                    process.terminate()
                    process.wait(timeout=5)  # 等待最多5秒
                except subprocess.TimeoutExpired:
                    process.kill()  # 如果进程没有及时退出，强制结束
                logger.info(f"{SERVICES[name]['name']}已停止")

def run_all():
    """运行所有服务"""
    manager = ServiceManager()
    manager.start_all()

def run_service(service_name: str):
    """运行单个服务"""
    if service_name not in SERVICES:
        logger.error(f"未知服务: {service_name}")
        sys.exit(1)

    config = SERVICES[service_name]
    try:
        logger.info(f"启动 {config['name']}...")
        uvicorn.run(
            app=config["module"],
            host=config["host"],
            port=config["port"],
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_all() 