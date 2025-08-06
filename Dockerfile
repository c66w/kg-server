FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p knowledge_bases logs

# 设置服务环境变量
ENV PORT=6408
ENV HOST=0.0.0.0

# 暴露端口（默认6408，可通过环境变量覆盖）
EXPOSE ${PORT}

# 启动命令
CMD ["sh", "-c", "gunicorn main:app -c gunicorn.conf.py --bind ${HOST}:${PORT}"] 