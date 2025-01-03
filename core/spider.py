import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from models.novel import Novel
from datetime import datetime
import re
import logging
from flask import current_app

class NovelSpider:
    BASE_URL = 'http://www.woaisaicheshou.com/mu/2/'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    @staticmethod
    async def fetch_page(url):
        try:
            # 首先尝试同步请求
            current_app.logger.info(f"Fetching page synchronously: {url}")
            response = requests.get(url, headers=NovelSpider.HEADERS, timeout=30)
            response.encoding = 'gbk'  # 强制使用GBK编码
            if response.status_code == 200:
                current_app.logger.info("Successfully fetched page synchronously")
                return response.text
            
            # 如果同步请求失败，尝试异步请求
            current_app.logger.info("Synchronous request failed, trying async request")
            async with aiohttp.ClientSession(headers=NovelSpider.HEADERS) as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        try:
                            text = content.decode('gbk')
                            current_app.logger.info("Successfully decoded with GBK")
                            return text
                        except:
                            current_app.logger.warning("GBK decode failed, trying GB2312")
                            try:
                                return content.decode('gb2312')
                            except:
                                current_app.logger.warning("GB2312 decode failed, falling back to UTF-8")
                                return content.decode('utf-8', errors='ignore')
                    else:
                        current_app.logger.error(f"Failed to fetch page: {url}, status: {response.status}")
                        return None
        except Exception as e:
            current_app.logger.error(f"Error fetching page {url}: {str(e)}")
            return None
    
    @staticmethod
    def parse_novel_info(html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            current_app.logger.info("Started parsing novel info")
            
            # 打印页面内容用于调试
            current_app.logger.debug(f"Raw HTML content: {html[:1000]}")
            current_app.logger.debug(f"Parsed HTML structure: {soup.prettify()[:1000]}")
            
            # 获取标题
            title = ''
            title_candidates = [
                soup.find('h1'),
                soup.find('div', class_='title'),
                soup.find('div', class_='book-title'),
                soup.find(string=re.compile(r'《.*》'))
            ]
            
            for title_elem in title_candidates:
                if title_elem:
                    title = re.sub(r'[《》]', '', title_elem.text.strip())
                    if title:
                        break
            
            current_app.logger.info(f"Found title: {title}")
            
            # 获取作者
            author = '未知作者'
            author_patterns = [
                r'作\s*者[：:]\s*([^\n]+)',
                r'作\s*者[：:]\s*([^<]+)',
                r'([^《》]+)著'
            ]
            
            for pattern in author_patterns:
                author_match = re.search(pattern, html)
                if author_match:
                    author = author_match.group(1).strip()
                    break
            
            current_app.logger.info(f"Found author: {author}")
            
            # 获取简介
            description = ''
            desc_patterns = [
                r'简\s*介[：:]\s*([^\n]+)',
                r'内容简介[：:]\s*([^\n]+)',
                r'描\s*述[：:]\s*([^\n]+)'
            ]
            
            for pattern in desc_patterns:
                desc_match = re.search(pattern, html)
                if desc_match:
                    description = desc_match.group(1).strip()
                    break
            
            current_app.logger.info(f"Found description: {description[:100]}...")
            
            return {
                'title': title or '未知标题',
                'author': author,
                'description': description
            }
        except Exception as e:
            current_app.logger.error(f"Error parsing novel info: {str(e)}")
            return {
                'title': '解析失败',
                'author': '未知',
                'description': ''
            }
    
    @staticmethod
    def parse_chapters(html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            chapters = []
            
            # 查找所有可能的链接
            all_links = soup.find_all('a')
            current_app.logger.info(f"Found {len(all_links)} total links")
            
            # 章节链接的正则模式
            chapter_patterns = [
                r'第.*章',
                r'序章',
                r'前言',
                r'后记',
                r'\d+\.html$'
            ]
            
            for link in all_links:
                href = link.get('href', '')
                text = link.text.strip()
                
                # 检查是否是章节链接
                is_chapter = any(re.search(pattern, text) or re.search(pattern, href) for pattern in chapter_patterns)
                
                if is_chapter:
                    if not href.startswith('http'):
                        href = NovelSpider.BASE_URL.rstrip('/') + '/' + href.lstrip('/')
                    
                    chapters.append({
                        'title': text,
                        'url': href
                    })
                    current_app.logger.debug(f"Found chapter: {text} - {href}")
            
            current_app.logger.info(f"Found {len(chapters)} chapters")
            return chapters
            
        except Exception as e:
            current_app.logger.error(f"Error parsing chapters: {str(e)}")
            return []
    
    @staticmethod
    async def fetch_chapter_content(session, url):
        """获取章节内容"""
        try:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text(encoding='utf-8')
                    soup = BeautifulSoup(html, 'html.parser')
                    content_elem = soup.select_one('.chapter-content')
                    if content_elem:
                        # 清理内容
                        for ad in content_elem.select('.advertisement'):
                            ad.decompose()
                        return content_elem.text.strip()
                return ''
        except Exception as e:
            logging.error(f"Error fetching chapter content {url}: {str(e)}")
            return ''

    @classmethod
    async def crawl_chapters(cls, session, chapters):
        """批量爬取章节内容"""
        tasks = []
        for chapter in chapters:
            if not chapter.get('content'):  # 只爬取没有内容的章节
                url = chapter['url']
                if not url.startswith('http'):
                    url = cls.BASE_URL + url.lstrip('/')
                tasks.append(cls.fetch_chapter_content(session, url))
            else:
                tasks.append(None)
        
        contents = await asyncio.gather(*tasks)
        
        # 更新章节内容
        for i, content in enumerate(contents):
            if content is not None:
                chapters[i]['content'] = content
        
        return chapters

    @classmethod
    async def crawl_novel(cls, url):
        try:
            # 检查小说是否已存在
            current_app.logger.info(f"Checking novel existence: {url}")
            novel = Novel.objects(source_url=url).first()
            
            if not novel:
                current_app.logger.info(f"Creating new novel for: {url}")
                novel = Novel(source_url=url, status=1)
                novel.save()
            
            async with aiohttp.ClientSession(headers=cls.HEADERS) as session:
                # 获取小说页面内容
                html = await cls.fetch_page(url)
                if not html:
                    raise Exception("Failed to fetch novel page")
                
                # 解析小说信息
                info = cls.parse_novel_info(html)
                novel.title = info['title']
                novel.author = info['author']
                novel.description = info['description']
                
                # 获取章节列表
                chapters = cls.parse_chapters(html)
                if chapters:
                    # 爬取章节内容
                    chapters = await cls.crawl_chapters(session, chapters)
                    novel.chapters = chapters
                    novel.status = 2  # 爬取完成
                else:
                    novel.status = 0  # 爬取失败
                
                novel.updated_at = datetime.now()
                novel.save()
                
                logging.info(f"Successfully crawled novel: {novel.title}")
                return novel
                
        except Exception as e:
            current_app.logger.error(f"Error crawling novel {url}: {str(e)}")
            if novel:
                novel.status = 0  # 爬取失败
                novel.save()
            raise e

    @classmethod
    async def start_crawl(cls, urls):
        tasks = []
        for url in urls:
            if not url.startswith('http'):
                url = cls.BASE_URL + url.lstrip('/')
            tasks.append(cls.crawl_novel(url))
        
        try:
            return await asyncio.gather(*tasks)
        except Exception as e:
            logging.error(f"Error in batch crawling: {str(e)}")
            return [] 