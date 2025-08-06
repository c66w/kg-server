from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import pandas as pd
import io
import os
import json
import re
from typing import List, Dict, Any
from datetime import datetime

app = FastAPI(title="CSV三元组解析服务", description="支持多知识库的CSV到三元组转换")

# 安全配置
security = HTTPBearer(auto_error=False)

# 文件大小限制 (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# 允许的文件类型
ALLOWED_EXTENSIONS = {'.csv'}

def validate_space_name(space_name: str) -> bool:
    """验证知识库名称是否安全"""
    # 只允许字母、数字、下划线、连字符
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', space_name))

def validate_file_type(filename: str) -> bool:
    """验证文件类型"""
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:6408",
        "http://127.0.0.1:6408",
        # 添加你的服务器域名，例如：
        # "https://your-domain.com",
        "http://1.15.95.222:6408"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# 挂载静态文件
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 知识库存储目录
KNOWLEDGE_BASE_DIR = "knowledge_bases"

def ensure_knowledge_base_dir():
    """确保知识库目录存在"""
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        os.makedirs(KNOWLEDGE_BASE_DIR)

def get_knowledge_base_path(space_name: str) -> str:
    """获取知识库文件路径"""
    return os.path.join(KNOWLEDGE_BASE_DIR, f"{space_name}.json")

def load_knowledge_base(space_name: str) -> List[Dict[str, Any]]:
    """加载知识库数据"""
    file_path = get_knowledge_base_path(space_name)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_knowledge_base(space_name: str, triples: List[Dict[str, Any]]):
    """保存知识库数据"""
    file_path = get_knowledge_base_path(space_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(triples, f, ensure_ascii=False, indent=2)

def csv_to_triples(csv_content: str, space_name: str) -> List[Dict[str, Any]]:
    """
    最简单的CSV到三元组转换
    每个格子都是实体，相邻格子生成关系
    """
    # 读取CSV
    df = pd.read_csv(io.StringIO(csv_content))
    triples = []
    
    # 获取所有格子的值
    cells = []
    for i in range(len(df)):
        for j in range(len(df.columns)):
            value = str(df.iloc[i, j]).strip()
            if value and value != 'nan':
                cells.append({
                    'value': value,
                    'row': i,
                    'col': j,
                    'col_name': df.columns[j]
                })
    
    # 生成行内相邻关系
    for i in range(len(cells) - 1):
        if cells[i]['row'] == cells[i+1]['row']:
            triples.append({
                'subject': cells[i]['value'],
                'predicate': 'next_to',
                'object': cells[i+1]['value'],
                'type': 'row_adjacent',
                'space': space_name,
                'created_at': datetime.now().isoformat()
            })
    
    # 生成表头关系（如果第一行是表头）
    # if len(df.columns) > 0:
    #     for cell in cells:
    #         if cell['row'] > 0:  # 跳过表头行
    #             triples.append({
    #                 'subject': cell['value'],
    #                 'predicate': 'has_property',
    #                 'object': cell['col_name'],
    #                 'type': 'header_relation',
    #                 'space': space_name,
    #                 'created_at': datetime.now().isoformat()
    #             })
    
    return triples

@app.post("/parse-csv/{space_name}")
async def parse_csv(space_name: str, file: UploadFile = File(...)):
    """
    上传CSV文件并解析为三元组，存储到指定知识库
    """
    try:
        # 验证知识库名称
        if not validate_space_name(space_name):
            raise HTTPException(status_code=400, detail="知识库名称只能包含字母、数字、下划线和连字符")
        
        # 验证文件类型
        if not validate_file_type(file.filename):
            raise HTTPException(status_code=400, detail="只支持CSV文件")
        
        # 确保知识库目录存在
        ensure_knowledge_base_dir()
        
        # 读取CSV文件内容
        content = await file.read()
        
        # 检查文件大小
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"文件大小超过限制 ({MAX_FILE_SIZE // 1024 // 1024}MB)")
        
        # 尝试多种编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        csv_content = None
        
        for encoding in encodings:
            try:
                csv_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if csv_content is None:
            raise HTTPException(status_code=400, detail="无法解码文件，请确保文件编码为UTF-8、GBK或GB2312")
        
        # 解析为三元组
        new_triples = csv_to_triples(csv_content, space_name)
        
        # 加载现有知识库数据
        existing_triples = load_knowledge_base(space_name)
        
        # 合并新数据
        all_triples = existing_triples + new_triples
        
        # 保存到知识库
        save_knowledge_base(space_name, all_triples)
        
        return JSONResponse({
            "success": True,
            "message": f"成功解析出 {len(new_triples)} 个三元组，已存储到知识库 '{space_name}'",
            "new_triples": new_triples,
            "total_triples": len(all_triples),
            "space_name": space_name
        })
        
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"解析失败: {str(e)}"
        }, status_code=400)

@app.get("/spaces")
async def list_spaces():
    """列出所有知识库"""
    ensure_knowledge_base_dir()
    spaces = []
    for filename in os.listdir(KNOWLEDGE_BASE_DIR):
        if filename.endswith('.json'):
            space_name = filename[:-5]  # 去掉.json后缀
            file_path = os.path.join(KNOWLEDGE_BASE_DIR, filename)
            triples = load_knowledge_base(space_name)
            spaces.append({
                "name": space_name,
                "triple_count": len(triples),
                "created_at": triples[0]['created_at'] if triples and len(triples) > 0 else None
            })
    return {"spaces": spaces}

@app.get("/spaces/{space_name}")
async def get_space_triples(space_name: str, limit: int = 100, offset: int = 0):
    """获取指定知识库的三元组"""
    # 验证知识库名称
    if not validate_space_name(space_name):
        raise HTTPException(status_code=400, detail="知识库名称只能包含字母、数字、下划线和连字符")
    
    # 验证分页参数
    if limit < 1 or limit > 1000:
        raise HTTPException(status_code=400, detail="limit参数必须在1-1000之间")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset参数不能为负数")
    
    triples = load_knowledge_base(space_name)
    total = len(triples)
    paginated_triples = triples[offset:offset + limit]
    
    return {
        "space_name": space_name,
        "total_count": total,
        "limit": limit,
        "offset": offset,
        "triples": paginated_triples
    }

@app.delete("/spaces/{space_name}")
async def delete_space(space_name: str):
    """删除指定知识库"""
    # 验证知识库名称
    if not validate_space_name(space_name):
        raise HTTPException(status_code=400, detail="知识库名称只能包含字母、数字、下划线和连字符")
    
    file_path = get_knowledge_base_path(space_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"success": True, "message": f"知识库 '{space_name}' 已删除"}
    else:
        raise HTTPException(status_code=404, detail=f"知识库 '{space_name}' 不存在")

@app.get("/")
async def root():
    """重定向到前端页面"""
    return RedirectResponse(url="/static/index.html")

@app.get("/api")
async def api_info():
    """API信息"""
    return {
        "message": "CSV三元组解析服务 - 支持多知识库", 
        "version": "2.0",
        "endpoints": {
            "upload": "POST /parse-csv/{space_name}",
            "list_spaces": "GET /spaces",
            "get_triples": "GET /spaces/{space_name}",
            "delete_space": "DELETE /spaces/{space_name}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    import os
    
    # 从环境变量获取端口，默认为6408
    port = int(os.getenv('PORT', 6408))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"🚀 启动CSV三元组解析服务...")
    print(f"📍 服务地址: http://{host}:{port}")
    print(f"📖 API文档: http://{host}:{port}/docs")
    print(f"🌐 Web界面: http://{host}:{port}")
    
    uvicorn.run(app, host=host, port=port) 