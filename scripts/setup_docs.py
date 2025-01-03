import os
import requests
from pathlib import Path

def download_file(url: str, filename: str):
    """下载文件到指定路径"""
    response = requests.get(url)
    response.raise_for_status()
    
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded: {filename}")

def setup_docs():
    """设置API文档所需的静态文件"""
    # 创建静态文件目录
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    # 要下载的文件
    files = {
        "swagger-ui-bundle.js": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.1.3/swagger-ui-bundle.js",
        "swagger-ui.css": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.1.3/swagger-ui.css",
        "redoc.standalone.js": "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    }
    
    # 下载文件
    for filename, url in files.items():
        filepath = static_dir / filename
        if not filepath.exists():
            try:
                download_file(url, str(filepath))
            except Exception as e:
                print(f"Error downloading {filename}: {str(e)}")

if __name__ == "__main__":
    setup_docs() 