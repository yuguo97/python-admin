"""测试菜单 API"""
import requests
import json

# 先登录获取 token
login_url = "http://localhost:8000/auth/login"
login_data = {
    "username": "admin",
    "password": "123456"
}

response = requests.post(login_url, data=login_data)
if response.status_code == 200:
    result = response.json()
    token = result.get("data", {}).get("access_token")
    print(f"✅ 登录成功，Token: {token[:20]}...")
    
    # 获取菜单列表
    menu_url = "http://localhost:8000/menus"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    menu_response = requests.get(menu_url, headers=headers)
    if menu_response.status_code == 200:
        menu_result = menu_response.json()
        print(f"\n✅ 获取菜单成功")
        print(f"状态码: {menu_result.get('code')}")
        print(f"消息: {menu_result.get('message')}")
        print(f"\n菜单数据:")
        print(json.dumps(menu_result.get('data'), indent=2, ensure_ascii=False))
    else:
        print(f"❌ 获取菜单失败: {menu_response.status_code}")
        print(menu_response.text)
else:
    print(f"❌ 登录失败: {response.status_code}")
    print(response.text)
