import os
import requests
from pathlib import Path

def download_swagger_files():
    """下载 Swagger UI 所需的静态文件"""
    files = {
        'swagger-ui-bundle.js': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js',
        'swagger-ui.css': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css',
        'redoc.standalone.js': 'https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js'
    }
    
    services = ['admin_service', 'system_service', 'crawler_service', 'gateway_service']
    
    for service in services:
        # 创建static目录
        static_dir = Path(service) / 'static'
        static_dir.mkdir(parents=True, exist_ok=True)
        
        # 下载文件
        for filename, url in files.items():
            file_path = static_dir / filename
            if not file_path.exists():
                print(f'Downloading {filename} for {service}...')
                response = requests.get(url)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f'Downloaded {filename} to {file_path}')

if __name__ == '__main__':
    download_swagger_files() 