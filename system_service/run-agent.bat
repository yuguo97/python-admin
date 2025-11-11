@echo off
REM 设备信息采集Agent启动脚本
REM 请修改以下配置

REM 中心平台地址
set SERVER_URL=http://your-server:8002

REM 认证Token
set TOKEN=your-token

REM 采集间隔(分钟), 0表示只执行一次
set INTERVAL=30

REM ========================================
REM 以下内容无需修改
REM ========================================

echo ====================================
echo 设备信息采集Agent
echo ====================================
echo 服务器: %SERVER_URL%
echo 间隔: %INTERVAL% 分钟
echo ====================================
echo.

REM 检查是否存在Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python,请先安装Python
    pause
    exit /b 1
)

REM 检查agent.py是否存在
if not exist agent.py (
    echo [错误] 未找到agent.py文件
    pause
    exit /b 1
)

REM 运行Agent
echo [信息] 启动Agent...
python agent.py --server %SERVER_URL% --token %TOKEN% --interval %INTERVAL%

if %errorlevel% neq 0 (
    echo.
    echo [错误] Agent运行失败
    pause
    exit /b 1
)

echo.
echo [完成] Agent已退出
pause
