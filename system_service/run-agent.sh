#!/bin/bash
# 设备信息采集Agent启动脚本
# 请修改以下配置

# 中心平台地址
SERVER_URL="http://your-server:8002"

# 认证Token
TOKEN="your-token"

# 采集间隔(分钟), 0表示只执行一次
INTERVAL=30

# ========================================
# 以下内容无需修改
# ========================================

echo "===================================="
echo "设备信息采集Agent"
echo "===================================="
echo "服务器: $SERVER_URL"
echo "间隔: $INTERVAL 分钟"
echo "===================================="
echo ""

# 检查是否存在Python3
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3,请先安装Python3"
    exit 1
fi

# 检查agent.py是否存在
if [ ! -f "agent.py" ]; then
    echo "[错误] 未找到agent.py文件"
    exit 1
fi

# 运行Agent
echo "[信息] 启动Agent..."
python3 agent.py --server "$SERVER_URL" --token "$TOKEN" --interval "$INTERVAL"

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] Agent运行失败"
    exit 1
fi

echo ""
echo "[完成] Agent已退出"
