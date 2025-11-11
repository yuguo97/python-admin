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
        info = {
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

        # 采集已安装软件（仅Windows）
        info["installed_software"] = self.get_installed_software() if platform.system() == "Windows" else []
        # 网卡信息
        info["network_cards"] = self.get_network_cards()
        # 主板序列号
        info["motherboard_serial"] = self.get_motherboard_serial()
        # CPU详细信息
        info["cpu_detail"] = self.get_cpu_detail()
        # 内存详细信息
        info["memory_detail"] = self.get_memory_detail()
        # 系统唯一标识符（UUID）
        info["system_uuid"] = self.get_system_uuid()
        return info

    def get_installed_software(self):
        """获取已安装软件列表（仅Windows）"""
        import subprocess
        try:
            # 注意: Windows 注册表路径中包含 "\U" 会被 Python 解释为 Unicode 转义序列，
            # 因此使用原始字符串或把反斜杠再转义。
            result = subprocess.run([
                "powershell",
                "Get-ItemProperty",
                r"HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
                "| Select-Object DisplayName,DisplayVersion,Publisher,InstallDate | ConvertTo-Json"
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout:
                # 可能是数组或单个对象
                try:
                    data = json.loads(result.stdout)
                    if isinstance(data, list):
                        return [
                            {"name": x.get("DisplayName"), "version": x.get("DisplayVersion"), "publisher": x.get("Publisher"), "date": x.get("InstallDate")} for x in data if x.get("DisplayName")
                        ]
                    elif isinstance(data, dict):
                        return [{"name": data.get("DisplayName"), "version": data.get("DisplayVersion"), "publisher": data.get("Publisher"), "date": data.get("InstallDate")}] if data.get("DisplayName") else []
                except Exception:
                    return []
            return []
        except Exception as e:
            logger.warning(f"获取已安装软件失败: {str(e)}")
            return []

    def get_network_cards(self):
        """获取网卡信息（名称、MAC、IP、速率）"""
        cards = []
        try:
            import socket
            for name, addrs in psutil.net_if_addrs().items():
                card = {"name": name, "mac": None, "ip": None, "speed": None}
                for addr in addrs:
                    # addr.family 可能是一个具有 name 属性的枚举，也可能是整数。
                    fam = getattr(addr, "family", None)
                    fam_name = getattr(fam, "name", None) if fam is not None else None
                    # 兼容不同平台和 psutil 版本的判断方式
                    if fam_name == "AF_LINK" or str(fam) == "AF_LINK" or fam == getattr(psutil, 'AF_LINK', None):
                        card["mac"] = addr.address
                    elif fam_name == "AF_INET" or str(fam) == "AF_INET" or fam == socket.AF_INET:
                        card["ip"] = addr.address
                # 速率
                stats = psutil.net_if_stats().get(name)
                if stats:
                    card["speed"] = stats.speed
                cards.append(card)
        except Exception as e:
            logger.warning(f"获取网卡信息失败: {str(e)}")
        return cards

    def get_motherboard_serial(self):
        """获取主板序列号（Windows: wmic; Linux: dmidecode）"""
        try:
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(["wmic", "baseboard", "get", "SerialNumber"], capture_output=True, text=True, timeout=5)
                lines = result.stdout.splitlines()
                for line in lines:
                    if line.strip() and "SerialNumber" not in line:
                        return line.strip()
            elif platform.system() == "Linux":
                import subprocess
                result = subprocess.run(["dmidecode", "-s", "baseboard-serial-number"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return result.stdout.strip()
        except Exception as e:
            logger.warning(f"获取主板序列号失败: {str(e)}")
        return None

    def get_cpu_detail(self):
        """获取CPU详细信息（型号、频率、核心数）"""
        try:
            info = {
                "model": platform.processor(),
                "physical_cores": psutil.cpu_count(logical=False),
                "total_cores": psutil.cpu_count(logical=True),
                "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else None,
                "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None
            }
            return info
        except Exception as e:
            logger.warning(f"获取CPU详细信息失败: {str(e)}")
            return {}

    def get_memory_detail(self):
        """获取内存详细信息（总量、类型、插槽）"""
        try:
            info = {"total": psutil.virtual_memory().total, "slots": None, "type": None}
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(["wmic", "memorychip", "get", "BankLabel,Capacity,MemoryType"], capture_output=True, text=True, timeout=5)
                lines = result.stdout.splitlines()
                slots = []
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 3:
                        slots.append({"bank": parts[0], "capacity": int(parts[1]), "type": parts[2]})
                info["slots"] = slots
            elif platform.system() == "Linux":
                import subprocess
                result = subprocess.run(["dmidecode", "-t", "memory"], capture_output=True, text=True, timeout=5)
                info["raw"] = result.stdout
            return info
        except Exception as e:
            logger.warning(f"获取内存详细信息失败: {str(e)}")
            return {}

    def get_system_uuid(self):
        """获取系统唯一标识符（UUID）"""
        try:
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(["wmic", "csproduct", "get", "UUID"], capture_output=True, text=True, timeout=5)
                lines = result.stdout.splitlines()
                for line in lines:
                    if line.strip() and "UUID" not in line:
                        return line.strip()
            elif platform.system() == "Linux":
                import subprocess
                result = subprocess.run(["cat", "/sys/class/dmi/id/product_uuid"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return result.stdout.strip()
        except Exception as e:
            logger.warning(f"获取系统UUID失败: {str(e)}")
        return None

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