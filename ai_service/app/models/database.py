from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ChatRecord(Base):
    """对话记录模型"""
    __tablename__ = "chat_records"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False, comment="用户输入的问题")
    response = Column(Text, nullable=False, comment="AI的回复")
    is_stream = Column(Boolean, default=False, comment="是否为流式对话")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间") 