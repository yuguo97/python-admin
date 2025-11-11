"""
服务管理器
用于管理微服务的启动、停止和状态检查
"""

import os
import sys
import subprocess
import psutil
import json
from typing import Dict, Optional, List
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger("service_manager", "service_manager")

# 服务进程信息存储文件
PID_FILE = Path(__file__).parent.parent / "service_pids.json"


class ServiceManager:
    """服务管理器"""
    
    def __init__(self):
        self.service_config = {
            "system": {
                "module": "system_service.app.main:app",
                "port": int(os.getenv("SYSTEM_SERVICE_PORT", 8002)),
                "name": "System Service",
                "description": "系统信息服务"
            },
            "crawler": {
                "module": "crawler_service.app.main:app",
                "port": int(os.getenv("CRAWLER_SERVICE_PORT", 8001)),
                "name": "Crawler Service",
                "description": "爬虫服务"
            },
            "ai": {
                "module": "ai_service.app.main:app",
                "port": int(os.getenv("AI_SERVICE_PORT", 8003)),
                "name": "AI Service",
                "description": "AI服务"
            },
            "gateway": {
                "module": "gateway_service.app.main:app",
                "port": int(os.getenv("GATEWAY_SERVICE_PORT", 8999)),
                "name": "Gateway Service",
                "description": "网关服务"
            }
        }
        self.project_root = Path(__file__).parent.parent.parent
    
    def _load_pids(self) -> Dict[str, int]:
        """加载已保存的进程ID"""
        if PID_FILE.exists():
            try:
                with open(PID_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载PID文件失败: {e}")
        return {}
    
    def _save_pids(self, pids: Dict[str, int]):
        """保存进程ID到文件"""
        try:
            with open(PID_FILE, 'w') as f:
                json.dump(pids, f, indent=2)
        except Exception as e:
            logger.error(f"保存PID文件失败: {e}")
    
    def _is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
        except (psutil.AccessDenied, PermissionError):
            # 权限不足时,尝试使用其他方法
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('0.0.0.0', port))
                    return False
                except OSError:
                    return True
        return False
    
    def _get_process_by_port(self, port: int) -> Optional[psutil.Process]:
        """根据端口获取进程"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return psutil.Process(conn.pid)
        except (psutil.AccessDenied, psutil.NoSuchProcess, PermissionError):
            pass
        return None
    
    def get_service_status(self, service_name: str) -> Dict:
        """获取服务状态"""
        if service_name not in self.service_config:
            raise ValueError(f"未知的服务: {service_name}")
        
        config = self.service_config[service_name]
        port = config["port"]
        
        # 检查端口是否被占用
        is_running = self._is_port_in_use(port)
        
        status = {
            "service_name": service_name,
            "name": config["name"],
            "port": port,
            "description": config["description"],
            "status": "running" if is_running else "stopped"
        }
        
        # 如果服务运行中,获取进程信息
        if is_running:
            process = self._get_process_by_port(port)
            if process:
                try:
                    status["pid"] = process.pid
                    status["cpu_percent"] = process.cpu_percent()
                    status["memory_mb"] = process.memory_info().rss / 1024 / 1024
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
        
        return status
    
    def get_all_services_status(self) -> List[Dict]:
        """获取所有服务状态"""
        services = []
        for service_name in self.service_config.keys():
            try:
                status = self.get_service_status(service_name)
                services.append(status)
            except Exception as e:
                logger.error(f"获取服务状态失败 {service_name}: {e}")
                services.append({
                    "service_name": service_name,
                    "name": self.service_config[service_name]["name"],
                    "port": self.service_config[service_name]["port"],
                    "description": self.service_config[service_name]["description"],
                    "status": "unknown",
                    "error": str(e)
                })
        return services
    
    def start_service(self, service_name: str) -> Dict:
        """启动服务

        如果 service 配置中包含外部管理器 (如 'manager' 与相关 'unit'/'program' 字段)，
        则尝试通过外部管理器启动（可配置）。否则使用本地 uvicorn 子进程启动。
        返回包含 status 字段 ("running"|"starting") 以及 port_free 布尔值的字典。
        """
        if service_name not in self.service_config:
            raise ValueError(f"未知的服务: {service_name}")
        
        config = self.service_config[service_name]
        port = config["port"]
        
        # 检查服务是否已经运行
        if self._is_port_in_use(port):
            raise RuntimeError(f"服务 {service_name} 已在运行中 (端口 {port} 已被占用)")
        
        # 如果配置了外部管理器, 使用它来启动
        manager = config.get("manager")
        if manager:
            # 示例: manager == "systemd" 并且 config 包含 'unit'
            try:
                if manager == "systemd" and config.get("unit"):
                    unit = config.get("unit")
                    subprocess.check_call(["systemctl", "start", unit])
                elif manager == "supervisor" and config.get("program"):
                    program = config.get("program")
                    subprocess.check_call(["supervisorctl", "start", program])
                # 仍然保存 a placeholder pid as None since external manager 管理PID
                pids = self._load_pids()
                pids[service_name] = None
                self._save_pids(pids)
                logger.info(f"已通过外部管理器 ({manager}) 发送启动命令: {service_name}")
                # 短等待并检测端口
                import time
                timeout = 5
                interval = 0.5
                start_time = time.time()
                started = False
                while time.time() - start_time < timeout:
                    if self._is_port_in_use(port):
                        started = True
                        break
                    time.sleep(interval)
                final_status = "running" if started else "starting"
                return {
                    "service_name": service_name,
                    "pid": None,
                    "port": port,
                    "status": final_status,
                    "port_free": not self._is_port_in_use(port)
                }
            except Exception as e:
                logger.error(f"通过外部管理器启动失败: {e}")
                raise RuntimeError(str(e))

        # 构建本地启动命令
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            config["module"],
            "--host", "0.0.0.0",
            "--port", str(port),
            "--log-level", "info"
        ]
        
        logger.info(f"启动服务: {service_name}, 命令: {' '.join(cmd)}")
        
        # 启动进程
        try:
            if sys.platform == "win32":
                # Windows: 使用 DETACHED_PROCESS 和 CREATE_NEW_PROCESS_GROUP
                DETACHED_PROCESS = 0x00000008
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                process = subprocess.Popen(
                    cmd,
                    cwd=str(self.project_root),
                    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
            else:
                # Linux/Mac: 使用 start_new_session
                process = subprocess.Popen(
                    cmd,
                    cwd=str(self.project_root),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            # 保存PID
            pids = self._load_pids()
            pids[service_name] = process.pid
            self._save_pids(pids)

            logger.info(f"服务启动命令已发送: {service_name} (PID: {process.pid})")

            # 等待端口被占用以确认服务已启动
            import time
            timeout = 5
            interval = 0.5
            start_time = time.time()
            started = False
            while time.time() - start_time < timeout:
                if self._is_port_in_use(port):
                    started = True
                    break
                time.sleep(interval)

            final_status = "running" if started else "starting"
            logger.info(f"服务 {service_name} 启动检测结果: {final_status}")

            return {
                "service_name": service_name,
                "pid": process.pid,
                "port": port,
                "status": final_status,
                "port_free": not self._is_port_in_use(port)
            }
            
        except Exception as e:
            logger.error(f"启动服务失败: {service_name}, 错误: {e}")
            raise RuntimeError(f"启动服务失败: {str(e)}")
    
    def stop_service(self, service_name: str, force: bool = False, operator: Optional[str] = None) -> Dict:
        """停止服务"""
        if service_name not in self.service_config:
            raise ValueError(f"未知的服务: {service_name}")
        
        config = self.service_config[service_name]
        port = config["port"]
        
        # 查找占用端口的进程
        process = self._get_process_by_port(port)
        
        if not process:
            # 尝试从保存的PID文件中查找
            pids = self._load_pids()
            if service_name in pids:
                try:
                    process = psutil.Process(pids[service_name])
                    if not process.is_running():
                        process = None
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process = None
        
        if not process:
            raise RuntimeError(f"服务 {service_name} 未运行")
        
        # 终止进程
        try:
            pid = process.pid
            logger.info(f"正在停止服务: {service_name} (PID: {pid}), force={force}, operator={operator}")
            
            # 先尝试优雅关闭
            process.terminate()
            
            # 等待进程结束
            try:
                process.wait(timeout=5)
            except psutil.TimeoutExpired:
                # 如果5秒后还没结束,根据 force 参数决定是否强制杀死
                if force:
                    logger.warning(f"服务 {service_name} 未响应,强制终止 (force=True)")
                    process.kill()
                    try:
                        process.wait(timeout=2)
                    except Exception:
                        pass
                else:
                    logger.warning(f"服务 {service_name} 未响应且未设置 force, 保留进程")
                    # 在未强制的情况下，将认为停止尝试未完成，抛出错误
                    raise RuntimeError(f"服务 {service_name} 未响应, 请重试或使用 force=true")
            
            # 从PID文件中移除
            pids = self._load_pids()
            if service_name in pids:
                del pids[service_name]
                self._save_pids(pids)
            
            logger.info(f"服务进程已终止: {service_name} (PID: {pid})")

            # 等待端口释放并检测是否被自动重启
            import time
            timeout = 5
            interval = 0.5
            start_time = time.time()
            while time.time() - start_time < timeout:
                if not self._is_port_in_use(port):
                    break
                time.sleep(interval)

            port_free = not self._is_port_in_use(port)

            # 如果端口未释放但 operator 请求了强制停止, 仍视为失败
            if not port_free:
                logger.warning(f"服务 {service_name} 停止后端口 {port} 仍被占用")
                # 检测是否为自动重启: 再观测短时间内是否持续被占用
                ar_start = time.time()
                auto_restarted = False
                while time.time() - ar_start < 3:
                    if self._is_port_in_use(port):
                        auto_restarted = True
                        break
                    time.sleep(0.5)

                if auto_restarted:
                    logger.warning(f"服务 {service_name} 可能被外部机制自动重启")
                    # 抛出带特定前缀的错误，便于上层识别为自动重启场景
                    raise RuntimeError(f"AUTO_RESTART: 服务 {service_name} 停止失败: 端口 {port} 被外部机制占用 (可能自动重启)")
                else:
                    # 明确端口占用错误代码
                    raise RuntimeError(f"PORT_OCCUPIED: 服务 {service_name} 停止失败: 端口 {port} 仍被占用")

            logger.info(f"服务已停止且端口已释放: {service_name} (PID: {pid})")

            return {
                "service_name": service_name,
                "pid": pid,
                "status": "stopped",
                "port_free": port_free
            }
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"停止服务失败: {service_name}, 错误: {e}")
            raise RuntimeError(f"停止服务失败: {str(e)}")
    
    def restart_service(self, service_name: str, force: bool = False, operator: Optional[str] = None) -> Dict:
        """重启服务

        支持传入 force 和 operator，便于在 stop 阶段执行强制终止并记录操作者。
        """
        logger.info(f"重启服务: {service_name}, force={force}, operator={operator}")

        # 先停止
        try:
            self.stop_service(service_name, force=force, operator=operator)
        except RuntimeError as e:
            if "未运行" not in str(e):
                raise

        # 等待一小段时间
        import time
        time.sleep(1)

        # 再启动
        return self.start_service(service_name)


# 创建全局实例
service_manager = ServiceManager()
