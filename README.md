# 微服务管理系统

这是一个基于Python FastAPI的微服务系统，包含后台管理、爬虫和系统监控三个服务。

## 功能特点

- 后台管理服务：系统管理和配置
- 爬虫服务：网络小说爬取和管理
- 系统监控服务：实时监控系统状态

## 环境要求

- Python 3.8+
- MySQL 5.7+
- MongoDB 4.0+
- Redis 6.0+

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 初始化数据库：
```bash
python manage.py init-db
```

3. 创建管理员用户：
```bash
python manage.py create-admin
```

4. 启动服务：
```bash
# 启动所有服务
python manage.py start

# 或者启动单个服务
python manage.py start --service admin    # 启动后台管理服务
python manage.py start --service crawler  # 启动爬虫服务
python manage.py start --service system   # 启动系统监控服务
```

## 服务访问

- 后台管理服务：http://localhost:8000
- 爬虫服务：http://localhost:8001
- 系统监控服务：http://localhost:8002

API文档访问：
- 后台管理服务：http://localhost:8000/docs
- 爬虫服务：http://localhost:8001/docs
- 系统监控服务：http://localhost:8002/docs

## 项目结构

```
.
├── admin_service/     # 后台管理服务
├── crawler_service/   # 爬虫服务
├── system_service/    # 系统监控服务
├── services/         # 服务管理模块
├── utils/           # 公共工具
├── static/          # 静态文件
├── scripts/         # 脚本文件
├── logs/           # 日志文件
├── .env            # 环境配置
├── manage.py       # 管理脚本
└── requirements.txt # 项目依赖
```

## 配置说明

主要配置文件：
- `.env`：环境变量配置
- `services/__init__.py`：服务配置
- 各服务模块下的配置文件

## 日志

日志文件位于 `logs/` 目录：
- admin.log：后台管理服务日志
- crawler.log：爬虫服务日志
- system.log：系统监控服务日志
- manage.log：管理脚本日志

## 开发指南

1. 代码规范
   - 遵循PEP 8规范
   - 使用类型注解
   - 编写详细的文档字符串

2. 提交规范
   - feat: 新功能
   - fix: 修复bug
   - docs: 文档更新
   - style: 代码格式调整
   - refactor: 重构
   - test: 测试相关
   - chore: 其他修改

## 许可证

MIT License 