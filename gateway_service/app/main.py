from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Dict, Any
import os
from dotenv import load_dotenv
from utils.logger import setup_logger
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from utils.docs import setup_docs

# 设置日志记录器
logger = setup_logger("gateway", "gateway")

load_dotenv()

# 服务路由配置
SERVICE_ROUTES = {
    "admin": f"http://localhost:{os.getenv('ADMIN_SERVICE_PORT')}",
    "system": f"http://localhost:{os.getenv('SYSTEM_SERVICE_PORT')}",
    "crawler": f"http://localhost:{os.getenv('CRAWLER_SERVICE_PORT')}",
    "ai": f"http://localhost:{os.getenv('AI_SERVICE_PORT')}"
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API Gateway 启动")
    logger.info(f"服务路由配置: {SERVICE_ROUTES}")
    yield
    logger.info("API Gateway 关闭")

app = FastAPI(
    title="API Gateway",
    description="API Gateway Service Documentation",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan
)

# 配置API文档
setup_docs(app, "API Gateway")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

async def forward_request(service: str, path: str, request: Request) -> Dict[str, Any]:
    """转发请求到对应的微服务"""
    if service not in SERVICE_ROUTES:
        logger.error(f"服务未找到: {service}")
        raise HTTPException(status_code=404, detail="Service not found")
    
    service_url = SERVICE_ROUTES[service]
    url = f"{service_url}{path}"
    logger.info(f"转发请求到: {url}")
    
    async with httpx.AsyncClient() as client:
        try:
            # 获取原始请求的方法、头部和数据
            method = request.method
            headers = dict(request.headers)
            body = await request.body()
            
            # 转发请求
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body
            )
            
            logger.info(f"请求成功: {url}")
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"服务请求失败 {url}: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
        except Exception as e:
            logger.error(f"转发请求时发生错误 {url}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway_route(service: str, path: str, request: Request):
    """通用路由处理器"""
    return await forward_request(service, f"/{path}", request) 