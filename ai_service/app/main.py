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
    ChatRequest, ChatResponse, ChatRecordResponse,
    ChatRecordListResponse, ChatRecordQueryRequest,
    ChatRecordDeleteRequest
)
from .models.database import ChatRecord, init_db, get_db
from .services.chat import ChatService
from .services.llm import LLMService
from utils.logger import setup_logger
from utils.response import (
    success_response, error_response, server_error,
    not_found_error, unauthorized_error
)
from utils.auth import verify_token
from utils.tracing import init_tracing, create_span, add_span_attribute, set_span_status, end_span

# 设置日志记录器
logger = setup_logger("ai_service", "ai")

app = FastAPI(
    title="AI对话服务",
    description="""
    提供基于大语言模型的对话服务。
    
    ## 功能特点
    * 文本对话
    * 流式响应
    * 对话历史记录
    * 上下文管理
    """,
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# 初始化链路追踪
init_tracing(app, "ai-service")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
chat_service = ChatService()
llm_service = LLMService()

# 初始化数据库
init_db()

@app.on_event("startup")
async def startup_event():
    """服务启动时初始化"""
    logger.info("初始化AI服务...")
    logger.info("AI服务初始化完成")

@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时清理资源"""
    logger.info("关闭AI服务...")
    logger.info("AI服务已关闭")

@app.post("/chat")
async def chat(request: ChatRequest, _: dict = Depends(verify_token)):
    """发送对话请求"""
    with create_span("chat") as span:
        logger.info(f"收到对话请求: {request.prompt}")
        add_span_attribute(span, "prompt", request.prompt)
        
        try:
            response = await chat_service.chat(request.prompt)
            logger.info("对话响应成功")
            add_span_attribute(span, "response", response)
            set_span_status(span, StatusCode.OK)
            return success_response(ChatResponse(response=response))
        except Exception as e:
            logger.error(f"对话请求失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error(f"对话请求失败: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, _: dict = Depends(verify_token)):
    """发送流式对话请求"""
    with create_span("chat_stream") as span:
        logger.info(f"收到流式对话请求: {request.prompt}")
        add_span_attribute(span, "prompt", request.prompt)
        
        try:
            async def event_generator() -> AsyncGenerator[str, None]:
                async for chunk in chat_service.chat_stream(request.prompt):
                    yield f"data: {json.dumps({'response': chunk})}\n\n"
                    add_span_attribute(span, "chunk", chunk)
            
            set_span_status(span, StatusCode.OK)
            return EventSourceResponse(event_generator())
        except Exception as e:
            logger.error(f"流式对话请求失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error(f"流式对话请求失败: {str(e)}")

@app.get("/chat/records")
async def get_chat_records(
    request: ChatRecordQueryRequest = Depends(),
    _: dict = Depends(verify_token)
):
    """获取对话记录列表"""
    with create_span("get_chat_records") as span:
        logger.info("获取对话记录列表")
        add_span_attribute(span, "page", str(request.page))
        add_span_attribute(span, "page_size", str(request.page_size))
        
        try:
            records = await chat_service.get_chat_records(request)
            logger.info(f"获取到 {len(records.items)} 条对话记录")
            add_span_attribute(span, "records.count", str(len(records.items)))
            set_span_status(span, StatusCode.OK)
            return success_response(records)
        except Exception as e:
            logger.error(f"获取对话记录失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error(f"获取对话记录失败: {str(e)}")

@app.delete("/chat/records")
async def delete_chat_records(
    request: ChatRecordDeleteRequest = Depends(),
    _: dict = Depends(verify_token)
):
    """删除对话记录"""
    with create_span("delete_chat_records") as span:
        logger.info("删除对话记录")
        add_span_attribute(span, "record_id", str(request.record_id) if request.record_id else "all")
        
        try:
            await chat_service.delete_chat_records(request)
            logger.info("对话记录删除成功")
            set_span_status(span, StatusCode.OK)
            return success_response({"message": "对话记录删除成功"})
        except Exception as e:
            logger.error(f"删除对话记录失败: {str(e)}")
            add_span_attribute(span, "error", str(e))
            set_span_status(span, StatusCode.ERROR, str(e))
            return server_error(f"删除对话记录失败: {str(e)}") 