# 集中式电脑配置统计系统 - 部署指南

## 系统架构

本系统采用"终端采集 + 中心平台"的架构:

- **Agent (采集端)**: 运行在每台电脑上的轻量级采集脚本,负责收集硬件和软件信息
- **Server (中心平台)**: 接收、存储、展示所有设备的配置信息

## 一、中心平台部署

### 1.1 环境要求

- Python 3.8+
- MongoDB 4.0+
- Redis 5.0+

### 1.2 安装依赖

```bash
cd system_service
pip install -r requirements.txt
```

### 1.3 配置

确保 `utils/config.py` 中配置了正确的 MongoDB 和 Redis 连接信息。

### 1.4 启动服务

```bash
# 开发环境
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# 生产环境
uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers 4
```

### 1.5 验证服务

访问 API 文档: `http://your-server:8002/docs`

## 二、Agent 部署

### 2.1 方式一: Python 脚本 (推荐用于测试)

#### 安装依赖

```bash
pip install -r requirements-agent.txt
```

#### Windows 运行

```bash
python agent.py --server http://your-server:8002 --token your-token
```

#### Linux 运行

```bash
# 单次执行
python3 agent.py --server http://your-server:8002 --token your-token

# 循环执行 (每30分钟)
python3 agent.py --server http://your-server:8002 --token your-token --interval 30
```

### 2.2 方式二: 打包为可执行文件 (推荐用于生产)

#### 打包

```bash
# 安装打包工具
pip install pyinstaller

# 执行打包脚本
python build_agent.py
```

打包后的文件位于 `dist/device-agent.exe` (Windows) 或 `dist/device-agent` (Linux)

#### Windows 部署

**方法1: 手动双击运行**

创建批处理文件 `run-agent.bat`:

```batch
@echo off
device-agent.exe --server http://your-server:8002 --token your-token --interval 30
```

**方法2: 任务计划程序**

1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器: 每天或每小时
4. 操作: 启动程序 `device-agent.exe`
5. 参数: `--server http://your-server:8002 --token your-token`

**方法3: GPO (组策略) 批量部署**

1. 将 `device-agent.exe` 和 `run-agent.bat` 放到共享文件夹
2. 创建 GPO,在"计算机配置 → 首选项 → 控制面板设置 → 计划任务"中添加任务
3. 配置任务定期执行 `run-agent.bat`

**方法4: Ansible/Salt 自动化部署**

使用配置管理工具批量部署到多台机器。

#### Linux 部署

**方法1: Cron 定时任务**

编辑 crontab:

```bash
crontab -e
```

添加定时任务 (每30分钟执行一次):

```cron
*/30 * * * * /path/to/device-agent --server http://your-server:8002 --token your-token
```

**方法2: Systemd Timer**

创建服务文件 `/etc/systemd/system/device-agent.service`:

```ini
[Unit]
Description=Device Configuration Agent
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/device-agent --server http://your-server:8002 --token your-token
User=root

[Install]
WantedBy=multi-user.target
```

创建定时器文件 `/etc/systemd/system/device-agent.timer`:

```ini
[Unit]
Description=Device Agent Timer
Requires=device-agent.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=30min

[Install]
WantedBy=timers.target
```

启用并启动:

```bash
systemctl daemon-reload
systemctl enable device-agent.timer
systemctl start device-agent.timer
```

## 三、API 使用说明

### 3.1 设备上报

Agent 自动调用此接口上报数据。

```http
POST /devices/report
Authorization: Bearer your-token
Content-Type: application/json

{
  "device_id": "uuid",
  "serial_number": "SN123456",
  "collected_at": "2024-01-01T00:00:00",
  "os": {...},
  "cpu": {...},
  "memory": {...},
  "disks": [...],
  "networks": [...],
  "software": [...]
}
```

### 3.2 查询设备列表

```http
POST /devices/query
Authorization: Bearer your-token
Content-Type: application/json

{
  "page": 1,
  "page_size": 20,
  "hostname": "PC-001",
  "os_system": "Windows"
}
```

### 3.3 获取设备详情

```http
GET /devices/{device_id}
Authorization: Bearer your-token
```

### 3.4 获取统计信息

```http
GET /devices/statistics/summary
Authorization: Bearer your-token
```

