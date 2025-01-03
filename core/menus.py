from models.menu import Menu, db
from flask import current_app

class MenuService:
    @staticmethod
    def get_menu_tree():
        """获取菜单树"""
        try:
            # 获取所有启用的菜单
            menus = Menu.query.filter_by(status=1).order_by(Menu.sort.asc()).all()
            
            # 构建菜单树
            menu_dict = {menu.id: menu.to_dict() for menu in menus}
            menu_tree = []
            
            for menu_id, menu in menu_dict.items():
                if menu['parent_id'] == 0:
                    menu['children'] = []
                    menu_tree.append(menu)
                else:
                    parent = menu_dict.get(menu['parent_id'])
                    if parent:
                        if 'children' not in parent:
                            parent['children'] = []
                        parent['children'].append(menu)
            
            return menu_tree
            
        except Exception as e:
            current_app.logger.error(f"Get menu tree error: {str(e)}")
            raise e

    @staticmethod
    def create_menu(data):
        """创建菜单"""
        try:
            # 检查必填字段
            required_fields = ['name', 'path']
            for field in required_fields:
                if not data.get(field):
                    raise ValueError(f"缺少必填字段: {field}")
            
            # 检查路径唯一性
            if Menu.query.filter_by(path=data['path']).first():
                raise ValueError("菜单路径已存在")
            
            # 创建菜单
            menu = Menu(
                parent_id=data.get('parent_id', 0),
                name=data['name'],
                path=data['path'],
                component=data.get('component', ''),
                icon=data.get('icon', ''),
                sort=data.get('sort', 0),
                status=data.get('status', 1),
                is_show=data.get('is_show', True)
            )
            
            db.session.add(menu)
            db.session.commit()
            return menu
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Create menu error: {str(e)}")
            raise e

    @staticmethod
    def update_menu(menu_id, data):
        """更新菜单"""
        try:
            menu = Menu.query.get(menu_id)
            if not menu:
                return None
            
            # 检查路径唯一性
            if 'path' in data:
                existing = Menu.query.filter_by(path=data['path']).first()
                if existing and existing.id != menu_id:
                    raise ValueError("菜单路径已存在")
            
            # 更新字段
            allowed_fields = [
                'parent_id', 'name', 'path', 'component',
                'icon', 'sort', 'status', 'is_show'
            ]
            
            for field in allowed_fields:
                if field in data:
                    setattr(menu, field, data[field])
            
            db.session.commit()
            return menu
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Update menu error: {str(e)}")
            raise e

    @staticmethod
    def delete_menu(menu_id):
        """删除菜单"""
        try:
            menu = Menu.query.get(menu_id)
            if not menu:
                return False
            
            # 检查是否有子菜单
            if Menu.query.filter_by(parent_id=menu_id).first():
                raise ValueError("该菜单下有子菜单，不能删除")
            
            db.session.delete(menu)
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Delete menu error: {str(e)}")
            raise e

    @staticmethod
    def get_menu_by_id(menu_id):
        """根据ID获取菜单"""
        try:
            menu = Menu.query.get(menu_id)
            return menu.to_dict() if menu else None
        except Exception as e:
            current_app.logger.error(f"Get menu error: {str(e)}")
            raise e 