from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    """聊天请求模型"""
    prompt: str

class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str

class ChatRecordResponse(BaseModel):
    """对话记录响应模型"""
    id: int
    prompt: str
    response: str
    is_stream: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatRecordListResponse(BaseModel):
    """对话记录列表响应模型"""
    total: int
    records: List[ChatRecordResponse]

class ChatRecordQueryRequest(BaseModel):
    """对话记录查询请求模型"""
    skip: int = 0
    limit: int = 100
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ChatRecordDeleteRequest(BaseModel):
    """对话记录删除请求模型"""
    record_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None 