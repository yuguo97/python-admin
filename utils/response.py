from flask import jsonify
from utils.error_codes import ErrorCode

class APIResponse:
    """API响应格式化工具"""
    
    @staticmethod
    def success(data=None, message='success', code=200):
        """
        成功响应
        :param data: 响应数据
        :param message: 响应消息
        :param code: 响应码
        """
        response = {
            'code': code,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return jsonify(response)
    
    @staticmethod
    def error(message='error', code=400, data=None):
        """
        错误响应
        :param message: 错误消息
        :param code: 错误码
        :param data: 错误数据
        """
        response = {
            'code': code,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return jsonify(response)
    
    @staticmethod
    def validation_error(errors):
        """
        参数验证错误响应
        :param errors: 错误信息
        """
        return jsonify({
            'code': ErrorCode.INVALID_PARAMS.code,
            'message': '参数验证失败',
            'data': errors
        })
    
    @staticmethod
    def unauthorized(message='未授权访问'):
        """
        未授权响应
        :param message: 错误消息
        """
        return jsonify({
            'code': ErrorCode.UNAUTHORIZED.code,
            'message': message
        }), 401
    
    @staticmethod
    def forbidden(message='禁止访问'):
        """
        禁止访问响应
        :param message: 错误消息
        """
        return jsonify({
            'code': ErrorCode.PERMISSION_DENIED.code,
            'message': message
        }), 403
    
    @staticmethod
    def not_found(message='资源不存在'):
        """
        资源不存在响应
        :param message: 错误消息
        """
        return jsonify({
            'code': 404,
            'message': message
        }), 404 