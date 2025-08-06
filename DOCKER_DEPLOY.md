# 🐳 Docker部署指南

## 快速开始

### 1. 一键部署（推荐）

```bash
# 克隆项目
git clone <your-repo-url>
cd kg-server

# 一键启动（端口8080）
./docker-run.sh -b -d -p 8080
```

### 2. 使用Docker Compose

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑端口配置
vim .env

# 启动服务
docker-compose up -d
```

## 📋 部署选项

### 端口配置

| 方式 | 外部端口 | 内部端口 | 说明 |
|------|----------|----------|------|
| 默认 | 8080 | 6408 | 推荐配置 |
| 自定义 | 任意 | 6408 | 通过参数指定 |
| 高端口 | 9000+ | 6408 | 避免端口冲突 |

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `EXTERNAL_PORT` | 8080 | 对外暴露的端口 |
| `INTERNAL_PORT` | 6408 | 容器内部端口 |
| `PORT` | 6408 | 应用监听端口 |
| `HOST` | 0.0.0.0 | 应用监听地址 |

## 🚀 部署示例

### 示例1：标准部署
```bash
# 使用默认端口8080
./docker-run.sh -b -d -p 8080

# 访问地址
http://your-server-ip:8080
```

### 示例2：自定义端口
```bash
# 使用端口9000
./docker-run.sh -b -d -p 9000

# 访问地址
http://your-server-ip:9000
```

### 示例3：生产环境部署
```bash
# 使用高端口，后台运行
./docker-run.sh -b -d -p 9090

# 配置防火墙
sudo ufw allow 9090

# 配置反向代理（可选）
# nginx配置指向 localhost:9090
```

### 示例4：多实例部署
```bash
# 实例1：端口8080
./docker-run.sh -b -d -p 8080 -n csv-parser-1

# 实例2：端口8081
./docker-run.sh -b -d -p 8081 -n csv-parser-2

# 实例3：端口8082
./docker-run.sh -b -d -p 8082 -n csv-parser-3
```

## 🔧 管理命令

### 查看服务状态
```bash
# 查看容器状态
docker ps

# 查看日志
docker logs -f csv-triple-parser

# 查看资源使用
docker stats csv-triple-parser
```

### 停止和重启
```bash
# 停止服务
docker stop csv-triple-parser

# 启动服务
docker start csv-triple-parser

# 重启服务
docker restart csv-triple-parser

# 删除容器
docker rm csv-triple-parser
```

### 更新服务
```bash
# 停止现有容器
docker stop csv-triple-parser

# 删除旧容器
docker rm csv-triple-parser

# 重新构建并启动
./docker-run.sh -b -d -p 8080
```

## 📊 监控和日志

### 日志管理
```bash
# 实时查看日志
docker logs -f csv-triple-parser

# 查看最近100行日志
docker logs --tail 100 csv-triple-parser

# 查看错误日志
docker logs csv-triple-parser 2>&1 | grep ERROR
```

### 健康检查
```bash
# 检查服务是否响应
curl http://localhost:8080/api

# 检查健康状态
docker inspect csv-triple-parser | grep Health -A 10
```

## 🔒 安全配置

### 防火墙设置
```bash
# Ubuntu/Debian
sudo ufw allow 8080

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

### 反向代理配置（Nginx）
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🐛 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 检查端口占用
netstat -tulpn | grep :8080

# 使用其他端口
./docker-run.sh -b -d -p 9090
```

#### 2. 权限问题
```bash
# 确保脚本有执行权限
chmod +x docker-run.sh

# 确保目录有写权限
chmod 755 knowledge_bases logs
```

#### 3. 内存不足
```bash
# 查看系统资源
free -h
df -h

# 清理Docker缓存
docker system prune -a
```

#### 4. 网络问题
```bash
# 检查Docker网络
docker network ls

# 检查容器网络
docker inspect csv-triple-parser | grep IPAddress
```

## 📈 性能优化

### 资源限制
```bash
# 限制内存使用
docker run -d \
  --name csv-parser \
  --memory=512m \
  --cpus=1.0 \
  -p 8080:6408 \
  csv-triple-parser
```

### 数据持久化
```bash
# 使用命名卷
docker run -d \
  --name csv-parser \
  -p 8080:6408 \
  -v csv_data:/app/knowledge_bases \
  -v csv_logs:/app/logs \
  csv-triple-parser
```

## 🔄 自动化部署

### 使用脚本自动化
```bash
#!/bin/bash
# deploy.sh

# 停止现有服务
docker stop csv-triple-parser 2>/dev/null
docker rm csv-triple-parser 2>/dev/null

# 拉取最新代码
git pull

# 重新部署
./docker-run.sh -b -d -p 8080

# 发送通知
echo "部署完成: http://$(hostname -I | awk '{print $1}'):8080"
```

### 定时备份
```bash
#!/bin/bash
# backup.sh

# 创建备份目录
mkdir -p backups/$(date +%Y%m%d)

# 备份数据
cp -r knowledge_bases/* backups/$(date +%Y%m%d)/

# 压缩备份
tar -czf backups/backup_$(date +%Y%m%d_%H%M%S).tar.gz backups/$(date +%Y%m%d)/

# 清理旧备份（保留7天）
find backups/ -name "backup_*.tar.gz" -mtime +7 -delete
``` 