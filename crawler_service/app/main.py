"""爬虫服务主模块"""

import asyncio
from fastapi import FastAPI, HTTPException, Request, Depends
from typing import List
from bson import ObjectId
from utils.logger import setup_logger
from utils.response import (
    success_response, error_response, unauthorized_error,
    forbidden_error, server_error, not_found_error
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from utils.auth import verify_token
from utils.tracing import init_tracing, create_span, add_span_attribute, set_span_status, end_span
from .routers import novels, chapters
from .database import init_indexes, close_db
from .crawler import NovelCrawler

# 设置日志记录器
logger = setup_logger("crawler", "crawler")

# 创建FastAPI应用
app = FastAPI(
    title="爬虫服务",
    description="小说爬虫服务API",
    version="1.0.0"
)

# 初始化追踪系统
init_tracing(app, "crawler-service")
logger.info("追踪系统初始化成功")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(novels.router, prefix="/api/v1", tags=["novels"])
app.include_router(chapters.router, prefix="/api/v1", tags=["chapters"])

# 创建爬虫实例
crawler = NovelCrawler()

# 自定义API文档路由
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
    )

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"全局异常: {str(exc)}")
    return server_error(f"服务器内部错误: {str(exc)}")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理器"""
    return error_response(
        message=str(exc.detail),
        status_code=exc.status_code
    )

@app.on_event("startup")
async def startup_event():
    """服务启动时执行"""
    try:
        # 初始化数据库索引
        await init_indexes()
        logger.info("数据库索引初始化成功")
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时执行"""
    try:
        # 关闭数据库连接
        await close_db()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"服务关闭失败: {str(e)}")
        raise

@app.get("/")
@create_span("health_check")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "crawler"}

@app.post("/novels")
async def create_novel(url: str, _: dict = Depends(verify_token)):
    """
    创建新小说爬取任务
    
    参数:
        - url: 小说源网址
    
    返回:
        小说基本信息:
        - id: 小说ID
        - title: 标题
        - author: 作者
        - description: 简介
        - cover_url: 封面图片URL
        - source_url: 源网址
        - created_at: 创建时间
    
    错误:
        - 400: 小说已存在
        - 401: 未授权访问
        - 500: 爬取失败或服务器错误
    
    说明:
        提交小说URL后会立即开始爬取小说基本信息，
        章节内容需要通过单独的接口爬取
    """
    with create_span("create_novel") as span:
        logger.info(f"开始爬取小说: {url}")
        add_span_attribute(span, "novel.url", url)
        
        # 检查是否已经存在
        existing = await async_db.novels.find_one({"source_url": url})
        if existing:
            logger.warning(f"小说已存在: {url}")
            add_span_attribute(span, "novel.exists", "true")
            set_span_status(span, StatusCode.ERROR, "小说已存在")
            return error_response("小说已存在", status_code=400)
        
        try:
            novel = await crawler.crawl_novel(url)
            logger.info(f"小说信息爬取成功: {novel.title}")
            add_span_attribute(span, "novel.title", novel.title)
            add_span_attribute(span, "novel.author", novel.author)
            set_span_status(span, StatusCode.OK)
            return success_response(novel.dict())
        except Exception as e:
            logger.error(f"爬取小说失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error(f"爬取小说失败: {str(e)}")

@app.post("/novels/{novel_id}/chapters")
async def crawl_chapters(novel_id: str, chapter_urls: List[str], _: dict = Depends(verify_token)):
    """
    爬取小说章节内容
    
    参数:
        - novel_id: 小说ID
        - chapter_urls: 章节URL列表
    
    返回:
        - message: 任务启动状态信息
    
    错误:
        - 401: 未授权访问
        - 404: 小说不存在
        - 500: 爬取失败或服务器错误
    
    说明:
        这是一个异步任务，接口会立即返回，
        实际爬取过程在后台进行
    """
    with create_span("crawl_chapters") as span:
        logger.info(f"开始爬取小说章节: {novel_id}, 章节数: {len(chapter_urls)}")
        add_span_attribute(span, "novel.id", novel_id)
        add_span_attribute(span, "chapters.count", str(len(chapter_urls)))
        
        try:
            # 检查小说是否存在
            novel = await async_db.novels.find_one({"_id": ObjectId(novel_id)})
            if not novel:
                add_span_attribute(span, "novel.exists", "false")
                set_span_status(span, StatusCode.ERROR, "小说不存在")
                return not_found_error(f"小说不存在: {novel_id}")
            
            # 启动爬取任务
            await crawler.crawl_chapters(ObjectId(novel_id), chapter_urls)
            logger.info(f"章节爬取任务已启动: {novel_id}")
            add_span_attribute(span, "task.status", "started")
            set_span_status(span, StatusCode.OK)
            return success_response({"message": "章节爬取任务已启动"})
        except Exception as e:
            logger.error(f"爬取章节失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error(f"爬取章节失败: {str(e)}")

@app.get("/novels")
async def list_novels(skip: int = 0, limit: int = 10):
    """获取小说列表"""
    logger.info(f"获取小说列表: skip={skip}, limit={limit}")
    try:
        novels = await async_db.novels.find().skip(skip).limit(limit).to_list(length=limit)
        return success_response(novels)
    except Exception as e:
        logger.error(f"获取小说列表失败: {str(e)}")
        return server_error("获取小说列表失败")

@app.get("/novels/{novel_id}")
async def get_novel(novel_id: str):
    """获取小说详情"""
    logger.info(f"获取小说详情: {novel_id}")
    try:
        novel = await async_db.novels.find_one({"_id": ObjectId(novel_id)})
        if not novel:
            return not_found_error(f"小说不存在: {novel_id}")
        return success_response(novel)
    except Exception as e:
        logger.error(f"获取小说详情失败: {str(e)}")
        return server_error("获取小说详情失败")

@app.get("/novels/{novel_id}/chapters")
async def get_chapters(novel_id: str, skip: int = 0, limit: int = 10):
    """获取小说章节列表"""
    logger.info(f"获取小说章节: novel_id={novel_id}, skip={skip}, limit={limit}")
    try:
        # 检查小说是否存在
        novel = await async_db.novels.find_one({"_id": ObjectId(novel_id)})
        if not novel:
            return not_found_error(f"小说不存在: {novel_id}")
        
        chapters = await async_db.chapters.find(
            {"novel_id": ObjectId(novel_id)}
        ).skip(skip).limit(limit).to_list(length=limit)
        
        return success_response(chapters)
    except Exception as e:
        logger.error(f"获取章节列表失败: {str(e)}")
        return server_error("获取章节列表失败")

@app.get("/novels/{novel_id}/chapters/{chapter_id}")
async def get_chapter(novel_id: str, chapter_id: str):
    """获取章节详情"""
    logger.info(f"获取章节详情: novel_id={novel_id}, chapter_id={chapter_id}")
    try:
        chapter = await async_db.chapters.find_one({
            "_id": ObjectId(chapter_id),
            "novel_id": ObjectId(novel_id)
        })
        if not chapter:
            return not_found_error(f"章节不存在: {chapter_id}")
        return success_response(chapter)
    except Exception as e:
        logger.error(f"获取章节详情失败: {str(e)}")
        return server_error("获取章节详情失败") 