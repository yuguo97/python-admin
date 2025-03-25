""" LLM服务类 """

from typing import AsyncGenerator
import httpx
from ..utils.logger import setup_logger

logger = setup_logger("llm_service", "llm_service.log")

class LLMService:
    """ LLM服务类，用于处理与本地大模型的交互 """
    
    def __init__(self):
        """ 初始化LLM服务 """
        self.base_url = "http://localhost:11434"
        self.model = "llama2"  # 默认使用llama2模型
        logger.info("LLM服务初始化完成")
    
    async def chat(self, prompt: str) -> str:
        """ 同步聊天接口 """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                return response.json()["response"]
        except Exception as e:
            logger.error(f"同步对话失败: {str(e)}", extra={"prompt": prompt})
            raise
    
    async def chat_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """ 流式聊天接口 """
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True
                    }
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                data = line.split("data: ")[1]
                                if data != "[DONE]":
                                    yield data
                            except Exception as e:
                                logger.error(f"处理流式响应失败: {str(e)}")
                                continue
        except Exception as e:
            logger.error(f"流式对话失败: {str(e)}", extra={"prompt": prompt})
            raise
    
    async def close(self):
        """ 关闭服务 """
        logger.info("LLM服务关闭") 