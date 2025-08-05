# Gunicorn配置文件
bind = "0.0.0.0:6408"
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