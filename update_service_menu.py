"""更新服务管理菜单配置"""
from admin_service.app.database import SessionLocal
from admin_service.app.menus.models import Menu

def update_service_menu():
    db = SessionLocal()
    try:
        # 查找旧的服务管理菜单
        old_menu = db.query(Menu).filter(Menu.code == 'app:services').first()
        
        if old_menu:
            # 获取系统管理菜单的ID
            system_menu = db.query(Menu).filter(Menu.code == 'system').first()
            
            if system_menu:
                # 更新服务管理菜单
                old_menu.code = 'system:service'
                old_menu.name = '服务管理'
                old_menu.path = '/system/services'
                old_menu.component = 'system/Services'
                old_menu.parent_id = system_menu.id
                
                db.commit()
                print('✅ 已成功更新服务管理菜单')
                print(f'   - 编码: {old_menu.code}')
                print(f'   - 路径: {old_menu.path}')
                print(f'   - 组件: {old_menu.component}')
                print(f'   - 父菜单: system')
            else:
                print('❌ 未找到系统管理菜单')
        else:
            # 如果没有旧菜单，创建新菜单
            system_menu = db.query(Menu).filter(Menu.code == 'system').first()
            if system_menu:
                new_menu = Menu(
                    code='system:service',
                    name='服务管理',
                    path='/system/services',
                    component='system/Services',
                    icon='Monitor',
                    parent_id=system_menu.id,
                    sort_order=5,
                    visible=1
                )
                db.add(new_menu)
                db.commit()
                print('✅ 已创建新的服务管理菜单')
            else:
                print('❌ 未找到系统管理菜单')
        
        # 显示所有菜单
        print('\n当前所有菜单:')
        all_menus = db.query(Menu).all()
        for menu in all_menus:
            print(f'  - {menu.code}: {menu.name} ({menu.path})')
            
    except Exception as e:
        db.rollback()
        print(f'❌ 更新失败: {str(e)}')
    finally:
        db.close()

if __name__ == '__main__':
    update_service_menu()
