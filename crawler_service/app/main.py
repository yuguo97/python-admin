""" 爬虫服务主应用 """

from fastapi import FastAPI, HTTPException, Request, Depends
from typing import List
from . import models
from .database import async_db, init_indexes
from .crawler import NovelCrawler
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

# 设置日志记录器
logger = setup_logger("crawler_service", "crawler")

app = FastAPI(
    title="爬虫管理服务",
    description="""
    提供网络小说爬取和管理功能的服务。
    
    ## 功能特点
    * 小说信息爬取
    * 章节内容爬取
    * 异步爬虫实现
    * MongoDB存储
    """,
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# 初始化链路追踪
init_tracing(app, "crawler-service")

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

crawler = NovelCrawler()

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
    """服务启动时初始化"""
    logger.info("初始化爬虫服务...")
    init_indexes()
    logger.info("爬虫服务初始化完成")

@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时清理资源"""
    logger.info("关闭爬虫服务...")
    await crawler.close_session()
    logger.info("爬虫服务已关闭")

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