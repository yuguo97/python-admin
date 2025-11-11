"""
设备管理服务
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .database import devices
from .models import DeviceReportData, DeviceRecord, DeviceQuery, DeviceStatistics
from utils.logger import setup_logger

logger = setup_logger("device_service", "device_service")


class DeviceService:
    """设备管理服务"""
    
    @staticmethod
    async def save_device_report(report: DeviceReportData) -> bool:
        """
        保存设备上报数据
        
        Args:
            report: 设备上报数据
            
        Returns:
            bool: 是否保存成功
        """
        try:
            device_id = report.device_id
            now = datetime.now()
            
            # 提取关键信息
            ip_addresses = [net.ipv4 for net in report.networks if net.ipv4]
            mac_addresses = [net.mac for net in report.networks if net.mac]
            total_disk_gb = sum(disk.total_gb for disk in report.disks)
            
            # 查询是否已存在
            existing = await devices.find_one({"device_id": device_id})
            
            if existing:
                # 更新现有记录
                update_data = {
                    "$set": {
                        "serial_number": report.serial_number,
                        "hostname": report.os.hostname,
                        "os_system": report.os.system,
                        "os_version": report.os.version,
                        "cpu_model": report.cpu.model,
                        "cpu_cores": report.cpu.logical_cores,
                        "memory_gb": report.memory.total_gb,
                        "total_disk_gb": total_disk_gb,
                        "ip_addresses": ip_addresses,
                        "mac_addresses": mac_addresses,
                        "last_seen": now,
                        "raw_data": report.dict()
                    },
                    "$inc": {
                        "report_count": 1
                    }
                }
                
                await devices.update_one(
                    {"device_id": device_id},
                    update_data
                )
                logger.info(f"更新设备记录: {device_id} ({report.os.hostname})")
            else:
                # 创建新记录
                device_record = {
                    "device_id": device_id,
                    "serial_number": report.serial_number,
                    "hostname": report.os.hostname,
                    "os_system": report.os.system,
                    "os_version": report.os.version,
                    "cpu_model": report.cpu.model,
                    "cpu_cores": report.cpu.logical_cores,
                    "memory_gb": report.memory.total_gb,
                    "total_disk_gb": total_disk_gb,
                    "ip_addresses": ip_addresses,
                    "mac_addresses": mac_addresses,
                    "first_seen": now,
                    "last_seen": now,
                    "report_count": 1,
                    "raw_data": report.dict()
                }
                
                await devices.insert_one(device_record)
                logger.info(f"创建设备记录: {device_id} ({report.os.hostname})")
            
            return True
            
        except Exception as e:
            logger.error(f"保存设备报告失败: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def query_devices(query: DeviceQuery) -> Dict[str, Any]:
        """
        查询设备列表
        
        Args:
            query: 查询参数
            
        Returns:
            Dict: 包含设备列表和分页信息
        """
        try:
            # 构建查询条件
            filter_dict = {}
            
            if query.device_id:
                filter_dict["device_id"] = {"$regex": query.device_id, "$options": "i"}
            
            if query.hostname:
                filter_dict["hostname"] = {"$regex": query.hostname, "$options": "i"}
            
            if query.os_system:
                filter_dict["os_system"] = {"$regex": query.os_system, "$options": "i"}
            
            if query.ip_address:
                filter_dict["ip_addresses"] = {"$in": [query.ip_address]}
            
            # 计算总数
            total = await devices.count_documents(filter_dict)
            
            # 分页查询
            skip = (query.page - 1) * query.page_size
            cursor = devices.find(filter_dict).sort("last_seen", -1).skip(skip).limit(query.page_size)
            
            device_list = []
            async for doc in cursor:
                # 移除MongoDB的_id字段
                doc.pop("_id", None)
                # 转换datetime为字符串
                if "first_seen" in doc:
                    doc["first_seen"] = doc["first_seen"].isoformat()
                if "last_seen" in doc:
                    doc["last_seen"] = doc["last_seen"].isoformat()
                device_list.append(doc)
            
            return {
                "total": total,
                "page": query.page,
                "page_size": query.page_size,
                "devices": device_list
            }
            
        except Exception as e:
            logger.error(f"查询设备失败: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_device_detail(device_id: str) -> Optional[Dict[str, Any]]:
        """
        获取设备详情
        
        Args:
            device_id: 设备ID
            
        Returns:
            Optional[Dict]: 设备详情
        """
        try:
            device = await devices.find_one({"device_id": device_id})
            
            if device:
                device.pop("_id", None)
                if "first_seen" in device:
                    device["first_seen"] = device["first_seen"].isoformat()
                if "last_seen" in device:
                    device["last_seen"] = device["last_seen"].isoformat()
                return device
            
            return None
            
        except Exception as e:
            logger.error(f"获取设备详情失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def get_statistics() -> DeviceStatistics:
        """
        获取设备统计信息
        
        Returns:
            DeviceStatistics: 统计信息
        """
        try:
            # 总设备数
            total_devices = await devices.count_documents({})
            
            # 操作系统分布
            os_pipeline = [
                {"$group": {"_id": "$os_system", "count": {"$sum": 1}}}
            ]
            os_distribution = {}
            async for doc in devices.aggregate(os_pipeline):
                os_distribution[doc["_id"]] = doc["count"]
            
            # CPU分布 (按核心数分组)
            cpu_pipeline = [
                {"$group": {"_id": "$cpu_cores", "count": {"$sum": 1}}}
            ]
            cpu_distribution = {}
            async for doc in devices.aggregate(cpu_pipeline):
                key = f"{doc['_id']}核"
                cpu_distribution[key] = doc["count"]
            
            # 内存分布 (按范围分组)
            memory_pipeline = [
                {
                    "$bucket": {
                        "groupBy": "$memory_gb",
                        "boundaries": [0, 4, 8, 16, 32, 64, 128, 256],
                        "default": "256+",
                        "output": {"count": {"$sum": 1}}
                    }
                }
            ]
            memory_distribution = {}
            async for doc in devices.aggregate(memory_pipeline):
                boundary = doc["_id"]
                if boundary == "256+":
                    key = "256GB+"
                else:
                    key = f"{boundary}GB"
                memory_distribution[key] = doc["count"]
            
            # 在线/离线设备 (30分钟内有上报视为在线)
            threshold = datetime.now() - timedelta(minutes=30)
            online_devices = await devices.count_documents({"last_seen": {"$gte": threshold}})
            offline_devices = total_devices - online_devices
            
            return DeviceStatistics(
                total_devices=total_devices,
                os_distribution=os_distribution,
                cpu_distribution=cpu_distribution,
                memory_distribution=memory_distribution,
                online_devices=online_devices,
                offline_devices=offline_devices
            )
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def delete_device(device_id: str) -> bool:
        """
        删除设备记录
        
        Args:
            device_id: 设备ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            result = await devices.delete_one({"device_id": device_id})
            if result.deleted_count > 0:
                logger.info(f"删除设备记录: {device_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除设备失败: {e}", exc_info=True)
            return False
