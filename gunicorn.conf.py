import os

# Gunicorn配置文件
# 从环境变量获取端口，默认为6408
PORT = int(os.getenv('PORT', 6408))
HOST = os.getenv('HOST', '0.0.0.0')

bind = f"{HOST}:{PORT}"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info" 