"""聊天服务模块"""

from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.database import ChatRecord
from ..models import ChatRecordQueryRequest, ChatRecordDeleteRequest
from .llm import LLMService
from utils.logger import setup_logger

logger = setup_logger("chat_service", "ai")

class ChatService:
    def __init__(self):
        self.llm_service = LLMService()
        logger.info("初始化聊天服务")

    async def chat(self, prompt: str) -> str:
        """处理普通对话请求"""
        try:
            response = await self.llm_service.chat(prompt)
            return response
        except Exception as e:
            logger.error(f"对话处理失败: {str(e)}")
            raise

    async def chat_stream(self, prompt: str):
        """处理流式对话请求"""
        try:
            async for chunk in self.llm_service.chat_stream(prompt):
                yield chunk
        except Exception as e:
            logger.error(f"流式对话处理失败: {str(e)}")
            raise

    async def get_chat_records(
        self,
        request: ChatRecordQueryRequest,
        db: Session
    ) -> List[ChatRecord]:
        """获取对话记录"""
        try:
            query = db.query(ChatRecord)
            if request.record_id:
                query = query.filter(ChatRecord.id == request.record_id)
            
            total = query.count()
            records = query.offset((request.page - 1) * request.page_size).limit(request.page_size).all()
            
            return {
                "items": records,
                "total": total,
                "page": request.page,
                "page_size": request.page_size
            }
        except Exception as e:
            logger.error(f"获取对话记录失败: {str(e)}")
            raise

    async def delete_chat_records(
        self,
        request: ChatRecordDeleteRequest,
        db: Session
    ):
        """删除对话记录"""
        try:
            if request.record_id:
                db.query(ChatRecord).filter(ChatRecord.id == request.record_id).delete()
            else:
                db.query(ChatRecord).delete()
            db.commit()
        except Exception as e:
            logger.error(f"删除对话记录失败: {str(e)}")
            db.rollback()
            raise 