from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl
from datetime import datetime

class Novel(BaseModel):
    """小说模型"""
    title: str
    author: str
    description: Optional[str] = None
    cover_url: Optional[HttpUrl] = None
    source_url: HttpUrl
    status: str = "pending"  # pending, crawling, completed, error
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """转换为字典，并处理ObjectId"""
        d = super().dict(*args, **kwargs)
        # 处理datetime
        d['created_at'] = self.created_at.isoformat()
        d['updated_at'] = self.updated_at.isoformat()
        return d

class Chapter(BaseModel):
    """章节模型"""
    novel_id: str
    title: str
    content: str
    chapter_number: int
    source_url: HttpUrl
    created_at: datetime = datetime.now()

    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """转换为字典，并处理ObjectId"""
        d = super().dict(*args, **kwargs)
        # 处理datetime
        d['created_at'] = self.created_at.isoformat()
        return d

class NovelList(BaseModel):
    """小说列表模型"""
    novels: List[Novel]
    total: int
    skip: int
    limit: int

class ChapterList(BaseModel):
    """章节列表模型"""
    chapters: List[Chapter]
    total: int
    skip: int
    limit: int 