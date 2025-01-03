from flask import jsonify

class APIResponse:
    """API响应格式化工具"""
    
    @staticmethod
    def success(data=None, message='success'):
        return jsonify({
            'code': 200,
            'data': data,
            'message': message
        })
    
    @staticmethod
    def error(message='error', code=400):
        return jsonify({
            'code': code,
            'message': message
        }) 