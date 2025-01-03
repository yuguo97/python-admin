import multiprocessing
import os

# 监听地址和端口
bind = '0.0.0.0:5000'

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = 'gevent'

# 最大客户端并发数量
worker_connections = 1000

# 进程名称
proc_name = 'gunicorn_app'

# 进程pid记录文件
pidfile = 'logs/gunicorn.pid'

# 访问日志文件
accesslog = 'logs/access.log'

# 错误日志文件
errorlog = 'logs/error.log'

# 日志级别
loglevel = 'info'

# 后台运行
daemon = True

# 重载
reload = True

# 超时时间
timeout = 30

# 保持连接数
keepalive = 2

# 日志格式
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"' 