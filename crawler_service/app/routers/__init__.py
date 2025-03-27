"""路由模块初始化"""

from fastapi import APIRouter
from . import novels, chapters

# 创建主路由
router = APIRouter()

# 注册子路由
router.include_router(novels.router, prefix="/novels", tags=["novels"])
router.include_router(chapters.router, prefix="/novels", tags=["chapters"]) 