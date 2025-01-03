import os
from app import create_app
from scripts.init_menus import init_menus
from scripts.init_users import init_users

# 检查数据库文件是否存在
if not os.path.exists('app.db'):
    print("Creating new database file...")
else:
    print("Using existing database file...")

app = create_app()

if __name__ == '__main__':
    # 初始化数据
    init_users()  # 初始化用户
    init_menus()  # 初始化菜单
    
    # 启动应用
    app.run(debug=True)