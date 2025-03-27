"""章节路由模块"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId
from utils.logger import setup_logger
from utils.response import success_response, error_response, not_found_error, server_error
from utils.auth import verify_token
from utils.tracing import create_span, add_span_attribute, set_span_status
from ..database import chapters, novels, async_db
from ..crawler import NovelCrawler

# 设置日志记录器
logger = setup_logger("crawler_chapters", "crawler")

# 创建路由
router = APIRouter()

# 创建爬虫实例
crawler = NovelCrawler()

@router.post("/{novel_id}/chapters")
async def crawl_chapters(novel_id: str, chapter_urls: List[str], _: dict = Depends(verify_token)):
    """爬取小说章节内容"""
    with create_span("crawl_chapters") as span:
        logger.info(f"开始爬取小说章节: {novel_id}, 章节数: {len(chapter_urls)}")
        add_span_attribute(span, "novel.id", novel_id)
        add_span_attribute(span, "chapters.count", str(len(chapter_urls)))
        
        try:
            # 检查小说是否存在
            novel = await novels.find_one({"_id": ObjectId(novel_id)})
            if not novel:
                add_span_attribute(span, "novel.exists", "false")
                set_span_status(span, "error", "小说不存在")
                return not_found_error(f"小说不存在: {novel_id}")
            
            # 启动爬取任务
            await crawler.crawl_chapters(ObjectId(novel_id), chapter_urls)
            logger.info(f"章节爬取任务已启动: {novel_id}")
            add_span_attribute(span, "task.status", "started")
            set_span_status(span, "ok")
            return success_response({"message": "章节爬取任务已启动"})
        except Exception as e:
            logger.error(f"爬取章节失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, "error", str(e))
            return server_error(f"爬取章节失败: {str(e)}")

@router.get("/{novel_id}/chapters")
async def get_chapters(novel_id: str, skip: int = 0, limit: int = 10):
    """获取小说章节列表"""
    logger.info(f"获取小说章节: novel_id={novel_id}, skip={skip}, limit={limit}")
    try:
        # 检查小说是否存在
        novel = await novels.find_one({"_id": ObjectId(novel_id)})
        if not novel:
            return not_found_error(f"小说不存在: {novel_id}")
        
        chapters_list = await chapters.find(
            {"novel_id": ObjectId(novel_id)}
        ).skip(skip).limit(limit).to_list(length=limit)
        
        return success_response(chapters_list)
    except Exception as e:
        logger.error(f"获取章节列表失败: {str(e)}")
        return server_error("获取章节列表失败")

@router.get("/{novel_id}/chapters/{chapter_id}")
async def get_chapter(novel_id: str, chapter_id: str):
    """获取章节详情"""
    logger.info(f"获取章节详情: novel_id={novel_id}, chapter_id={chapter_id}")
    try:
        chapter = await chapters.find_one({
            "_id": ObjectId(chapter_id),
            "novel_id": ObjectId(novel_id)
        })
        if not chapter:
            return not_found_error(f"章节不存在: {chapter_id}")
        return success_response(chapter)
    except Exception as e:
        logger.error(f"获取章节详情失败: {str(e)}")
        return server_error("获取章节详情失败") 