"""小说路由模块"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId
from utils.logger import setup_logger
from utils.response import success_response, error_response, not_found_error, server_error
from utils.auth import verify_token
from utils.tracing import create_span, add_span_attribute, set_span_status
from ..database import novels, async_db
from ..crawler import NovelCrawler

# 设置日志记录器
logger = setup_logger("crawler_novels", "crawler")

# 创建路由
router = APIRouter()

# 创建爬虫实例
crawler = NovelCrawler()

@router.post("")
async def create_novel(url: str, _: dict = Depends(verify_token)):
    """创建新小说爬取任务"""
    with create_span("create_novel") as span:
        logger.info(f"开始爬取小说: {url}")
        add_span_attribute(span, "novel.url", url)
        
        # 检查是否已经存在
        existing = await novels.find_one({"source_url": url})
        if existing:
            logger.warning(f"小说已存在: {url}")
            add_span_attribute(span, "novel.exists", "true")
            set_span_status(span, "error", "小说已存在")
            return error_response("小说已存在", status_code=400)
        
        try:
            novel = await crawler.crawl_novel(url)
            logger.info(f"小说信息爬取成功: {novel.title}")
            add_span_attribute(span, "novel.title", novel.title)
            add_span_attribute(span, "novel.author", novel.author)
            set_span_status(span, "ok")
            return success_response(novel.dict())
        except Exception as e:
            logger.error(f"爬取小说失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, "error", str(e))
            return server_error(f"爬取小说失败: {str(e)}")

@router.get("")
async def list_novels(skip: int = 0, limit: int = 10):
    """获取小说列表"""
    logger.info(f"获取小说列表: skip={skip}, limit={limit}")
    try:
        novels_list = await novels.find().skip(skip).limit(limit).to_list(length=limit)
        return success_response(novels_list)
    except Exception as e:
        logger.error(f"获取小说列表失败: {str(e)}")
        return server_error("获取小说列表失败")

@router.get("/{novel_id}")
async def get_novel(novel_id: str):
    """获取小说详情"""
    logger.info(f"获取小说详情: {novel_id}")
    try:
        novel = await novels.find_one({"_id": ObjectId(novel_id)})
        if not novel:
            return not_found_error(f"小说不存在: {novel_id}")
        return success_response(novel)
    except Exception as e:
        logger.error(f"获取小说详情失败: {str(e)}")
        return server_error("获取小说详情失败") 