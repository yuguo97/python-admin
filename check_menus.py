"""检查菜单数据"""
from admin_service.app.database import SessionLocal
from admin_service.app.menus.models import Menu

db = SessionLocal()
try:
    # 查询所有菜单
    menus = db.query(Menu).order_by(Menu.sort_order).all()
    
    print(f'数据库中共有 {len(menus)} 个菜单:\n')
    
    for menu in menus:
        parent_name = ''
        if menu.parent_id:
            parent = db.query(Menu).filter(Menu.id == menu.parent_id).first()
            if parent:
                parent_name = f' (父菜单: {parent.name})'
        
        print(f'ID: {menu.id}')
        print(f'  编码: {menu.code}')
        print(f'  名称: {menu.name}')
        print(f'  路径: {menu.path}')
        print(f'  组件: {menu.component}')
        print(f'  图标: {menu.icon}')
        print(f'  排序: {menu.sort_order}')
        print(f'  可见: {menu.visible}{parent_name}')
        print()
    
    # 特别检查服务管理菜单
    service_menu = db.query(Menu).filter(Menu.code == 'system:service').first()
    if service_menu:
        print('✅ 找到服务管理菜单')
    else:
        print('❌ 未找到服务管理菜单')
        
finally:
    db.close()
