"""
测试服务管理器功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from admin_service.app.service_manager import service_manager


def test_get_status():
    """测试获取服务状态"""
    print("=" * 60)
    print("测试获取所有服务状态")
    print("=" * 60)
    
    services = service_manager.get_all_services_status()
    
    for service in services:
        print(f"\n服务: {service['name']}")
        print(f"  - 服务名: {service['service_name']}")
        print(f"  - 端口: {service['port']}")
        print(f"  - 状态: {service['status']}")
        print(f"  - 描述: {service['description']}")
        
        if service['status'] == 'running' and 'pid' in service:
            print(f"  - PID: {service['pid']}")
            if 'cpu_percent' in service:
                print(f"  - CPU: {service['cpu_percent']:.2f}%")
            if 'memory_mb' in service:
                print(f"  - 内存: {service['memory_mb']:.2f} MB")


def test_start_service(service_name):
    """测试启动服务"""
    print("\n" + "=" * 60)
    print(f"测试启动服务: {service_name}")
    print("=" * 60)
    
    try:
        result = service_manager.start_service(service_name)
        print(f"✓ 启动成功")
        print(f"  - PID: {result['pid']}")
        print(f"  - 端口: {result['port']}")
        
        # 等待服务启动
        import time
        time.sleep(2)
        
        # 验证状态
        status = service_manager.get_service_status(service_name)
        print(f"  - 当前状态: {status['status']}")
        
    except Exception as e:
        print(f"✗ 启动失败: {e}")


def test_stop_service(service_name):
    """测试停止服务"""
    print("\n" + "=" * 60)
    print(f"测试停止服务: {service_name}")
    print("=" * 60)
    
    try:
        result = service_manager.stop_service(service_name)
        print(f"✓ 停止成功")
        print(f"  - PID: {result['pid']}")
        
        # 验证状态
        status = service_manager.get_service_status(service_name)
        print(f"  - 当前状态: {status['status']}")
        
    except Exception as e:
        print(f"✗ 停止失败: {e}")


def test_restart_service(service_name):
    """测试重启服务"""
    print("\n" + "=" * 60)
    print(f"测试重启服务: {service_name}")
    print("=" * 60)
    
    try:
        result = service_manager.restart_service(service_name)
        print(f"✓ 重启成功")
        print(f"  - PID: {result['pid']}")
        print(f"  - 端口: {result['port']}")
        
        # 等待服务启动
        import time
        time.sleep(2)
        
        # 验证状态
        status = service_manager.get_service_status(service_name)
        print(f"  - 当前状态: {status['status']}")
        
    except Exception as e:
        print(f"✗ 重启失败: {e}")


def main():
    """主函数"""
    print("服务管理器测试工具")
    print("=" * 60)
    
    # 显示所有服务状态
    test_get_status()
    
    # 交互式菜单
    while True:
        print("\n" + "=" * 60)
        print("请选择操作:")
        print("1. 查看所有服务状态")
        print("2. 启动服务")
        print("3. 停止服务")
        print("4. 重启服务")
        print("0. 退出")
        print("=" * 60)
        
        choice = input("请输入选项 (0-4): ").strip()
        
        if choice == "0":
            print("退出测试工具")
            break
        elif choice == "1":
            test_get_status()
        elif choice in ["2", "3", "4"]:
            print("\n可用服务:")
            print("  - system")
            print("  - crawler")
            print("  - ai")
            print("  - gateway")
            
            service_name = input("\n请输入服务名称: ").strip()
            
            if service_name not in ["system", "crawler", "ai", "gateway"]:
                print("✗ 无效的服务名称")
                continue
            
            if choice == "2":
                test_start_service(service_name)
            elif choice == "3":
                test_stop_service(service_name)
            elif choice == "4":
                test_restart_service(service_name)
        else:
            print("✗ 无效的选项")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断,退出测试工具")
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
