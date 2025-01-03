from enum import Enum

class ErrorCode(Enum):
    """错误类型枚举"""
    
    # 通用错误 (1000-1999)
    UNKNOWN_ERROR = (1000, "未知错误")
    INVALID_PARAMS = (1001, "无效的参数")
    MISSING_PARAMS = (1002, "缺少必要参数")
    DATABASE_ERROR = (1003, "数据库错误")
    
    # 认证相关错误 (2000-2999)
    AUTH_UNAUTHORIZED = (2000, "未认证")
    TOKEN_EXPIRED = (2001, "token已过期")
    TOKEN_INVALID = (2002, "无效的token")
    LOGIN_REQUIRED = (2003, "请先登录")
    
    # 用户相关错误 (3000-3999)
    USER_NOT_FOUND = (3000, "用户不存在")
    USER_ALREADY_EXISTS = (3001, "用户已存在")
    INVALID_USERNAME = (3002, "无效的用户名")
    INVALID_PASSWORD = (3003, "无效的密码")
    INVALID_EMAIL = (3004, "无效的邮箱格式")
    INVALID_PHONE = (3005, "无效的手机号格式")
    WRONG_PASSWORD = (3006, "密码错误")
    ACCOUNT_DISABLED = (3007, "账号已被禁用")
    
    # 权限相关错误 (4000-4999)
    PERMISSION_DENIED = (4000, "权限不足")
    OPERATION_FORBIDDEN = (4001, "禁止的操作")
    
    # HTTP 状态码
    HTTP_SUCCESS = (200, "成功")
    HTTP_UNAUTHORIZED = (401, "未授权")
    HTTP_FORBIDDEN = (403, "禁止访问")
    HTTP_NOT_FOUND = (404, "资源不存在")
    HTTP_SERVER_ERROR = (500, "服务器错误")
    
    # 菜单相关错误 (5000-5999)
    MENU_NOT_FOUND = (5000, "菜单不存在")
    MENU_ALREADY_EXISTS = (5001, "菜单已存在")
    MENU_HAS_CHILDREN = (5002, "菜单下有子菜单")
    
    def __init__(self, code, message):
        self.code = code
        self.message = message 