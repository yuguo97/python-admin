# 系统监控服务 (System Service)

集中式电脑配置统计系统,采用"终端采集 + 中心平台"架构,实现企业内所有电脑硬件和软件配置的统一管理。

## 功能特性

### 中心平台 (Server)

- ✅ 系统信息监控 (CPU、内存、磁盘、网络)
- ✅ 进程和服务监控
- ✅ 设备配置管理
- ✅ 设备信息采集和存储
- ✅ 设备查询和统计
- ✅ RESTful API
- ✅ Swagger API 文档
- ✅ 链路追踪 (OpenTelemetry)

### 采集端 (Agent)

- ✅ 跨平台支持 (Windows/Linux/macOS)
- ✅ 硬件信息采集 (CPU、内存、磁盘、网卡)
- ✅ 操作系统信息
- ✅ 软件清单 (Windows)
- ✅ 设备唯一标识
- ✅ 自动上报到中心平台
- ✅ 支持定时循环采集
- ✅ 可打包为独立可执行文件

## 快速开始

### 1. 启动中心平台

```bash
cd system_service
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

访问 API 文档: http://localhost:8002/docs

### 2. 运行 Agent

```bash
# 安装依赖
pip install -r requirements-agent.txt

# 单次采集
python agent.py --server http://localhost:8002 --token your-token

# 循环采集 (每30分钟)
python agent.py --server http://localhost:8002 --token your-token --interval 30
```

### 3. 查看设备信息

```bash
curl -X POST http://localhost:8002/devices/query \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"page": 1, "page_size": 20}'
```

详细说明请查看 [快速开始指南](QUICKSTART.md)

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        中心平台 (Server)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  FastAPI     │  │   MongoDB    │  │    Redis     │      │
│  │  (REST API)  │  │  (数据存储)   │  │   (缓存)     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ HTTP/HTTPS
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
   │ Agent 1 │         │ Agent 2 │        │ Agent N │
   │(Windows)│         │ (Linux) │        │  (Mac)  │
   └─────────┘         └─────────┘        └─────────┘
   采集 + 上报         采集 + 上报         采集 + 上报
```

## 项目结构

```
system_service/
├── app/
│   ├── main.py              # FastAPI 主应用
│   ├── system_info.py       # 系统信息采集
│   ├── device_service.py    # 设备管理服务
│   ├── models.py            # 数据模型
│   └── database.py          # 数据库连接
├── agent.py                 # 采集端脚本
├── build_agent.py           # Agent 打包脚本
├── run-agent.bat            # Windows 启动脚本
├── run-agent.sh             # Linux 启动脚本
├── systemd-examples/        # Systemd 配置示例
│   ├── device-agent.service
│   └── device-agent.timer
├── requirements.txt         # 服务端依赖
├── requirements-agent.txt   # Agent 依赖
├── README.md                # 本文件
├── QUICKSTART.md            # 快速开始指南
└── DEPLOYMENT.md            # 详细部署文档
```

## API 接口

### 设备管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /devices/report | 设备上报 (Agent调用) |
| POST | /devices/query | 查询设备列表 |
| GET | /devices/{device_id} | 获取设备详情 |
| GET | /devices/statistics/summary | 获取统计信息 |
| DELETE | /devices/{device_id} | 删除设备 |

### 系统监控

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /system | 获取完整系统信息 |
| GET | /system/cpu | 获取CPU信息 |
| GET | /system/memory | 获取内存信息 |
| GET | /system/disk | 获取磁盘信息 |
| GET | /system/network | 获取网络信息 |
| GET | /system/processes | 获取进程信息 |
| GET | /system/services | 获取服务状态 |

完整 API 文档: http://your-server:8002/docs

## 采集信息

Agent 会采集以下信息:

### 基础信息
- 设备唯一标识 (UUID)
- 主板序列号
- 主机名

### 操作系统
- 系统类型 (Windows/Linux/macOS)
- 版本号
- 架构
- 启动时间

### 硬件信息
- **CPU**: 型号、核心数、频率
- **内存**: 总容量、类型
- **磁盘**: 设备、容量、使用率
- **网卡**: IP地址、MAC地址、状态

### 软件信息 (Windows)
- 已安装软件列表
- 软件版本

## 部署方式

### Agent 部署

#### 1. Python 脚本
适用于测试环境,需要 Python 环境。

#### 2. 可执行文件
使用 PyInstaller 打包为独立 exe/binary,无需 Python 环境。

```bash
python build_agent.py
```

#### 3. 定时任务

**Windows:**
- 任务计划程序
- GPO (组策略)
- Ansible/Salt

**Linux:**
- Cron
- Systemd Timer

详细部署方式请查看 [部署文档](DEPLOYMENT.md)

## 配置说明

### 环境变量

```bash
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=admin_db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
```

### Agent 参数

```bash
python agent.py \
  --server http://your-server:8002 \  # 服务器地址
  --token your-token \                # 认证Token
  --timeout 30 \                      # 超时时间(秒)
  --interval 30                       # 采集间隔(分钟)
```

## 开发指南

### 安装开发依赖

```bash
pip install -r requirements.txt
pip install -r requirements-agent.txt
```

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black .
isort .
```

### 启动开发服务器

```bash
uvicorn app.main:app --reload --port 8002
```

## 性能优化

- **缓存**: 使用 Redis 缓存系统信息和统计数据
- **索引**: MongoDB 为常用查询字段创建索引
- **采集频率**: 建议 30-60 分钟采集一次
- **数据保留**: 定期清理过期历史数据

## 安全建议

1. 使用 HTTPS 加密通信
2. 定期更换认证 Token
3. 限制 API 访问来源
4. 启用防火墙规则
5. 定期审计日志

## 监控告警

可扩展以下告警功能:

- 设备离线告警
- 磁盘空间不足
- 内存使用率过高
- 新设备上线通知

## 数据导出

支持导出为:

- Excel 表格
- CSV 文件
- PDF 报告

## 技术栈

### 服务端
- FastAPI - Web 框架
- MongoDB - 数据存储
- Redis - 缓存
- Motor - 异步 MongoDB 驱动
- OpenTelemetry - 链路追踪

### Agent
- psutil - 系统信息采集
- requests - HTTP 请求
- wmi (Windows) - Windows 管理接口
- dmidecode (Linux) - 硬件信息

## 常见问题

**Q: Agent 需要管理员权限吗?**

A: Windows 建议以管理员运行,Linux 某些信息需要 root 权限。

**Q: 如何批量部署?**

A: 可使用 GPO、Ansible、Salt 等工具批量部署。

**Q: 数据多久上报一次?**

A: 建议 30 分钟,可通过 `--interval` 参数调整。

**Q: 支持哪些操作系统?**

A: Windows、Linux、macOS 均支持。

**Q: 如何查看运行状态?**

A: 查看 `agent.log` 日志或在中心平台查看最后上报时间。

## 文档

- [快速开始指南](QUICKSTART.md) - 5分钟快速部署
- [部署文档](DEPLOYMENT.md) - 详细部署说明
- [API 文档](http://your-server:8002/docs) - Swagger UI

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request!

## 更新日志

### v1.0.0 (2024-01-01)
- ✅ 初始版本发布
- ✅ 支持设备信息采集
- ✅ 支持中心平台管理
- ✅ 支持跨平台部署
- ✅ 支持统计分析

## 联系方式

如有问题,请查看:
- 项目文档
- API 文档: http://your-server:8002/docs
- 日志文件: `agent.log`
