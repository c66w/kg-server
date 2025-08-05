# CSV三元组解析服务 API 文档

## 概述

CSV三元组解析服务是一个支持多知识库的RESTful API服务，能够将CSV文件解析为三元组（主语-谓语-宾语）格式，并支持知识库的创建、查询和管理。

**服务地址**: `http://1.15.95.222:6408`  
**API版本**: v2.0  
**数据格式**: JSON

## 基础信息

### 服务状态
- **运行状态**: 服务运行在 `http://1.15.95.222:6408`
- **健康检查**: `GET /api`
- **Web界面**: `GET /` (重定向到前端页面)

### 数据模型

#### 三元组 (Triple)
```json
{
  "subject": "张三",
  "predicate": "next_to",
  "object": "25",
  "type": "row_adjacent",
  "space": "company_data",
  "created_at": "2024-01-15T10:30:00"
}
```

#### 知识库 (Space)
```json
{
  "name": "company_data",
  "triple_count": 150,
  "created_at": "2024-01-15T10:30:00"
}
```

## API 端点

### 1. 服务信息

#### 获取API信息
```http
GET /api
```

**响应示例**:
```json
{
  "message": "CSV三元组解析服务 - 支持多知识库",
  "version": "2.0",
  "endpoints": {
    "upload": "POST /parse-csv/{space_name}",
    "list_spaces": "GET /spaces",
    "get_triples": "GET /spaces/{space_name}",
    "delete_space": "DELETE /spaces/{space_name}"
  }
}
```

### 2. CSV文件上传与解析

#### 上传CSV文件到指定知识库
```http
POST /parse-csv/{space_name}
```

**路径参数**:
- `space_name` (string, 必需): 知识库名称，如 `company_data`, `product_info`

**请求体**: `multipart/form-data`
- `file` (file, 必需): CSV文件

**响应格式**:
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

**错误响应**:
```json
{
  "success": false,
  "message": "解析失败: 文件格式错误"
}
```

