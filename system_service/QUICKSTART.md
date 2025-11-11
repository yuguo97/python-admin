# 快速开始指南

## 5分钟快速部署

### 步骤 1: 启动中心平台

```bash
cd system_service

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

访问 http://localhost:8002/docs 确认服务正常运行。

### 步骤 2: 获取认证Token

从管理后台获取 API Token,或使用测试 Token。

### 步骤 3: 部署Agent (选择一种方式)

#### 方式A: 直接运行Python脚本 (测试推荐)

```bash
# 安装依赖
pip install -r requirements-agent.txt

# 运行Agent
python agent.py --server http://localhost:8002 --token your-token
```

#### 方式B: 使用批处理/Shell脚本

**Windows:**

1. 编辑 `run-agent.bat`,修改 `SERVER_URL` 和 `TOKEN`
2. 双击运行 `run-agent.bat`

**Linux:**

1. 编辑 `run-agent.sh`,修改 `SERVER_URL` 和 `TOKEN`
2. 添加执行权限: `chmod +x run-agent.sh`
3. 运行: `./run-agent.sh`

#### 方式C: 打包为可执行文件 (生产推荐)

```bash
# 打包
python build_agent.py

# Windows运行
dist\device-agent.exe --server http://localhost:8002 --token your-token

# Linux运行
./dist/device-agent --server http://localhost:8002 --token your-token
```

### 步骤 4: 查看设备信息

访问 API 查询设备:

```bash
curl -X POST http://localhost:8002/devices/query \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"page": 1, "page_size": 20}'
```

或访问 http://localhost:8002/docs 使用 Swagger UI 测试。

### 步骤 5: 查看统计信息

```bash
curl http://localhost:8002/devices/statistics/summary \
  -H "Authorization: Bearer your-token"
```

## 定时采集配置

### Windows 任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 名称: "设备信息采集"
4. 触发器: 每天,重复间隔 30 分钟
5. 操作: 启动程序
   - 程序: `C:\path\to\device-agent.exe`
   - 参数: `--server http://your-server:8002 --token your-token`

### Linux Cron

```bash
# 编辑crontab
crontab -e

# 添加定时任务 (每30分钟)
*/30 * * * * /usr/local/bin/device-agent --server http://your-server:8002 --token your-token
```

### Linux Systemd

```bash
# 复制服务文件
sudo cp systemd-examples/device-agent.service /etc/systemd/system/
sudo cp systemd-examples/device-agent.timer /etc/systemd/system/

# 修改服务文件中的服务器地址和Token
sudo nano /etc/systemd/system/device-agent.service

# 启用并启动定时器
sudo systemctl daemon-reload
sudo systemctl enable device-agent.timer
sudo systemctl start device-agent.timer

# 查看状态
sudo systemctl status device-agent.timer
```

## API 使用示例

### 查询所有 Windows 设备

```bash
curl -X POST http://localhost:8002/devices/query \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "os_system": "Windows",
    "page": 1,
    "page_size": 20
  }'
```

### 查询指定主机名

```bash
curl -X POST http://localhost:8002/devices/query \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "PC-001",
    "page": 1,
    "page_size": 20
  }'
```

### 获取设备详情

```bash
curl http://localhost:8002/devices/{device_id} \
  -H "Authorization: Bearer your-token"
```

### 获取统计信息

```bash
curl http://localhost:8002/devices/statistics/summary \
  -H "Authorization: Bearer your-token"
```

返回示例:

```json
{
  "code": 200,
  "data": {
    "total_devices": 50,
    "os_distribution": {
      "Windows": 35,
      "Linux": 15
    },
    "cpu_distribution": {
      "4核": 20,
      "8核": 25,
      "16核": 5
    },
    "memory_distribution": {
      "8GB": 15,
      "16GB": 25,
      "32GB": 10
    },
    "online_devices": 45,
    "offline_devices": 5
  }
}
```

## 批量部署

### 使用 Ansible

创建 playbook `deploy-agent.yml`:

```yaml
---
- name: Deploy Device Agent
  hosts: all
  become: yes
  tasks:
    - name: Copy agent binary
      copy:
        src: dist/device-agent
        dest: /usr/local/bin/device-agent
        mode: '0755'
    
    - name: Copy systemd service
      copy:
        src: systemd-examples/device-agent.service
        dest: /etc/systemd/system/device-agent.service
    
    - name: Copy systemd timer
      copy:
        src: systemd-examples/device-agent.timer
        dest: /etc/systemd/system/device-agent.timer
    
    - name: Enable and start timer
      systemd:
        name: device-agent.timer
        enabled: yes
        state: started
        daemon_reload: yes
```

执行部署:

```bash
ansible-playbook -i inventory.ini deploy-agent.yml
```

### 使用 GPO (Windows)

1. 将 `device-agent.exe` 和 `run-agent.bat` 放到域共享文件夹
2. 创建 GPO: "计算机配置 → 首选项 → 控制面板设置 → 计划任务"
3. 新建计划任务:
   - 名称: DeviceAgent
   - 操作: 运行 `\\server\share\run-agent.bat`
   - 触发器: 每天,重复间隔 30 分钟
4. 链接 GPO 到目标 OU

## 故障排查

### Agent 无法连接服务器

```bash
# 测试网络连接
ping your-server
telnet your-server 8002

# 查看日志
cat agent.log
```

### 查看服务器日志

```bash
# 查看系统服务日志
tail -f logs/system.log

# 查看MongoDB数据
mongo
use admin_db
db.devices.find().pretty()
```

### 验证数据上报

```bash
# 查看最近上报的设备
curl -X POST http://localhost:8002/devices/query \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"page": 1, "page_size": 10}' | jq
```

## 下一步

- 详细部署文档: [DEPLOYMENT.md](DEPLOYMENT.md)
- API 文档: http://your-server:8002/docs
- 配置定时采集任务
- 设置告警规则
- 导出设备清单报表
