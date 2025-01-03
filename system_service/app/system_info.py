import psutil
import platform
import json
from datetime import datetime
from typing import Dict, Any
from .database import get_redis
from utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger("system_monitor", "system_monitor")

class SystemMonitor:
    """系统监控类"""
    
    def __init__(self):
        self.redis = None
        self.cache_ttl = 60  # 缓存过期时间（秒）

    def init_redis(self):
        """初始化Redis连接"""
        self.redis = get_redis()
        logger.info("Redis连接已初始化")

    def close_redis(self):
        """关闭Redis连接"""
        if self.redis:
            self.redis.close()
            self.redis = None
            logger.info("Redis连接已关闭")

    def get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        logger.debug("开始获取CPU信息")
        cache_key = "cpu_info"
        
        if self.redis:
            cached = self.redis.get(cache_key)
            if cached:
                logger.debug("返回CPU缓存信息")
                return json.loads(cached)

        info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else None,
            "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            "cpu_usage_per_core": [x for x in psutil.cpu_percent(percpu=True)],
            "total_cpu_usage": psutil.cpu_percent()
        }
        
        if self.redis:
            self.redis.setex(cache_key, self.cache_ttl, json.dumps(info))
            logger.debug("CPU信息已缓存")
        
        return info

    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        logger.debug("开始获取内存信息")
        cache_key = "memory_info"
        
        if self.redis:
            cached = self.redis.get(cache_key)
            if cached:
                logger.debug("返回内存缓存信息")
                return json.loads(cached)

        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        info = {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percentage": memory.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_free": swap.free,
            "swap_percentage": swap.percent
        }
        
        if self.redis:
            self.redis.setex(cache_key, self.cache_ttl, json.dumps(info))
            logger.debug("内存信息已缓存")
        
        return info

    def get_disk_info(self) -> Dict[str, Any]:
        """获取磁盘信息"""
        logger.debug("开始获取磁盘信息")
        cache_key = "disk_info"
        
        if self.redis:
            cached = self.redis.get(cache_key)
            if cached:
                logger.debug("返回磁盘缓存信息")
                return json.loads(cached)

        partitions = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "filesystem": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percentage": usage.percent
                })
                logger.debug(f"已获取分区信息: {partition.device}")
            except Exception as e:
                logger.warning(f"获取分区信息失败 {partition.device}: {str(e)}")
                continue
        
        info = {"partitions": partitions}
        if self.redis:
            self.redis.setex(cache_key, self.cache_ttl, json.dumps(info))
            logger.debug("磁盘信息已缓存")
        
        return info

    def get_network_info(self) -> Dict[str, Any]:
        """获取网络信息"""
        logger.debug("开始获取网络信息")
        cache_key = "network_info"
        
        if self.redis:
            cached = self.redis.get(cache_key)
            if cached:
                logger.debug("返回网络缓存信息")
                return json.loads(cached)

        info = {
            "interfaces": {},
            "connections": len(psutil.net_connections())
        }
        
        for interface_name, stats in psutil.net_io_counters(pernic=True).items():
            info["interfaces"][interface_name] = {
                "bytes_sent": stats.bytes_sent,
                "bytes_recv": stats.bytes_recv,
                "packets_sent": stats.packets_sent,
                "packets_recv": stats.packets_recv,
                "errors_in": stats.errin,
                "errors_out": stats.errout
            }
            logger.debug(f"已获取网络接口信息: {interface_name}")
        
        if self.redis:
            self.redis.setex(cache_key, self.cache_ttl, json.dumps(info))
            logger.debug("网络信息已缓存")
        
        return info

    def get_system_info(self) -> Dict[str, Any]:
        """获取完整的系统信息
        Returns:
            Dict: 包含系统、CPU、内存、磁盘和网络的完整信息
        """
        return {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info()
        } 

    def get_process_info(self, limit: int = 10) -> Dict[str, Any]:
        """获取进程信息
        
        Args:
            limit: 返回的进程数量
            
        Returns:
            Dict: 进程信息，包含：
                - processes: 进程列表
                - total: 总进程数
        """
        logger.debug(f"获取进程信息: limit={limit}")
        processes = []
        for proc in sorted(
            psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
            key=lambda p: p.info['cpu_percent'],
            reverse=True
        )[:limit]:
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            'processes': processes,
            'total': len(psutil.pids())
        }

    def check_service_status(self, service: str, port: int) -> Dict[str, Any]:
        """检查服务状态
        
        Args:
            service: 服务名称
            port: 服务端口
            
        Returns:
            Dict: 服务状态信息
        """
        logger.debug(f"检查服务状态: {service}:{port}")
        import socket
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        return {
            'service': service,
            'port': port,
            'status': 'running' if result == 0 else 'stopped',
            'timestamp': datetime.now().isoformat()
        } 