**使用示例**:
```bash
# 使用curl上传文件
curl -X POST "http://1.15.95.222:6408/parse-csv/company_data" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@employees.csv"

# 使用Python requests
import requests

url = "http://1.15.95.222:6408/parse-csv/company_data"
files = {"file": open("employees.csv", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

### 3. 知识库管理

#### 获取所有知识库列表
```http
GET /spaces
```

**响应格式**:
```json
{
  "spaces": [
    {
      "name": "company_data",
      "triple_count": 150,
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "name": "product_info",
      "triple_count": 89,
      "created_at": "2024-01-15T11:00:00"
    }
  ]
}
```

**使用示例**:
```bash
curl -X GET "http://1.15.95.222:6408/spaces"
```

#### 获取指定知识库的三元组
```http
GET /spaces/{space_name}
```

**路径参数**:
- `space_name` (string, 必需): 知识库名称

**查询参数**:
- `limit` (integer, 可选): 返回结果数量限制，默认100，最大1000
- `offset` (integer, 可选): 分页偏移量，默认0

**响应格式**:
```json
{
  "space_name": "company_data",
  "total_count": 150,
  "limit": 100,
  "offset": 0,
  "triples": [
    {
      "subject": "张三",
      "predicate": "next_to",
      "object": "25",
      "type": "row_adjacent",
      "space": "company_data",
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "subject": "张三",
      "predicate": "has_property",
      "object": "姓名",
      "type": "header_relation",
      "space": "company_data",
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

**使用示例**:
```bash
# 获取前50个三元组
curl -X GET "http://1.15.95.222:6408/spaces/company_data?limit=50"

# 获取第51-100个三元组
curl -X GET "http://1.15.95.222:6408/spaces/company_data?limit=50&offset=50"
```

#### 删除知识库
```http
DELETE /spaces/{space_name}
```

**路径参数**:
- `space_name` (string, 必需): 要删除的知识库名称

**响应格式**:
```json
{
  "success": true,
  "message": "知识库 'company_data' 已删除"
}
```

**错误响应**:
```json
{
  "detail": "知识库 'company_data' 不存在"
}
```

**使用示例**:
```bash
curl -X DELETE "http://1.15.95.222:6408/spaces/company_data"
```

## 三元组生成规则

### 1. 行内相邻关系
对于CSV中的每一行，相邻的格子会生成 `next_to` 关系：
```
张三,25,北京,工程师
```
生成的三元组：
- `(张三, next_to, 25)`
- `(25, next_to, 北京)`
- `(北京, next_to, 工程师)`

### 2. 表头属性关系
如果CSV第一行是表头，数据行中的每个值会与对应的表头生成 `has_property` 关系：
```
姓名,年龄,城市,职业
张三,25,北京,工程师
```
生成的三元组：
- `(张三, has_property, 姓名)`
- `(25, has_property, 年龄)`
- `(北京, has_property, 城市)`
- `(工程师, has_property, 职业)`

## 错误码说明

| HTTP状态码 | 说明 |
|-----------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误或文件格式错误 |
| 404 | 资源不存在（如知识库不存在） |
| 500 | 服务器内部错误 |

## 使用示例

### 完整工作流程

1. **创建知识库并上传数据**
```bash
# 上传员工数据
curl -X POST "http://1.15.95.222:6408/parse-csv/company_data" \
     -F "file=@employees.csv"

# 上传产品数据
curl -X POST "http://1.15.95.222:6408/parse-csv/product_info" \
     -F "file=@products.csv"
```

2. **查看所有知识库**
```bash
curl -X GET "http://1.15.95.222:6408/spaces"
```

3. **查询特定知识库的三元组**
```bash
curl -X GET "http://1.15.95.222:6408/spaces/company_data?limit=20"
```

4. **删除不需要的知识库**
```bash
curl -X DELETE "http://1.15.95.222:6408/spaces/old_data"
```

### Python客户端示例

```python
import requests
import json

class CSVTripleClient:
    def __init__(self, base_url="http://1.15.95.222:6408"):
        self.base_url = base_url
    
    def upload_csv(self, space_name, file_path):
        """上传CSV文件到指定知识库"""
        url = f"{self.base_url}/parse-csv/{space_name}"
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        return response.json()
    
    def list_spaces(self):
        """获取所有知识库"""
        url = f"{self.base_url}/spaces"
        response = requests.get(url)
        return response.json()
    
    def get_triples(self, space_name, limit=100, offset=0):
        """获取指定知识库的三元组"""
        url = f"{self.base_url}/spaces/{space_name}"
        params = {'limit': limit, 'offset': offset}
        response = requests.get(url, params=params)
        return response.json()
    
    def delete_space(self, space_name):
        """删除知识库"""
        url = f"{self.base_url}/spaces/{space_name}"
        response = requests.delete(url)
        return response.json()

# 使用示例
client = CSVTripleClient()

# 上传文件
result = client.upload_csv("test_space", "employees.csv")
print(f"上传结果: {result}")

# 查看知识库
spaces = client.list_spaces()
print(f"知识库列表: {spaces}")

# 获取三元组
triples = client.get_triples("test_space", limit=10)
print(f"三元组: {triples}")
```

### JavaScript客户端示例

```javascript
class CSVTripleClient {
    constructor(baseUrl = 'http://1.15.95.222:6408') {
        this.baseUrl = baseUrl;
    }
    
    async uploadCSV(spaceName, file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseUrl}/parse-csv/${spaceName}`, {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    }
    
    async listSpaces() {
        const response = await fetch(`${this.baseUrl}/spaces`);
        return await response.json();
    }
    
    async getTriples(spaceName, limit = 100, offset = 0) {
        const response = await fetch(
            `${this.baseUrl}/spaces/${spaceName}?limit=${limit}&offset=${offset}`
        );
        return await response.json();
    }
    
    async deleteSpace(spaceName) {
        const response = await fetch(`${this.baseUrl}/spaces/${spaceName}`, {
            method: 'DELETE'
        });
        return await response.json();
    }
}

// 使用示例
const client = new CSVTripleClient();

// 上传文件
const fileInput = document.getElementById('fileInput');
if (fileInput && fileInput.files.length > 0) {
    const file = fileInput.files[0];
    const result = await client.uploadCSV('test_space', file);
    console.log('上传结果:', result);
}

// 查看知识库
const spaces = await client.listSpaces();
console.log('知识库列表:', spaces);
```

## 注意事项

1. **文件格式**: 仅支持CSV格式文件，使用逗号分隔
2. **文件大小**: 建议单个文件不超过10MB
3. **编码格式**: 支持UTF-8编码
4. **知识库名称**: 建议使用英文和数字，避免特殊字符
5. **数据持久化**: 所有数据保存在本地文件系统中
6. **并发限制**: 建议同时上传文件数不超过5个

## 联系信息

如有问题或建议，请联系开发团队。

---
*文档版本: v2.0*  
*最后更新: 2024年1月*