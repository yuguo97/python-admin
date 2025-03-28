""" 聊天相关的数据模型 """

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ChatRequest(BaseModel):
    """ 聊天请求模型 """
    prompt: str

class ChatResponse(BaseModel):
    """ 聊天响应模型 """
    response: str

class ChatRecordResponse(BaseModel):
    """ 聊天记录响应模型 """
    id: int
    prompt: str
    response: str
    is_stream: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatRecordListResponse(BaseModel):
    """ 聊天记录列表响应模型 """
    total: int
    records: List[ChatRecordResponse]

class ChatRecordQueryRequest(BaseModel):
    """ 聊天记录查询请求模型 """
    page: int = 1
    page_size: int = 10
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ChatRecordDeleteRequest(BaseModel):
    """ 聊天记录删除请求模型 """
    record_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None 