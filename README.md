# 微服务管理系统

这是一个基于Python FastAPI的微服务系统，包含后台管理、爬虫、系统监控和AI服务。

## 功能特点

- 后台管理服务：系统管理和配置
- 爬虫服务：网络小说爬取和管理
- 系统监控服务：实时监控系统状态
- AI服务：提供本地大模型对话能力

## 环境要求

- Python 3.8+
- MySQL 5.7+
- MongoDB 4.0+
- Redis 6.0+

## 项目结构

```
.
├── admin_service/     # 后台管理服务
├── crawler_service/   # 爬虫服务
├── system_service/    # 系统监控服务
├── ai_service/        # AI服务
├── gateway/           # API网关
├── utils/             # 公共工具
├── scripts/           # 脚本文件
├── docs/              # 文档
├── logs/              # 日志文件
├── .env               # 环境配置
├── manage.py          # 管理脚本
└── requirements.txt   # 项目依赖
```

## 环境配置
项目使用 `.env` 文件进行环境配置，主要配置项包括：

### 基础配置
```env
# 环境配置
ENV=development
DEBUG=true

# 密钥配置
SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 数据库配置
```env
# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=123456
MYSQL_DATABASE=ai_service

# MongoDB配置
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DATABASE=crawler_service

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 服务配置
```env
# 服务配置
ADMIN_SERVICE_HOST=0.0.0.0
ADMIN_SERVICE_PORT=8000
CRAWLER_SERVICE_HOST=0.0.0.0
CRAWLER_SERVICE_PORT=8001
SYSTEM_SERVICE_HOST=0.0.0.0
SYSTEM_SERVICE_PORT=8002
AI_SERVICE_HOST=0.0.0.0
AI_SERVICE_PORT=8003

# AI服务配置
MODEL_NAME=deepseek-ai/deepseek-coder-1.5b-base
MODEL_MAX_LENGTH=2048
MODEL_TEMPERATURE=0.7
MODEL_TOP_P=0.9

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化数据库
```bash
python manage.py init-db
```

### 3. 创建管理员用户
```bash
python manage.py create-admin
```

### 4. 启动服务
```bash
# 启动所有服务
python manage.py start --service all

# 或者启动单个服务
python manage.py start --service admin    # 启动后台管理服务
python manage.py start --service crawler  # 启动爬虫服务
python manage.py start --service system   # 启动系统监控服务
python manage.py start --service ai      # 启动AI服务
```

## 服务说明

### 服务访问地址
- 后台管理服务：http://localhost:8000
- 爬虫服务：http://localhost:8001
- 系统监控服务：http://localhost:8002
- AI服务：http://localhost:8003

### API文档访问
- 后台管理服务：http://localhost:8000/docs
- 爬虫服务：http://localhost:8001/docs
- 系统监控服务：http://localhost:8002/docs
- AI服务：http://localhost:8003/docs

### AI服务功能

1. 对话接口
   - 同步对话：`POST /chat`
   - 流式对话：`POST /chat/stream`

2. 对话记录管理
   - 查询记录列表：`GET /chat/records`
   - 查询单条记录：`GET /chat/records/{record_id}`
   - 删除记录：`DELETE /chat/records`

3. 数据库表结构
```sql
CREATE TABLE chat_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    prompt TEXT NOT NULL COMMENT '用户输入的问题',
    response TEXT NOT NULL COMMENT 'AI的回复',
    is_stream BOOLEAN DEFAULT FALSE COMMENT '是否为流式对话',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## 日志

日志文件位于 `logs/` 目录：
- admin.log：后台管理服务日志
- crawler.log：爬虫服务日志
- system.log：系统监控服务日志
- manage.log：管理脚本日志

## 开发规范

1. 代码规范
   - 遵循PEP 8规范
   - 使用类型注解
   - 编写详细的文档字符串
   - 编写单元测试
   - 保持代码注释完整

2. 提交规范
   - feat: 新功能
   - fix: 修复bug
   - docs: 文档更新
   - style: 代码格式调整
   - refactor: 重构
   - test: 测试相关
   - chore: 其他修改

## 注意事项
1. AI服务需要较大的内存和显存，建议使用GPU服务器
2. 首次启动时会下载模型文件，需要等待一段时间
3. 建议定期清理对话记录，避免数据库占用过大

## 许可证

MIT License 