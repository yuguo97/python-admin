from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from core.menus import MenuService
from utils import APIResponse
from utils.jwt_utils import admin_required

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('', methods=['GET'])
@jwt_required()
def get_menus():
    """获取菜单树"""
    try:
        # 获取当前用户ID（确保是字符串）
        current_user_id = str(get_jwt_identity())
        current_app.logger.info(f"User {current_user_id} requesting menus")
        
        menus = MenuService.get_menu_tree()
        return APIResponse.success(data=menus)  # 明确指定 data 参数
    except Exception as e:
        current_app.logger.error(f"Get menus error: {str(e)}")
        return APIResponse.error(str(e))

@menu_bp.route('/<int:menu_id>', methods=['GET'])
@jwt_required()
def get_menu(menu_id):
    """获取菜单详情"""
    try:
        menu = MenuService.get_menu_by_id(menu_id)
        if not menu:
            return APIResponse.error('菜单不存在')
        return APIResponse.success(menu)
    except Exception as e:
        return APIResponse.error(str(e))

@menu_bp.route('', methods=['POST'])
@admin_required()
def create_menu():
    """创建菜单"""
    try:
        data = request.get_json()
        menu = MenuService.create_menu(data)
        return APIResponse.success(menu.to_dict(), '创建成功')
    except ValueError as e:
        return APIResponse.error(str(e))
    except Exception as e:
        current_app.logger.error(f"Create menu error: {str(e)}")
        return APIResponse.error('创建失败')

@menu_bp.route('/<int:menu_id>', methods=['PUT'])
@admin_required()
def update_menu(menu_id):
    """更新菜单"""
    try:
        data = request.get_json()
        menu = MenuService.update_menu(menu_id, data)
        if not menu:
            return APIResponse.error('菜单不存在')
        return APIResponse.success(menu.to_dict(), '更新成功')
    except ValueError as e:
        return APIResponse.error(str(e))
    except Exception as e:
        current_app.logger.error(f"Update menu error: {str(e)}")
        return APIResponse.error('更新失败')

@menu_bp.route('/<int:menu_id>', methods=['DELETE'])
@admin_required()
def delete_menu(menu_id):
    """删除菜单"""
    try:
        if MenuService.delete_menu(menu_id):
            return APIResponse.success(message='删除成功')
        return APIResponse.error('菜单不存在')
    except ValueError as e:
        return APIResponse.error(str(e))
    except Exception as e:
        current_app.logger.error(f"Delete menu error: {str(e)}")
        return APIResponse.error('删除失败') 