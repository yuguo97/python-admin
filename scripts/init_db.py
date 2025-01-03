import pymysql
from dotenv import load_dotenv
import os
import sys

def init_database():
    """初始化数据库"""
    # 加载环境变量
    load_dotenv()
    
    # 获取数据库配置
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = int(os.getenv('MYSQL_PORT', 3306))
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '123456')
    database = os.getenv('MYSQL_DATABASE', 'user_management')
    
    try:
        # 先尝试不指定数据库连接
        print(f"正在连接 MySQL ({user}@{host})...")
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        print("MySQL 连接成功")
        
        with conn.cursor() as cursor:
            # 检查数据库是否存在
            cursor.execute("SHOW DATABASES LIKE %s", (database,))
            exists = cursor.fetchone()
            
            if not exists:
                print(f"正在创建数据库 {database}...")
                cursor.execute(
                    f"CREATE DATABASE {database} "
                    "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
                print(f"数据库 {database} 创建成功")
            else:
                print(f"数据库 {database} 已存在")
            
            # 使用数据库
            cursor.execute(f"USE {database}")
            
            # 检查用户权限
            cursor.execute("SHOW GRANTS FOR %s@%s", (user, 'localhost'))
            grants = cursor.fetchall()
            print("\n当前用户权限:")
            for grant in grants:
                print(grant[0])
            
        conn.commit()
        print("\n数据库初始化完成")
        return True
        
    except pymysql.Error as e:
        error_code = e.args[0]
        error_msg = e.args[1]
        print(f"\n数据库错误 ({error_code}): {error_msg}")
        
        if error_code == 1045:  # Access denied
            print("\n解决方案:")
            print("1. 检查 MySQL root 密码是否正确")
            print("2. 在 MySQL 中执行:")
            print("   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123456';")
            print("   FLUSH PRIVILEGES;")
        
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    success = init_database()
    if not success:
        sys.exit(1) 