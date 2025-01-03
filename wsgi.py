from app import create_app
from scripts.init_menus import init_menus

app = create_app('production')

# 初始化菜单数据
init_menus()

if __name__ == '__main__':
    app.run() 