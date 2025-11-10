# API 架构说明

## 架构概览

本项目采用**微服务 + API 网关**的架构模式，前端通过统一的网关访问各个后端微服务。

```
┌─────────────────┐
│   前端应用      │
│  (Electron)     │
└────────┬────────┘
         │
         │ 所有请求
         ▼
┌─────────────────┐
│   API 网关      │
│  (Port: 8999)   │
└────────┬────────┘
         │
         ├──────────┬──────────┬──────────┐
         │          │          │          │
         ▼          ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │ Admin  │ │ System │ │Crawler │ │   AI   │
    │ :8000  │ │ :8002  │ │ :8001  │ │ :8003  │
    └────────┘ └────────┘ └────────┘ └────────┘
```

## 服务端口配置

| 服务名称 | 端口 | 说明 |
|---------|------|------|
| API Gateway | 8999 | 统一网关入口 |
| Admin Service | 8000 | 用户、角色、权限、菜单管理 |
| System Service | 8002 | 系统信息、监控 |
| Crawler Service | 8001 | 爬虫任务管理 |
| AI Service | 8003 | AI 相关功能 |

## 前端配置

### 环境变量配置

**开发环境** (`.env.development`):
```env
VITE_TITLE="后台管理系统"
# 网关地址 - 统一入口（所有微服务通过网关访问）
VITE_GATEWAY_URL="http://localhost:8999"
```

**生产环境** (`.env.production`):
```env
VITE_TITLE="后台管理系统"
# 网关地址 - 统一入口（生产环境应改为实际域名）
VITE_GATEWAY_URL="http://your-domain.com:8999"
```

> **注意**: 只需要配置网关地址，各微服务的路径会自动基于网关地址构建

### API 配置文件

`src/config/api.js` - 统一管理所有 API 配置：
```javascript
// 网关地址（从环境变量读取）
export const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:8999'

// 各微服务路径自动基于网关地址构建
export const API_BASE_URLS = {
  admin: `${GATEWAY_URL}/admin`,
  system: `${GATEWAY_URL}/system`,
  crawler: `${GATEWAY_URL}/crawler`,
  ai: `${GATEWAY_URL}/ai`
}
```

### 服务实例

`src/utils/request.js` 导出了各个微服务的 Axios 实例：
```javascript
import { adminService, systemService, crawlerService, aiService } from '@/utils/request'
```

## API 调用示例

### 1. Admin Service (用户管理)

```javascript
// src/api/user.js
import { adminService } from '@/utils/request'

export function getUserList(skip = 0, limit = 10) {
  return adminService({
    url: '/users',
    method: 'get',
    params: { skip, limit }
  })
}
```

**实际请求路径**: `http://localhost:8999/admin/users`

### 2. System Service (系统信息)

```javascript
// src/api/system.js
import { systemService } from '@/utils/request'

export function getSystemInfo() {
  return systemService({
    url: '/info',
    method: 'get'
  })
}
```

**实际请求路径**: `http://localhost:8999/system/info`

### 3. Crawler Service (爬虫任务)

```javascript
// src/api/crawler.js
import { crawlerService } from '@/utils/request'

export function getCrawlerTasks() {
  return crawlerService({
    url: '/tasks',
    method: 'get'
  })
}
```

**实际请求路径**: `http://localhost:8999/crawler/tasks`

### 4. AI Service (AI 功能)

```javascript
// src/api/ai.js
import { aiService } from '@/utils/request'

export function chatWithAI(message) {
  return aiService({
    url: '/chat',
    method: 'post',
    data: { message }
  })
}
```

**实际请求路径**: `http://localhost:8999/ai/chat`

## 网关路由规则

网关使用以下路由规则转发请求：

```
/{service}/{path}
```

- `{service}`: 服务名称 (admin, system, crawler, ai)
- `{path}`: 具体的 API 路径

**示例**:
- 前端请求: `http://localhost:8999/admin/users`
- 网关转发: `http://localhost:8000/users`

## 优势

### 1. 统一入口
- 所有请求通过网关统一管理
- 便于实施统一的认证、鉴权、限流等策略

### 2. 服务解耦
- 前端不需要知道各个微服务的具体地址
- 微服务可以独立部署和扩展

### 3. 配置简化
- 不再需要 Vite 代理配置
- 环境变量配置更清晰

### 4. 易于维护
- 统一的错误处理
- 统一的日志记录
- 便于监控和调试

## 启动顺序

1. **启动网关服务**:
   ```bash
   python manage.py start gateway
   ```

2. **启动各个微服务**:
   ```bash
   python manage.py start admin
   python manage.py start system
   python manage.py start crawler
   python manage.py start ai
   ```

3. **启动前端**:
   ```bash
   cd electron_admin
   npm run dev
   ```

## 注意事项

1. **网关必须先启动**: 确保网关服务在前端启动前已经运行
2. **CORS 配置**: 网关已配置允许跨域，无需额外配置
3. **认证令牌**: 所有请求会自动携带 Authorization 头
4. **超时设置**: 默认超时时间为 15 秒

## 故障排查

### 问题: 请求超时
- 检查网关服务是否运行: `netstat -ano | findstr :8999`
- 检查目标微服务是否运行
- 查看网关日志: `logs/gateway_*.log`

### 问题: 404 错误
- 确认服务名称正确 (admin, system, crawler, ai)
- 确认 API 路径正确
- 查看网关日志确认路由规则

### 问题: 认证失败
- 检查 token 是否正确
- 确认 Authorization 头是否正确携带
- 查看后端服务日志
