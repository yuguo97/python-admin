from flask import jsonify, request
from flask_jwt_extended import jwt_required
from . import api_bp
from models.user import User
from utils import APIResponse

@api_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = User.query.paginate(
        page=page, 
        per_page=per_page,
        error_out=False
    )
    
    return APIResponse.success({
        'items': [user.to_dict() for user in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })

@api_bp.route('/users/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    """获取单个用户"""
    user = User.query.get_or_404(id)
    return APIResponse.success(user.to_dict())

@api_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """创建用户"""
    data = request.get_json()
    
    if User.query.filter_by(username=data.get('username')).first():
        return APIResponse.error('用户名已存在')
        
    user = User(
        username=data.get('username'),
        email=data.get('email'),
        phone=data.get('phone'),
        status=data.get('status', 1),
        remark=data.get('remark')
    )
    user.set_password(data.get('password', '123456'))
    
    try:
        user.save()
        return APIResponse.success(user.to_dict(), '创建成功')
    except Exception as e:
        return APIResponse.error(str(e))

@api_bp.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    """更新用户"""
    user = User.query.get_or_404(id)
    data = request.get_json()
    
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return APIResponse.error('用户名已存在')
    
    try:
        for key, value in data.items():
            if key == 'password':
                user.set_password(value)
            elif hasattr(user, key):
                setattr(user, key, value)
        
        user.save()
        return APIResponse.success(user.to_dict(), '更新成功')
    except Exception as e:
        return APIResponse.error(str(e))

@api_bp.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    """删除用户"""
    user = User.query.get_or_404(id)
    
    try:
        user.delete()
        return APIResponse.success(message='删除成功')
    except Exception as e:
        return APIResponse.error(str(e))

# ... 其他路由 ... 