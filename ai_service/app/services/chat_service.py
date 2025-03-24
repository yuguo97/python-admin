from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.database import ChatRecord

class ChatService:
    """对话记录服务"""
    
    @staticmethod
    def create_chat_record(
        db: Session,
        prompt: str,
        response: str,
        is_stream: bool = False
    ) -> ChatRecord:
        """创建对话记录"""
        chat_record = ChatRecord(
            prompt=prompt,
            response=response,
            is_stream=is_stream
        )
        db.add(chat_record)
        db.commit()
        db.refresh(chat_record)
        return chat_record
    
    @staticmethod
    def get_chat_record(db: Session, record_id: int) -> Optional[ChatRecord]:
        """获取单个对话记录"""
        return db.query(ChatRecord).filter(ChatRecord.id == record_id).first()
    
    @staticmethod
    def get_chat_records(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[ChatRecord]:
        """获取对话记录列表"""
        query = db.query(ChatRecord)
        
        if start_time:
            query = query.filter(ChatRecord.created_at >= start_time)
        if end_time:
            query = query.filter(ChatRecord.created_at <= end_time)
            
        return query.order_by(ChatRecord.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_chat_record(db: Session, record_id: int) -> bool:
        """删除对话记录"""
        record = db.query(ChatRecord).filter(ChatRecord.id == record_id).first()
        if record:
            db.delete(record)
            db.commit()
            return True
        return False
    
    @staticmethod
    def delete_chat_records(
        db: Session,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> int:
        """批量删除对话记录"""
        query = db.query(ChatRecord)
        
        if start_time:
            query = query.filter(ChatRecord.created_at >= start_time)
        if end_time:
            query = query.filter(ChatRecord.created_at <= end_time)
            
        deleted_count = query.delete()
        db.commit()
        return deleted_count 