"""
终端采集脚本 - Agent
用于采集本机硬件和软件配置信息,并上报到中心平台

依赖:
    pip install psutil requests
    Windows: pip install wmi pywin32
    Linux: 需要 dmidecode 命令

使用方法:
    python agent.py --server http://your-server:8002 --token your-token
    
打包为 exe:
    pyinstaller -F agent.py
"""

import psutil
import platform
import socket
import json
import requests
import argparse
import sys
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SystemCollector:
    """系统信息采集器"""
    
    def __init__(self):
        self.os_type = platform.system()
        logger.info(f"初始化采集器,操作系统: {self.os_type}")
    
    def get_system_uuid(self) -> str:
        """获取系统唯一标识符"""
        try:
            if self.os_type == "Windows":
                import wmi
                c = wmi.WMI()
                for item in c.Win32_ComputerSystemProduct():
                    return item.UUID
            elif self.os_type == "Linux":
                import subprocess
                result = subprocess.run(
                    ['dmidecode', '-s', 'system-uuid'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip()
            else:
                # macOS 或其他系统,使用主机名+MAC地址作为标识
                mac = ':'.join(['{:02x}'.format((psutil.net_if_addrs()[iface][0].address.replace(':', ''))) 
                               for iface in psutil.net_if_addrs() if psutil.net_if_addrs()[iface][0].family == 17][:1])
                return f"{socket.gethostname()}-{mac}"
        except Exception as e:
            logger.warning(f"获取系统UUID失败: {e}, 使用主机名作为标识")
            return socket.gethostname()
    
    def get_serial_number(self) -> Optional[str]:
        """获取主板序列号"""
        try:
            if self.os_type == "Windows":
                import wmi
                c = wmi.WMI()
                for item in c.Win32_BIOS():
                    return item.SerialNumber
            elif self.os_type == "Linux":
                import subprocess
                result = subprocess.run(
                    ['dmidecode', '-s', 'baseboard-serial-number'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip()
        except Exception as e:
            logger.warning(f"获取序列号失败: {e}")
            return None
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        try:
            cpu_freq = psutil.cpu_freq()
            return {
                "model": platform.processor(),
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "max_frequency_mhz": round(cpu_freq.max, 2) if cpu_freq else None,
                "current_frequency_mhz": round(cpu_freq.current, 2) if cpu_freq else None,
            }
        except Exception as e:
            logger.error(f"获取CPU信息失败: {e}")
            return {}
    
    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        try:
            mem = psutil.virtual_memory()
            return {
                "total_gb": round(mem.total / (1024**3), 2),
                "type": "Unknown",  # psutil 无法直接获取内存类型
            }
        except Exception as e:
            logger.error(f"获取内存信息失败: {e}")
            return {}
    
    def get_disk_info(self) -> list:
        """获取磁盘信息"""
        disks = []
        try:
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "usage_percent": usage.percent
                    })
                except PermissionError:
                    continue
        except Exception as e:
            logger.error(f"获取磁盘信息失败: {e}")
        return disks
    
    def get_network_info(self) -> list:
        """获取网卡信息"""
        networks = []
        try:
            if_addrs = psutil.net_if_addrs()
            if_stats = psutil.net_if_stats()
            
            for interface_name, addrs in if_addrs.items():
                # 跳过回环接口
                if interface_name.startswith('lo'):
                    continue
                
                ipv4 = None
                mac = None
                
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        ipv4 = addr.address
                    elif addr.family == psutil.AF_LINK:
                        mac = addr.address
                
                # 获取网卡状态
                is_up = if_stats[interface_name].isup if interface_name in if_stats else False
                
                if ipv4 or mac:
                    networks.append({
                        "name": interface_name,
                        "ipv4": ipv4,
                        "mac": mac,
                        "is_up": is_up
                    })
        except Exception as e:
            logger.error(f"获取网卡信息失败: {e}")
        return networks
    
    def get_os_info(self) -> Dict[str, Any]:
        """获取操作系统信息"""
        try:
            return {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "architecture": platform.machine(),
                "hostname": socket.gethostname(),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
        except Exception as e:
            logger.error(f"获取操作系统信息失败: {e}")
            return {}
    
    def get_installed_software(self) -> list:
        """获取已安装软件列表 (仅Windows)"""
        software_list = []
        if self.os_type != "Windows":
            return software_list
        
        try:
            import winreg
            
            # 查询注册表中的已安装软件
            reg_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for reg_path in reg_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            try:
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                software_list.append({
                                    "name": name,
                                    "version": version
                                })
                            except:
                                pass
                            finally:
                                winreg.CloseKey(subkey)
                        except:
                            continue
                    winreg.CloseKey(key)
                except:
                    continue
        except Exception as e:
            logger.warning(f"获取软件列表失败: {e}")
        
        return software_list[:100]  # 限制返回数量
    
    def collect_all(self) -> Dict[str, Any]:
        """采集所有信息"""
        logger.info("开始采集系统信息...")
        
        data = {
            "device_id": self.get_system_uuid(),
            "serial_number": self.get_serial_number(),
            "collected_at": datetime.now().isoformat(),
            "os": self.get_os_info(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disks": self.get_disk_info(),
            "networks": self.get_network_info(),
            "software": self.get_installed_software()
        }
        
        logger.info(f"采集完成,设备ID: {data['device_id']}")
        return data


class AgentReporter:
    """数据上报器"""
    
    def __init__(self, server_url: str, token: str, timeout: int = 30):
        self.server_url = server_url.rstrip('/')
        self.token = token
        self.timeout = timeout
        logger.info(f"初始化上报器,服务器: {self.server_url}")
    
    def report(self, data: Dict[str, Any]) -> bool:
        """上报数据到中心平台"""
        url = f"{self.server_url}/devices/report"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        
        try:
            logger.info(f"开始上报数据到 {url}")
            response = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    logger.info(f"数据上报成功: {result.get('message', '')}")
                    return True
                else:
                    logger.error(f"数据上报失败: {result.get('message', '')}")
                    return False
            else:
                logger.error(f"数据上报失败,HTTP状态码: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"数据上报超时 (>{self.timeout}s)")
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"无法连接到服务器: {self.server_url}")
            return False
        except Exception as e:
            logger.error(f"数据上报异常: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='系统信息采集Agent')
    parser.add_argument('--server', required=True, help='中心平台服务器地址')
    parser.add_argument('--token', required=True, help='认证Token')
    parser.add_argument('--timeout', type=int, default=30, help='请求超时时间(秒)')
    parser.add_argument('--interval', type=int, default=0, help='循环采集间隔(分钟),0表示只执行一次')
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("系统信息采集Agent启动")
    logger.info(f"服务器: {args.server}")
    logger.info(f"间隔: {args.interval}分钟" if args.interval > 0 else "单次执行")
    logger.info("=" * 60)
    
    collector = SystemCollector()
    reporter = AgentReporter(args.server, args.token, args.timeout)
    
    def run_once():
        """执行一次采集和上报"""
        try:
            # 采集信息
            data = collector.collect_all()
            
            # 上报数据
            success = reporter.report(data)
            
            return success
        except Exception as e:
            logger.error(f"执行失败: {e}", exc_info=True)
            return False
    
    # 执行采集
    if args.interval > 0:
        # 循环模式
        logger.info(f"进入循环模式,每 {args.interval} 分钟执行一次")
        while True:
            run_once()
            logger.info(f"等待 {args.interval} 分钟后再次执行...")
            time.sleep(args.interval * 60)
    else:
        # 单次执行
        success = run_once()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
