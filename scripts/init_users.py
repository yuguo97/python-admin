from app import create_app
from models.user import User
from models import db

def init_users():
    """初始化用户数据"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查是否已存在管理员用户
            admin = User.query.filter_by(username='admin').first()
            
            if not admin:
                # 创建管理员用户
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    phone='13800138000',
                    status=1,
                    remark='系统管理员'
                )
                admin.set_password('123456')  # 设置初始密码
                
                db.session.add(admin)
                db.session.commit()
                print("管理员用户创建成功")
                
                # 验证密码是否正确设置
                if admin.check_password('123456'):
                    print("密码验证成功")
                else:
                    print("警告：密码验证失败")
            else:
                print("管理员用户已存在")
                
        except Exception as e:
            db.session.rollback()
            print(f"初始化用户失败: {str(e)}")
            raise e

if __name__ == '__main__':
    init_users()