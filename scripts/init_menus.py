from app import create_app
from models import db
from models.menu import Menu

def init_menus():
    """初始化菜单数据"""
    app = create_app()
    with app.app_context():
        # 检查是否已存在菜单数据
        if Menu.query.first():
            print("菜单数据已存在，跳过初始化")
            return
        
        # 定义初始菜单数据
        menus = [
            {
                'name': '首页',
                'path': '/dashboard',
                'component': 'Dashboard',
                'icon': 'HomeFilled',
                'sort': 1,
                'is_show': True
            },
            {
                'name': '系统管理',
                'path': '/system',
                'component': 'Layout',
                'icon': 'Setting',
                'sort': 2,
                'is_show': True,
                'children': [
                    {
                        'name': '用户管理',
                        'path': '/system/users',
                        'component': 'UserManagement',
                        'icon': 'User',
                        'sort': 1,
                        'is_show': True
                    },
                    {
                        'name': '菜单管理',
                        'path': '/system/menus',
                        'component': 'MenuManagement',
                        'icon': 'Menu',
                        'sort': 2,
                        'is_show': True
                    }
                ]
            }
        ]
        
        try:
            # 创建菜单
            for menu_data in menus:
                children = menu_data.pop('children', [])
                parent = Menu(**menu_data)
                db.session.add(parent)
                db.session.flush()  # 获取父菜单ID
                
                # 创建子菜单
                for child_data in children:
                    child_data['parent_id'] = parent.id
                    child = Menu(**child_data)
                    db.session.add(child)
            
            db.session.commit()
            print("菜单数据初始化成功")
            
        except Exception as e:
            db.session.rollback()
            print(f"菜单数据初始化失败: {str(e)}")

if __name__ == '__main__':
    init_menus() 