import asyncio
from typing import AsyncGenerator, Optional
import aiohttp
import json
import os
from .utils.logger import setup_logger
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置日志记录器
logger = setup_logger("llm_service", "llm")

class LLMService:
    def __init__(self):
        """初始化LLM服务"""
        self.model_name = os.getenv("MODEL_NAME", "deepseek-coder:1.5b")
        self.api_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
        self.max_length = int(os.getenv("MODEL_MAX_LENGTH", "2048"))
        self.temperature = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
        self.top_p = float(os.getenv("MODEL_TOP_P", "0.9"))
        
        logger.info(
            "初始化LLM服务",
            extra={
                "model": self.model_name,
                "api_base": self.api_base,
                "max_length": self.max_length,
                "temperature": self.temperature,
                "top_p": self.top_p
            }
        )
        
        # 创建异步HTTP会话
        self.session = None
    
    async def _ensure_session(self):
        """确保HTTP会话已创建"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _generate(self, prompt: str, stream: bool = False) -> AsyncGenerator[str, None]:
        """生成回复的核心方法"""
        await self._ensure_session()
        
        # 构建请求数据
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "num_predict": self.max_length
            }
        }
        
        endpoint = "/api/generate" if stream else "/api/generate"
        try:
            async with self.session.post(
                f"{self.api_base}{endpoint}",
                json=data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if stream:
                    # 流式处理响应
                    async for line in response.content.iter_any():
                        if line:
                            try:
                                chunk = json.loads(line)
                                if "response" in chunk:
                                    yield chunk["response"]
                                if chunk.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
                else:
                    # 一次性处理响应
                    result = await response.json()
                    if "error" in result:
                        raise Exception(result["error"])
                    yield result["response"]
                    
        except Exception as e:
            logger.error(f"生成回复失败: {str(e)}")
            raise
    
    async def chat(self, prompt: str) -> str:
        """同步聊天接口"""
        try:
            logger.info("开始生成回复", extra={"prompt_length": len(prompt)})
            start_time = time.time()
            
            response = ""
            async for chunk in self._generate(prompt, stream=False):
                response = chunk
            
            process_time = (time.time() - start_time) * 1000
            logger.info(
                "回复生成完成",
                extra={
                    "process_time_ms": round(process_time, 2),
                    "response_length": len(response)
                }
            )
            return response
            
        except Exception as e:
            logger.error(f"生成回复失败: {str(e)}")
            raise

    async def chat_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """流式聊天接口"""
        try:
            logger.info("开始流式生成", extra={"prompt_length": len(prompt)})
            start_time = time.time()
            
            total_length = 0
            async for chunk in self._generate(prompt, stream=True):
                total_length += len(chunk)
                yield chunk
            
            process_time = (time.time() - start_time) * 1000
            logger.info(
                "流式生成完成",
                extra={
                    "process_time_ms": round(process_time, 2),
                    "total_length": total_length
                }
            )
                
        except Exception as e:
            logger.error(f"流式生成失败: {str(e)}")
            raise

    async def close(self):
        """关闭服务，释放资源"""
        try:
            logger.info("开始释放资源")
            if self.session:
                await self.session.close()
                self.session = None
            logger.info("资源释放完成")
        except Exception as e:
            logger.error(f"资源释放失败: {str(e)}")
            raise 