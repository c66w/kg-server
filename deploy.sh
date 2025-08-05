#!/bin/bash

# 部署脚本
echo "开始部署CSV三元组解析服务..."

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 创建必要的目录
echo "创建必要目录..."
mkdir -p knowledge_bases
mkdir -p logs

# 设置权限
chmod +x deploy.sh

# 启动服务
echo "启动服务..."
echo "请根据你的部署环境选择启动方式："
echo ""
echo "1. 开发环境："
echo "   python main.py"
echo ""
echo "2. 生产环境（使用Gunicorn）："
echo "   gunicorn main:app -c gunicorn.conf.py"
echo ""
echo "3. 后台运行："
echo "   nohup gunicorn main:app -c gunicorn.conf.py > logs/app.log 2>&1 &"
echo ""
echo "4. 使用systemd服务（推荐）："
echo "   请参考下面的systemd配置文件" 