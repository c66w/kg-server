#!/bin/bash

# CSV三元组解析服务 - Docker启动脚本

# 默认配置
DEFAULT_EXTERNAL_PORT=8080
DEFAULT_INTERNAL_PORT=6408
DEFAULT_IMAGE_NAME="csv-triple-parser"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo -e "${BLUE}CSV三元组解析服务 - Docker启动脚本${NC}"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -p, --port PORT        设置外部端口 (默认: $DEFAULT_EXTERNAL_PORT)"
    echo "  -i, --internal PORT    设置内部端口 (默认: $DEFAULT_INTERNAL_PORT)"
    echo "  -n, --name NAME        设置容器名称 (默认: $DEFAULT_IMAGE_NAME)"
    echo "  -b, --build            构建镜像"
    echo "  -d, --detach           后台运行"
    echo "  -h, --help             显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -p 9000              # 使用端口9000启动"
    echo "  $0 -p 9000 -i 8000      # 外部端口9000，内部端口8000"
    echo "  $0 -b -d                # 构建镜像并后台运行"
    echo ""
}

# 解析命令行参数
EXTERNAL_PORT=$DEFAULT_EXTERNAL_PORT
INTERNAL_PORT=$DEFAULT_INTERNAL_PORT
CONTAINER_NAME=$DEFAULT_IMAGE_NAME
BUILD_IMAGE=false
DETACH_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            EXTERNAL_PORT="$2"
            shift 2
            ;;
        -i|--internal)
            INTERNAL_PORT="$2"
            shift 2
            ;;
        -n|--name)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        -b|--build)
            BUILD_IMAGE=true
            shift
            ;;
        -d|--detach)
            DETACH_MODE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 显示配置信息
echo -e "${BLUE}=== CSV三元组解析服务配置 ===${NC}"
echo -e "外部端口: ${GREEN}$EXTERNAL_PORT${NC}"
echo -e "内部端口: ${GREEN}$INTERNAL_PORT${NC}"
echo -e "容器名称: ${GREEN}$CONTAINER_NAME${NC}"
echo -e "构建镜像: ${GREEN}$BUILD_IMAGE${NC}"
echo -e "后台运行: ${GREEN}$DETACH_MODE${NC}"
echo ""

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}错误: Docker未运行，请先启动Docker${NC}"
    exit 1
fi

# 停止并删除现有容器
if docker ps -a --format "table {{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
    echo -e "${YELLOW}停止并删除现有容器: $CONTAINER_NAME${NC}"
    docker stop $CONTAINER_NAME > /dev/null 2>&1
    docker rm $CONTAINER_NAME > /dev/null 2>&1
fi

# 构建镜像
if [ "$BUILD_IMAGE" = true ]; then
    echo -e "${BLUE}构建Docker镜像...${NC}"
    docker build -t $CONTAINER_NAME .
    if [ $? -ne 0 ]; then
        echo -e "${RED}镜像构建失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}镜像构建成功${NC}"
fi

# 创建必要的目录
echo -e "${BLUE}创建必要目录...${NC}"
mkdir -p knowledge_bases logs

# 启动容器
echo -e "${BLUE}启动容器...${NC}"

DETACH_FLAG=""
if [ "$DETACH_MODE" = true ]; then
    DETACH_FLAG="-d"
fi

docker run $DETACH_FLAG \
    --name $CONTAINER_NAME \
    -p $EXTERNAL_PORT:$INTERNAL_PORT \
    -e PORT=$INTERNAL_PORT \
    -e HOST=0.0.0.0 \
    -v $(pwd)/knowledge_bases:/app/knowledge_bases \
    -v $(pwd)/logs:/app/logs \
    --restart unless-stopped \
    $CONTAINER_NAME

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 服务启动成功！${NC}"
    echo -e "${BLUE}📍 服务地址: ${GREEN}http://localhost:$EXTERNAL_PORT${NC}"
    echo -e "${BLUE}📖 API文档: ${GREEN}http://localhost:$EXTERNAL_PORT/docs${NC}"
    echo -e "${BLUE}🌐 Web界面: ${GREEN}http://localhost:$EXTERNAL_PORT${NC}"
    echo ""
    
    if [ "$DETACH_MODE" = true ]; then
        echo -e "${YELLOW}💡 容器在后台运行，使用以下命令查看日志:${NC}"
        echo -e "   docker logs -f $CONTAINER_NAME"
        echo ""
        echo -e "${YELLOW}💡 停止服务:${NC}"
        echo -e "   docker stop $CONTAINER_NAME"
    fi
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    exit 1
fi 