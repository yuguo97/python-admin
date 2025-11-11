"""
Agent打包脚本

使用 PyInstaller 将 agent.py 打包为独立可执行文件

使用方法:
    python build_agent.py
"""

import os
import sys
import subprocess
import shutil


def build_agent():
    """打包Agent为可执行文件"""
    
    print("=" * 60)
    print("开始打包 Agent...")
    print("=" * 60)
    
    # 检查 PyInstaller 是否安装
    try:
        import PyInstaller
        print(f"✓ PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        return False
    
    # 打包命令
    cmd = [
        "pyinstaller",
        "-F",  # 打包为单个文件
        "-n", "device-agent",  # 输出文件名
        "--clean",  # 清理临时文件
        "--distpath", "dist",  # 输出目录
        "--workpath", "build",  # 临时目录
        "--specpath", ".",  # spec文件目录
        "agent.py"
    ]
    
    print(f"\n执行命令: {' '.join(cmd)}\n")
    
    try:
        # 执行打包
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        
        print("\n" + "=" * 60)
        print("✓ 打包成功!")
        print("=" * 60)
        
        # 显示输出文件信息
        if sys.platform == "win32":
            exe_path = os.path.join("dist", "device-agent.exe")
        else:
            exe_path = os.path.join("dist", "device-agent")
        
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n输出文件: {exe_path}")
            print(f"文件大小: {size:.2f} MB")
            
            print("\n使用方法:")
            if sys.platform == "win32":
                print(f"  {exe_path} --server http://your-server:8002 --token your-token")
            else:
                print(f"  chmod +x {exe_path}")
                print(f"  ./{exe_path} --server http://your-server:8002 --token your-token")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 打包失败: {e}")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"\n✗ 打包失败: {e}")
        return False


def clean_build_files():
    """清理构建文件"""
    print("\n清理构建文件...")
    
    dirs_to_remove = ["build", "__pycache__"]
    files_to_remove = ["device-agent.spec"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  已删除: {dir_name}/")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"  已删除: {file_name}")
    
    print("✓ 清理完成")


if __name__ == "__main__":
    success = build_agent()
    
    if success:
        # 询问是否清理构建文件
        response = input("\n是否清理构建文件? (y/n): ").strip().lower()
        if response == 'y':
            clean_build_files()
    
    sys.exit(0 if success else 1)
