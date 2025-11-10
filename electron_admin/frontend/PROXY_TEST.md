# 代理测试说明

## 当前配置

- **前端地址**: http://localhost:8081 (注意是8081,不是8080)
- **Admin Service**: http://localhost:8000
- **System Service**: http://localhost:8002

## 代理映射

| 前端请求 | 代理到 | 实际后端地址 |
|---------|--------|-------------|
| `/api/admin/auth/login` | `http://localhost:8000` | `http://localhost:8000/auth/login` |
| `/api/admin/users/me` | `http://localhost:8000` | `http://localhost:8000/users/me` |
| `/api/system/info` | `http://localhost:8002` | `http://localhost:8002/system/info` |

## 测试步骤

1. **确保后端服务运行**
   ```bash
   # Admin Service (端口 8000)
   python manage.py start admin
   
   # System Service (端口 8002)
   python manage.py start system
   ```

2. **确保前端服务运行**
   ```bash
   cd electron_admin/frontend
   npm run dev
   ```
   应该显示: `Local: http://localhost:8081/`

3. **访问前端**
   在浏览器中打开: **http://localhost:8081**
   
   ⚠️ 注意: 必须是 8081,不是 8080!

4. **测试登录**
   - 用户名: `admin`
   - 密码: `123456`

## 验证代理是否工作

打开浏览器开发者工具 (F12) -> Network 标签:

### ✅ 正确的请求 (代理工作)
```
Request URL: http://localhost:8081/api/admin/auth/login
Status: 200 OK
```

### ❌ 错误的请求 (代理未工作)
```
Request URL: http://localhost:8000/auth/login
Status: timeout / CORS error
```

## 常见问题

### 1. 端口被占用
如果 8080 端口被占用,Vite 会自动使用 8081。
请确保访问正确的端口。

### 2. 代理不生效
- 清除浏览器缓存
- 硬刷新页面 (Ctrl + Shift + R)
- 重启前端开发服务器

### 3. CORS 错误
如果看到 CORS 错误,说明没有使用代理,直接访问了后端。
请确保:
- 访问 http://localhost:8081 (不是 8080)
- baseURL 配置为 `/api/admin`

## 当前状态

✅ Admin Service: 运行在 8000
✅ System Service: 运行在 8002  
✅ Frontend: 运行在 8081
✅ 代理配置: 已配置

请访问: **http://localhost:8081** 进行测试
