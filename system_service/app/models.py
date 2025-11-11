"""
设备信息数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class NetworkInfo(BaseModel):
    """网卡信息"""
    name: str
    ipv4: Optional[str] = None
    mac: Optional[str] = None
    is_up: bool = False


class DiskInfo(BaseModel):
    """磁盘信息"""
    device: str
    mountpoint: str
    filesystem: str
    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float


class MemoryInfo(BaseModel):
    """内存信息"""
    total_gb: float
    type: str = "Unknown"


class CPUInfo(BaseModel):
    """CPU信息"""
    model: str
    physical_cores: int
    logical_cores: int
    max_frequency_mhz: Optional[float] = None
    current_frequency_mhz: Optional[float] = None


class OSInfo(BaseModel):
    """操作系统信息"""
    system: str
    release: str
    version: str
    architecture: str
    hostname: str
    boot_time: str


class SoftwareInfo(BaseModel):
    """软件信息"""
    name: str
    version: str


class DeviceReportData(BaseModel):
    """设备上报数据"""
    device_id: str = Field(..., description="设备唯一标识")
    serial_number: Optional[str] = Field(None, description="主板序列号")
    collected_at: str = Field(..., description="采集时间")
    os: OSInfo
    cpu: CPUInfo
    memory: MemoryInfo
    disks: List[DiskInfo]
    networks: List[NetworkInfo]
    software: List[SoftwareInfo] = []


class DeviceRecord(BaseModel):
    """设备记录(数据库存储)"""
    device_id: str
    serial_number: Optional[str] = None
    hostname: str
    os_system: str
    os_version: str
    cpu_model: str
    cpu_cores: int
    memory_gb: float
    total_disk_gb: float
    ip_addresses: List[str] = []
    mac_addresses: List[str] = []
    first_seen: datetime
    last_seen: datetime
    report_count: int = 1
    raw_data: Dict[str, Any] = {}
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DeviceQuery(BaseModel):
    """设备查询参数"""
    device_id: Optional[str] = None
    hostname: Optional[str] = None
    os_system: Optional[str] = None
    ip_address: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class DeviceStatistics(BaseModel):
    """设备统计信息"""
    total_devices: int
    os_distribution: Dict[str, int]
    cpu_distribution: Dict[str, int]
    memory_distribution: Dict[str, int]
    online_devices: int
    offline_devices: int
