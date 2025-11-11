# 服务管理功能说明

## 概述

服务管理功能允许你通过 Web 界面自由启动、停止和重启微服务,无需手动操作命令行。

## 功能特性

- ✅ **启动服务**: 一键启动已停止的微服务
- ✅ **停止服务**: 安全停止运行中的微服务
- ✅ **重启服务**: 快速重启服务以应用配置更改
- ✅ **实时状态**: 自动刷新服务运行状态
- ✅ **进程管理**: 自动管理服务进程,防止僵尸进程
- ✅ **端口检测**: 智能检测端口占用情况

## 支持的服务

| 服务名称 | 端口 | 描述 | 可操作 |
|---------|------|------|--------|
| Admin Service | 8000 | 后台管理服务 | ❌ (当前服务) |
| System Service | 8002 | 系统信息服务 | ✅ |
| Crawler Service | 8001 | 爬虫服务 | ✅ |
| AI Service | 8003 | AI服务 | ✅ |
| Gateway Service | 8999 | 网关服务 | ✅ |

## 使用方法

### 1. Web 界面操作

1. 登录管理后台
2. 进入 **系统管理 → 服务管理** 页面
3. 查看所有服务的运行状态
4. 点击对应按钮进行操作:
   - **启动**: 启动已停止的服务
   - **停止**: 停止运行中的服务
   - **重启**: 重启运行中的服务
   - **查看**: 打开服务的 API 文档

### 2. 命令行测试

使用测试脚本验证服务管理功能:

```bash
python test_service_manager.py
```

测试脚本提供交互式菜单:
- 查看所有服务状态
- 启动指定服务
- 停止指定服务
- 重启指定服务

## 技术实现

### 服务管理器 (`service_manager.py`)

核心组件,负责:
- 服务进程的启动和停止
- 端口占用检测
- 进程状态监控
- PID 文件管理

### 启动流程

1. 检查服务是否已运行 (端口检测)
2. 构建 uvicorn 启动命令
3. 使用 `subprocess.Popen` 启动后台进程
4. 保存进程 PID 到文件
5. 验证服务启动状态

### 停止流程

1. 根据端口查找进程
2. 发送 `SIGTERM` 信号优雅关闭
3. 等待 5 秒
4. 如果未关闭,强制 `SIGKILL`
5. 清理 PID 文件

### 重启流程

1. 停止服务 (如果运行中)
2. 等待 1 秒
3. 启动服务
4. 验证启动状态

## API 接口

### 获取服务列表

```http
GET /services
Authorization: Bearer {token}
```

返回:
```json
{
  "code": 200,
  "data": [
    {
      "service_name": "system",
      "name": "System Service",
      "port": 8002,
      "description": "系统信息服务",
      "status": "running",
      "pid": 12345,
      "cpu_percent": 2.5,
      "memory_mb": 150.5
    }
  ]
}
```

### 启动服务

```http
POST /services/{service_name}/start
Authorization: Bearer {token}
```

### 停止服务

```http
POST /services/{service_name}/stop
Authorization: Bearer {token}
```

### 重启服务

```http
POST /services/{service_name}/restart
Authorization: Bearer {token}
```

## 配置说明

服务端口配置在 `.env` 文件中:

```env
ADMIN_SERVICE_PORT=8000
SYSTEM_SERVICE_PORT=8002
CRAWLER_SERVICE_PORT=8001
AI_SERVICE_PORT=8003
GATEWAY_SERVICE_PORT=8999
```

## 故障排查

### 问题1: 无法启动服务

**可能原因:**
- 端口已被占用
- Python 环境问题
- 服务代码错误

**解决方法:**
1. 检查端口是否被占用:
   ```bash
   # Windows
   netstat -ano | findstr :8002
   
   # Linux
   lsof -i :8002
   ```

2. 查看服务日志:
   ```bash
   tail -f logs/system.log
   ```

3. 手动启动测试:
   ```bash
   python -m uvicorn system_service.app.main:app --port 8002
   ```

### 问题2: 停止服务失败

**可能原因:**
- 权限不足
- 进程已僵死

**解决方法:**
1. 使用管理员权限运行
2. 手动终止进程:
   ```bash
   # Windows
   taskkill /F /PID {pid}
   
   # Linux
   kill -9 {pid}
   ```

### 问题3: 服务状态不准确

**可能原因:**
- 缓存问题
- 进程异常退出

**解决方法:**
1. 点击"刷新"按钮更新状态
2. 检查 `service_pids.json` 文件
3. 清理僵尸进程

## 安全建议

1. **权限控制**: 只有管理员可以操作服务
2. **操作日志**: 所有操作都会记录日志
3. **保护主服务**: Admin Service 不能被停止
4. **优雅关闭**: 优先使用 SIGTERM,避免数据丢失

## 性能优化

1. **后台启动**: 服务在独立进程中运行,不阻塞主服务
2. **状态缓存**: 服务状态定时刷新,减少检测开销
3. **PID 管理**: 使用文件记录 PID,快速定位进程

## 开发指南

### 添加新服务

1. 在 `service_manager.py` 中添加服务配置:

```python
self.service_config = {
    "new_service": {
        "module": "new_service.app.main:app",
        "port": int(os.getenv("NEW_SERVICE_PORT", 8004)),
        "name": "New Service",
        "description": "新服务描述"
    }
}
```

2. 在 `.env` 中添加端口配置:

```env
NEW_SERVICE_PORT=8004
```

3. 重启 Admin Service

### 扩展功能

可以添加以下功能:
- 服务日志查看
- 服务性能监控
- 自动重启策略
- 服务依赖管理
- 批量操作

## 常见问题

**Q: 为什么 Admin Service 不能停止?**

A: Admin Service 是管理服务本身,停止它会导致无法管理其他服务。

**Q: 服务启动后多久可以访问?**

A: 通常 2-5 秒,具体取决于服务的初始化时间。

**Q: 如何查看服务日志?**

A: 日志文件位于 `logs/` 目录下,按服务名称分类。

**Q: 服务崩溃后会自动重启吗?**

A: 当前版本不支持自动重启,需要手动操作。可以考虑使用 systemd 或 supervisor 实现自动重启。

**Q: 可以同时启动多个服务吗?**

A: 可以,每个服务独立运行,互不影响。

## 更新日志

### v1.0.0 (2024-01-01)
- ✅ 实现服务启动、停止、重启功能
- ✅ 添加服务状态监控
- ✅ 实现进程管理
- ✅ 添加 Web 界面操作
- ✅ 支持 Windows 和 Linux

## 联系支持

如有问题,请查看:
- 项目文档
- 日志文件: `logs/`
- 测试工具: `python test_service_manager.py`
