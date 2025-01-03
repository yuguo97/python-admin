import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
from . import models
from .database import async_db
from bson import ObjectId
from utils.logger import setup_logger

# 设置日志记录器
logger = setup_logger("crawler", "crawler_worker")

class NovelCrawler:
    def __init__(self):
        self.session = None

    async def init_session(self):
        """初始化HTTP会话"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("HTTP会话已初始化")

    async def close_session(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("HTTP会话已关闭")

    async def crawl_novel(self, url: str) -> models.Novel:
        """爬取小说基本信息
        Args:
            url: 小说页面URL
        Returns:
            models.Novel: 小说信息对象
        """
        logger.info(f"开始爬取小说信息: {url}")
        await self.init_session()
        try:
            async with self.session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # 这里的选择器需要根据实际网站调整
                title = soup.select_one('h1.novel-title').text.strip()
                author = soup.select_one('div.author').text.strip()
                description = soup.select_one('div.description').text.strip()
                
                logger.info(f"解析到小说信息: {title} - {author}")
                
                novel = {
                    "title": title,
                    "author": author,
                    "description": description,
                    "source_url": url,
                    "status": "pending",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                result = await async_db.novels.insert_one(novel)
                novel['_id'] = result.inserted_id
                logger.info(f"小说信息已保存到数据库: {title}")
                return models.Novel(**novel)
        except Exception as e:
            logger.error(f"爬取小说信息失败: {str(e)}")
            raise Exception(f"爬取小说信息失败: {str(e)}")

    async def crawl_chapters(self, novel_id: str, chapter_urls: List[str]):
        """爬取小说章节内容
        Args:
            novel_id: 小说ID
            chapter_urls: 章节URL列表
        """
        logger.info(f"开始爬取章节: novel_id={novel_id}, 章节数={len(chapter_urls)}")
        await self.init_session()
        novel_id = ObjectId(novel_id)
        
        # 更新小说状态为爬取中
        await async_db.novels.update_one(
            {"_id": novel_id},
            {"$set": {"status": "crawling", "updated_at": datetime.utcnow()}}
        )
        logger.info(f"小说状态已更新为爬取中: {novel_id}")
        
        try:
            for index, url in enumerate(chapter_urls, 1):
                try:
                    async with self.session.get(url) as response:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        title = soup.select_one('h1.chapter-title').text.strip()
                        content = soup.select_one('div.chapter-content').text.strip()
                        
                        chapter = {
                            "novel_id": novel_id,
                            "title": title,
                            "content": content,
                            "chapter_number": index,
                            "source_url": url,
                            "created_at": datetime.utcnow()
                        }
                        
                        await async_db.chapters.insert_one(chapter)
                        logger.info(f"章节已保存: {title}")
                        
                except Exception as e:
                    logger.error(f"爬取章节失败 {url}: {str(e)}")
                    continue
                
            # 更新小说状态为完成
            await async_db.novels.update_one(
                {"_id": novel_id},
                {"$set": {"status": "completed", "updated_at": datetime.utcnow()}}
            )
            logger.info(f"小说爬取完成: {novel_id}")
            
        except Exception as e:
            # 更新小说状态为错误
            await async_db.novels.update_one(
                {"_id": novel_id},
                {"$set": {"status": "error", "updated_at": datetime.utcnow()}}
            )
            logger.error(f"爬取章节失败: {str(e)}")
            raise Exception(f"爬取章节失败: {str(e)}") 