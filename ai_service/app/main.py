""" AI服务主应用 """

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session
import asyncio
from typing import AsyncGenerator
import json
import time

from .models import (
    ChatRequest,
    ChatResponse,
    ChatRecordResponse,
    ChatRecordListResponse,
    ChatRecordQueryRequest,
    ChatRecordDeleteRequest
)
from .models.database import ChatRecord, init_db, get_db
from .services.chat_service import ChatService
from .services.llm import LLMService
from utils.logger import setup_logger

# 设置日志
logger = setup_logger("ai_service", "ai_service.log")

# 创建FastAPI应用
app = FastAPI(
    title="AI服务",
    description="提供AI对话和流式对话服务",
    version="1.0.0"
)

# 初始化数据库
init_db()

# 初始化LLM服务
llm_service = LLMService()

@app.on_event("startup")
async def startup_event():
    """服务启动时的事件处理"""
    logger.info("AI服务启动")
    logger.info("数据库表初始化完成")

@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时的事件处理"""
    await llm_service.close()
    logger.info("AI服务关闭")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志的中间件"""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    log_data = {
        "method": request.method,
        "url": str(request.url),
        "client": request.client.host if request.client else None,
        "process_time_ms": round(process_time, 2),
        "status_code": response.status_code
    }
    
    logger.info(f"Request processed", extra=log_data)
    return response

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """同步聊天接口"""
    try:
        logger.info(f"收到同步对话请求", extra={"prompt": request.prompt})
        start_time = time.time()
        
        response = await llm_service.chat(request.prompt)
        process_time = (time.time() - start_time) * 1000
        
        # 保存对话记录
        chat_record = ChatService.create_chat_record(db, request.prompt, response, is_stream=False)
        
        logger.info(
            f"同步对话完成",
            extra={
                "chat_id": chat_record.id,
                "process_time_ms": round(process_time, 2)
            }
        )
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"同步对话失败: {str(e)}", extra={"prompt": request.prompt})
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """SSE流式聊天接口"""
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            logger.info(f"收到流式对话请求", extra={"prompt": request.prompt})
            start_time = time.time()
            
            full_response = ""
            async for chunk in llm_service.chat_stream(request.prompt):
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            # 保存完整的对话记录
            chat_record = ChatService.create_chat_record(db, request.prompt, full_response, is_stream=True)
            
            process_time = (time.time() - start_time) * 1000
            logger.info(
                f"流式对话完成",
                extra={
                    "chat_id": chat_record.id,
                    "process_time_ms": round(process_time, 2)
                }
            )
            
        except Exception as e:
            logger.error(f"流式对话失败: {str(e)}", extra={"prompt": request.prompt})
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return EventSourceResponse(event_generator())

@app.get("/chat/records", response_model=ChatRecordListResponse)
def get_chat_records(
    request: ChatRecordQueryRequest,
    db: Session = Depends(get_db)
):
    """获取对话记录列表"""
    try:
        logger.info("查询对话记录", extra={"params": request.dict()})
        records = ChatService.get_chat_records(
            db,
            skip=request.skip,
            limit=request.limit,
            start_time=request.start_time,
            end_time=request.end_time
        )
        total = len(records)
        logger.info(f"查询对话记录成功", extra={"total": total})
        return ChatRecordListResponse(total=total, records=records)
    except Exception as e:
        logger.error(f"查询对话记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/records/{record_id}", response_model=ChatRecordResponse)
def get_chat_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """获取单个对话记录"""
    try:
        logger.info(f"查询单条对话记录", extra={"record_id": record_id})
        record = ChatService.get_chat_record(db, record_id)
        if not record:
            logger.warning(f"对话记录不存在", extra={"record_id": record_id})
            raise HTTPException(status_code=404, detail="对话记录不存在")
        logger.info(f"查询单条对话记录成功", extra={"record_id": record_id})
        return record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询单条对话记录失败: {str(e)}", extra={"record_id": record_id})
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat/records")
def delete_chat_records(
    request: ChatRecordDeleteRequest,
    db: Session = Depends(get_db)
):
    """删除对话记录"""
    try:
        logger.info("删除对话记录", extra={"params": request.dict()})
        if request.record_id:
            success = ChatService.delete_chat_record(db, request.record_id)
            if not success:
                logger.warning(f"对话记录不存在", extra={"record_id": request.record_id})
                raise HTTPException(status_code=404, detail="对话记录不存在")
            logger.info(f"删除单条对话记录成功", extra={"record_id": request.record_id})
            return {"message": "删除成功"}
        else:
            deleted_count = ChatService.delete_chat_records(
                db,
                start_time=request.start_time,
                end_time=request.end_time
            )
            logger.info(f"批量删除对话记录成功", extra={"deleted_count": deleted_count})
            return {"message": f"成功删除 {deleted_count} 条记录"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除对话记录失败: {str(e)}", extra={"params": request.dict()})
        raise HTTPException(status_code=500, detail=str(e)) 