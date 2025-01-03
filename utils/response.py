from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi import status

def create_response(
    code: int,
    message: str,
    data: Any = None,
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """创建统一响应格式"""
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "data": data
        }
    )

def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """成功响应"""
    return create_response(200, message, data, status_code)

def error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    data: Any = None
) -> JSONResponse:
    """错误响应"""
    return create_response(status_code, message, data, status_code)

def unauthorized_error(
    message: str = "未授权访问",
    data: Any = None
) -> JSONResponse:
    """未授权错误"""
    return create_response(
        status.HTTP_401_UNAUTHORIZED,
        message,
        data,
        status.HTTP_401_UNAUTHORIZED
    )

def forbidden_error(
    message: str = "权限不足",
    data: Any = None
) -> JSONResponse:
    """禁止访问错误"""
    return create_response(
        status.HTTP_403_FORBIDDEN,
        message,
        data,
        status.HTTP_403_FORBIDDEN
    )

def not_found_error(
    message: str = "资源不存在",
    data: Any = None
) -> JSONResponse:
    """资源不存在错误"""
    return create_response(
        status.HTTP_404_NOT_FOUND,
        message,
        data,
        status.HTTP_404_NOT_FOUND
    )

def server_error(
    message: str = "服务器内部错误",
    data: Any = None
) -> JSONResponse:
    """服务器错误"""
    return create_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        message,
        data,
        status.HTTP_500_INTERNAL_SERVER_ERROR
    ) 