from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from models.user import User
from utils import APIResponse

user_bp = Blueprint('user', __name__)

@user_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        # 构建查询
        query = User.query
        
        # 如果有搜索关键词，添加搜索条件
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.username.like(search_term)) |
                (User.email.like(search_term)) |
                (User.phone.like(search_term))
            )
        
        # 执行分页查询
        pagination = query.order_by(User.created_at.desc()).paginate(
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
    except Exception as e:
        current_app.logger.error(f"Fetch users error: {str(e)}")
        return APIResponse.error(str(e))

@user_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    """获取单个用户"""
    try:
        user = User.query.get_or_404(id)
        return APIResponse.success(user.to_dict())
    except Exception as e:
        return APIResponse.error(str(e))

@user_bp.route('', methods=['POST'])
@jwt_required()
def create_user():
    """创建用户"""
    try:
        current_app.logger.info("Received create user request")
        data = request.get_json()
        
        # 记录请求数据
        current_app.logger.debug(f"Create user data: {data}")
        
        # 检查必要参数
        required_fields = ['username', 'password']
        for field in required_fields:
            if not data.get(field):
                current_app.logger.warning(f"Missing required field: {field}")
                return APIResponse.error(f'缺少必要参数: {field}')
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=data.get('username')).first():
            current_app.logger.warning(f"Username already exists: {data.get('username')}")
            return APIResponse.error('用户名已存在')
        
        # 创建用户
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            phone=data.get('phone'),
            status=data.get('status', 1),
            remark=data.get('remark')
        )
        user.set_password(data.get('password'))
        
        try:
            user.save()
            current_app.logger.info(f"User created successfully: {user.username}")
            return APIResponse.success(user.to_dict(), '创建成功')
        except Exception as e:
            current_app.logger.error(f"Database error while creating user: {str(e)}")
            return APIResponse.error('数据库错误')
            
    except Exception as e:
        current_app.logger.error(f"Create user error: {str(e)}")
        return APIResponse.error(str(e))

@user_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    """更新用户"""
    try:
        user = User.query.get_or_404(id)
        data = request.get_json()
        
        # 检查用户名是否已被其他用户使用
        if 'username' in data and data['username'] != user.username:
            if User.query.filter_by(username=data['username']).first():
                return APIResponse.error('用户名已存在')
        
        # 更新用户信息
        for key, value in data.items():
            if key == 'password':
                user.set_password(value)
            elif hasattr(user, key):
                setattr(user, key, value)
        
        user.save()
        return APIResponse.success(user.to_dict(), '更新成功')
    except Exception as e:
        current_app.logger.error(f"Update user error: {str(e)}")
        return APIResponse.error(str(e))

@user_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    """删除用户"""
    try:
        user = User.query.get_or_404(id)
        
        # 不允许删除管理员用户
        if user.username == 'admin':
            return APIResponse.error('不能删除管理员用户')
        
        user.delete()
        return APIResponse.success(message='删除成功')
    except Exception as e:
        current_app.logger.error(f"Delete user error: {str(e)}")
        return APIResponse.error(str(e)) 