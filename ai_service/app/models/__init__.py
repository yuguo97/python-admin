"""
AI服务数据模型包
"""

from .chat import (
    ChatRequest,
    ChatResponse,
    ChatRecordResponse,
    ChatRecordListResponse,
    ChatRecordQueryRequest,
    ChatRecordDeleteRequest
)
from .database import ChatRecord, init_db, get_db

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "ChatRecordResponse",
    "ChatRecordListResponse",
    "ChatRecordQueryRequest",
    "ChatRecordDeleteRequest",
    "ChatRecord",
    "init_db",
    "get_db"
]