返回:
- 总设备数
- 操作系统分布
- CPU 核心数分布
- 内存容量分布
- 在线/离线设备数

### 3.5 删除设备

```http
DELETE /devices/{device_id}
Authorization: Bearer your-token
```

## 四、配置说明

### 4.1 Agent 参数

| 参数 | 说明 | 必填 | 默认值 |
|------|------|------|--------|
| --server | 中心平台地址 | 是 | - |
| --token | 认证Token | 是 | - |
| --timeout | 请求超时时间(秒) | 否 | 30 |
| --interval | 循环采集间隔(分钟),0表示单次执行 | 否 | 0 |

### 4.2 采集信息

Agent 会采集以下信息:

**基础信息**
- 设备唯一标识 (UUID)
- 主板序列号
- 主机名

**操作系统**
- 系统类型 (Windows/Linux/macOS)
- 版本号
- 架构 (x86/x64/ARM)
- 启动时间

**CPU**
- 型号
- 物理核心数
- 逻辑核心数
- 频率

**内存**
- 总容量
- 类型

**磁盘**
- 设备名称
- 挂载点
- 文件系统
- 总容量/已用/可用
- 使用率

**网卡**
- 网卡名称
- IPv4 地址
- MAC 地址
- 状态 (启用/禁用)

**软件 (仅 Windows)**
- 已安装软件列表
- 软件版本

## 五、故障排查

### 5.1 Agent 无法连接服务器

1. 检查网络连接
2. 确认服务器地址和端口正确
3. 检查防火墙设置
4. 查看 `agent.log` 日志文件

### 5.2 认证失败

1. 确认 Token 正确
2. 检查 Token 是否过期
3. 查看服务器日志

### 5.3 数据未显示

1. 确认 Agent 上报成功 (查看日志)
2. 检查 MongoDB 连接
3. 查询数据库确认数据已存储

### 5.4 Linux 下权限不足

某些信息需要 root 权限:

```bash
sudo python3 agent.py --server http://your-server:8002 --token your-token
```

或者使用 sudo 配置 cron:

```bash
sudo crontab -e
```

## 六、安全建议

1. **使用 HTTPS**: 生产环境建议使用 HTTPS 加密通信
2. **Token 管理**: 定期更换 Token,不同环境使用不同 Token
3. **网络隔离**: 限制只有内网可访问中心平台
4. **访问控制**: 使用防火墙限制访问来源
5. **日志审计**: 定期检查日志,监控异常访问

## 七、性能优化

1. **采集频率**: 根据实际需求调整采集间隔,建议 30-60 分钟
2. **数据保留**: 定期清理过期的历史数据
3. **索引优化**: 为常用查询字段创建索引
4. **缓存策略**: 统计数据可使用 Redis 缓存

## 八、扩展功能

### 8.1 支持其他上报方式

除了 HTTP POST,还可以扩展支持:

- **TCP Socket**: 适用于内网环境
- **MQTT**: 适用于物联网场景
- **WebSocket**: 实时双向通信
- **共享文件**: 适用于无网络环境

### 8.2 告警功能

可以添加告警规则:

- 设备离线告警
- 磁盘空间不足告警
- 内存使用率过高告警
- 新设备上线通知

### 8.3 数据导出

支持导出为:

- Excel 表格
- CSV 文件
- PDF 报告

## 九、常见问题

**Q: Agent 需要管理员权限吗?**

A: Windows 下建议以管理员权限运行以获取完整信息。Linux 下某些信息需要 root 权限。

**Q: 如何批量部署到多台电脑?**

A: 可以使用 GPO、Ansible、Salt、Puppet 等工具批量部署。

**Q: 数据多久上报一次?**

A: 默认单次执行,建议通过定时任务设置为 30 分钟一次。

**Q: 如何查看 Agent 运行状态?**

A: 查看 `agent.log` 日志文件,或在中心平台查看设备最后上报时间。

**Q: 支持跨平台吗?**

A: 是的,Agent 支持 Windows、Linux、macOS。

## 十、联系支持

如有问题,请查看:

- 项目文档: `README.md`
- API 文档: `http://your-server:8002/docs`
- 日志文件: `agent.log` (Agent) 和服务器日志
