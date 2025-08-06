# CSV三元组解析服务

支持多知识库的CSV到三元组转换服务，以每个CSV格子作为最小单位。

## 🌟 项目特点

- ✅ **多知识库支持**：支持创建多个独立的知识库空间
- ✅ **超简单使用**：无需配置，直接上传CSV到指定知识库
- ✅ **格子为单位**：每个非空格子都是实体
- ✅ **自动关系生成**：行内相邻格子自动生成关系
- ✅ **表头识别**：自动识别表头生成属性关系
- ✅ **数据持久化**：知识库数据自动保存到本地文件
- ✅ **现代化UI**：美观的Web界面，支持拖拽操作
- ✅ **即开即用**：一行命令启动服务
- ✅ **生产就绪**：支持Docker部署和systemd服务

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
python main.py
```

服务将在 http://localhost:6408 启动

## 📖 使用方式

### 方式1：Web界面（推荐）
启动服务后，直接在浏览器中访问：
```
http://localhost:6408
```

你将看到一个现代化的Web界面，支持：
- 📁 拖拽上传CSV文件
- 🗂️ 知识库管理
- 📊 统计信息查看
- 🔍 三元组可视化浏览

### 方式2：API接口

#### 1. 上传CSV文件到指定知识库
```bash
curl -X POST "http://localhost:6408/parse-csv/company_data" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@employees.csv"
```

#### 2. 查看所有知识库
```bash
curl -X GET "http://localhost:6408/spaces"
```

#### 3. 查看指定知识库的三元组
```bash
curl -X GET "http://localhost:6408/spaces/company_data?limit=50&offset=0"
```

#### 4. 删除知识库
```bash
curl -X DELETE "http://localhost:6408/spaces/company_data"
```

## 🏗️ 部署

### 开发环境
```bash
python main.py
```

### 生产环境
```bash
# 使用Gunicorn
gunicorn main:app -c gunicorn.conf.py

# 后台运行
nohup gunicorn main:app -c gunicorn.conf.py > logs/app.log 2>&1 &
```

### Docker部署（推荐）

#### 方式1：使用Docker Compose（最简单）
```bash
# 1. 复制环境变量文件
cp .env.example .env

# 2. 编辑.env文件，设置端口
# EXTERNAL_PORT=8080  # 对外暴露的端口
# INTERNAL_PORT=6408  # 容器内部端口

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

#### 方式2：使用Docker脚本（功能最全）
```bash
# 1. 构建镜像并启动（端口8080）
./docker-run.sh -b -p 8080

# 2. 后台运行（端口9000）
./docker-run.sh -b -d -p 9000

# 3. 自定义内部端口
./docker-run.sh -p 8080 -i 8000

# 4. 查看帮助
./docker-run.sh --help
```

#### 方式3：直接使用Docker命令
```bash
# 1. 构建镜像
docker build -t csv-triple-parser .

# 2. 运行容器（端口8080）
docker run -d \
  --name csv-parser \
  -p 8080:6408 \
  -e PORT=6408 \
  -e HOST=0.0.0.0 \
  -v $(pwd)/knowledge_bases:/app/knowledge_bases \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  csv-triple-parser

# 3. 查看日志
docker logs -f csv-parser

# 4. 停止服务
docker stop csv-parser
```

### systemd服务
```bash
# 复制服务文件
sudo cp kg-server.service /etc/systemd/system/

# 启用服务
sudo systemctl enable kg-server
sudo systemctl start kg-server
```

## 📊 示例

### 示例CSV
```
姓名,年龄,城市
张三,25,北京
李四,30,上海
王五,28,广州
```

### 生成的三元组示例
```json
{
  "success": true,
  "message": "成功解析出 12 个三元组，已存储到知识库 'company_data'",
  "new_triples": [
    {
      "subject": "张三",
      "predicate": "next_to", 
      "object": "25",
      "type": "row_adjacent",
      "space": "company_data",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total_triples": 150,
  "space_name": "company_data"
}
```

## 🔧 技术栈

- **后端**: FastAPI + Python
- **前端**: HTML + CSS + JavaScript
- **数据处理**: Pandas
- **部署**: Gunicorn + systemd

## 📁 项目结构

```
kg-server/
├── main.py                 # 主应用文件
├── requirements.txt        # Python依赖
├── static/                 # 静态文件
│   └── index.html         # 前端页面
├── knowledge_bases/        # 知识库数据目录
├── gunicorn.conf.py       # Gunicorn配置
├── deploy.sh              # 部署脚本
├── kg-server.service      # systemd服务配置
├── Dockerfile             # Docker镜像配置
├── docker-compose.yml     # Docker Compose配置
├── docker-run.sh          # Docker启动脚本
├── .env.example           # 环境变量示例
├── .github/workflows/     # GitHub Actions
│   └── ci.yml            # CI/CD配置
└── README.md              # 项目说明
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [API文档](API_DOCUMENTATION.md)
- [部署指南](deploy.sh) 