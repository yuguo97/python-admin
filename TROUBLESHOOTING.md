# 故障排查指南

## 问题1: 登录401错误

### 错误信息
```
INFO: 127.0.0.1:60135 - "POST /auth/login HTTP/1.1" 401 Unauthorized
```

### 原因
- 用户名或密码错误
- 管理员用户未创建
- 密码不匹配

### 解决方案

#### 方案1: 重新创建管理员用户
```bash
python manage.py create-admin
```

默认账号信息:
- 用户名: `admin`
- 密码: `123456`

#### 方案2: 检查数据库
确保MySQL服务已启动,并且数据库已初始化:
```bash
python manage.py init-db
```

#### 方案3: 手动重置密码
如果需要重置密码,可以直接修改数据库或使用Python脚本。

---

## 问题2: 链路追踪错误

### 错误信息
```
Transient error StatusCode.UNAVAILABLE encountered while exporting traces to localhost:4317, retrying in 1s.
```

### 原因
系统尝试连接OpenTelemetry Collector服务(端口4317),但该服务未启动。

### 解决方案

#### 方案1: 禁用链路追踪(推荐)
在 `.env` 文件中添加或修改:
```env
ENABLE_TRACING=false
```

然后重启服务:
```bash
python manage.py start admin
```

#### 方案2: 启动OpenTelemetry Collector
如果需要使用链路追踪功能:

1. 安装并启动OpenTelemetry Collector
2. 确保服务运行在 `localhost:4317`
3. 在 `.env` 文件中设置:
```env
ENABLE_TRACING=true
OTLP_ENDPOINT=http://localhost:4317
```

---

## 问题3: 前端无法连接后端

### 错误信息
```
Network Error
请求失败
```

### 解决方案

1. **确认后端服务已启动**
```bash
python manage.py start admin
```

2. **检查后端地址**
确认后端运行在 `http://localhost:8000`

3. **检查前端配置**
查看 `electron_admin/frontend/.env.development`:
```env
VITE_API_BASE_URL="http://localhost:8000"
```

4. **检查CORS配置**
后端已配置允许所有来源,如果仍有问题,检查 `admin_service/app/main.py` 中的CORS设置。

---

## 问题4: 数据库连接失败

### 错误信息
```
Can't connect to MySQL server
sqlalchemy.exc.OperationalError
```

### 解决方案

1. **启动MySQL服务**
```bash
# Windows
net start mysql

# Linux/Mac
sudo systemctl start mysql
```

2. **检查数据库配置**
查看 `.env` 文件:
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=ai_service
```

3. **创建数据库**
```sql
CREATE DATABASE ai_service CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. **初始化数据库表**
```bash
python manage.py init-db
```

---

## 问题5: 前端依赖安装失败

### 解决方案

1. **清理缓存重新安装**
```bash
cd electron_admin/frontend
rm -rf node_modules
rm package-lock.json
cnpm install
```

2. **使用npm替代cnpm**
```bash
npm install
```

3. **检查Node版本**
确保Node.js版本 >= 14.0.0
```bash
node -v
```

---

## 问题6: 端口被占用

### 错误信息
```
Address already in use
OSError: [Errno 98] Address already in use
```

### 解决方案

1. **查找占用端口的进程**
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

2. **终止进程**
```bash
# Windows
taskkill /PID <进程ID> /F

# Linux/Mac
kill -9 <进程ID>
```

3. **修改端口**
在 `.env` 文件中修改:
```env
ADMIN_SERVICE_PORT=8001
```

---

## 常用命令

### 后端服务
```bash
# 初始化数据库
python manage.py init-db

# 创建管理员
python manage.py create-admin

# 启动所有服务
python manage.py start all

# 启动单个服务
python manage.py start admin
```

### 前端服务
```bash
# 进入前端目录
cd electron_admin/frontend

# 安装依赖
cnpm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

---

## 日志查看

日志文件位置: `logs/`
- `admin.log` - 后台管理服务日志
- `manage.log` - 管理脚本日志

查看实时日志:
```bash
# Windows
type logs\admin.log

# Linux/Mac
tail -f logs/admin.log
```

---

## 获取帮助

如果以上方案都无法解决问题:

1. 查看完整的错误日志
2. 检查所有服务是否正常运行(MySQL, Redis, MongoDB)
3. 确认环境配置文件 `.env` 是否正确
4. 查看API文档: http://localhost:8000/docs
