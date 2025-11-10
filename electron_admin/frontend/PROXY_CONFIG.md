# 前端代理配置说明

## 概述

前端使用 Vite 的代理功能统一所有后端微服务的出口,避免跨域问题,并简化API调用。

## 代理配置

### 开发环境

在 `vite.config.js` 中配置了以下代理:

```javascript
proxy: {
  // Admin Service - 后台管理服务 (端口: 8000)
  '/api/admin': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api\/admin/, '')
  },
  
  // System Service - 系统信息服务 (端口: 8001)
  '/api/system': {
    target: 'http://localhost:8001',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api\/system/, '')
  }
}
```

### 路径映射

| 前端请求路径 | 代理到 | 实际后端地址 |
|------------|--------|-------------|
| `/api/admin/users` | `http://localhost:8000` | `http://localhost:8000/users` |
| `/api/admin/roles` | `http://localhost:8000` | `http://localhost:8000/roles` |
| `/api/system/info` | `http://localhost:8001` | `http://localhost:8001/system/info` |
| `/api/system/cpu` | `http://localhost:8001` | `http://localhost:8001/system/cpu` |

## 使用方法

### 1. Admin Service (默认)

```javascript
import request from '@/utils/request'

// 自动使用 /api/admin 前缀
export function getUsers() {
  return request({
    url: '/users',  // 实际请求: /api/admin/users
    method: 'get'
  })
}
```

### 2. System Service

```javascript
import { systemService } from '@/utils/request'

// 自动使用 /api/system 前缀
export function getSystemInfo() {
  return systemService({
    url: '/system/info',  // 实际请求: /api/system/system/info
    method: 'get'
  })
}
```

## 添加新的微服务

### 1. 在 vite.config.js 中添加代理

```javascript
proxy: {
  // ... 现有配置
  
  // 新的微服务
  '/api/service-name': {
    target: 'http://localhost:port',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api\/service-name/, '')
  }
}
```

### 2. 在 request.js 中创建新的实例

```javascript
// 创建新服务实例
export const newService = axios.create({
  baseURL: '/api/service-name',
  timeout: 15000
})

// 添加拦截器
newService.interceptors.request.use(/* ... */)
newService.interceptors.response.use(/* ... */)
```

### 3. 创建 API 文件

```javascript
// src/api/service-name.js
import { newService } from '@/utils/request'

export function someApi() {
  return newService({
    url: '/endpoint',
    method: 'get'
  })
}
```

## 生产环境

生产环境需要在 Nginx 或其他反向代理中配置相同的路径映射:

```nginx
location /api/admin/ {
    proxy_pass http://admin-service:8000/;
}

location /api/system/ {
    proxy_pass http://system-service:8001/;
}
```

## 优势

1. **统一出口**: 所有API请求通过同一个域名和端口
2. **避免跨域**: 开发环境不需要配置CORS
3. **易于管理**: 集中管理所有微服务的地址
4. **环境隔离**: 开发、测试、生产环境可以使用不同的配置
5. **简化部署**: 生产环境只需配置反向代理即可

## 注意事项

1. 代理配置只在开发环境生效
2. 生产环境需要配置相应的反向代理
3. 修改代理配置后需要重启开发服务器
4. 确保后端服务已启动,否则代理会失败
