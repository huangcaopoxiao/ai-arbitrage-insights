#!/bin/bash
# 曹皇 - Docker (Colima) 安装脚本 👑
# 轻量级容器运行时，完美适配 Mac Mini

echo "🐳 曹皇 Docker 安装向导"
echo "========================"
echo ""

# 检查 Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ 需要先安装 Homebrew"
    echo "运行: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

echo "📦 安装 Colima + Docker CLI..."
echo "(这比 Docker Desktop 轻量 90%，更适合 Mac Mini)"
echo ""

# 安装 Colima (轻量级容器运行时)
brew install colima

# 安装 Docker CLI (命令行工具)
brew install docker

# 安装 Docker Compose
brew install docker-compose

echo ""
echo "✅ 安装完成"
echo ""

# 启动 Colima
echo "🚀 启动 Colima (首次启动需要 1-2 分钟)..."
colina start --cpu 2 --memory 4 --disk 20

echo ""
echo "📋 验证安装..."
docker --version
docker-compose --version
colina status

echo ""
echo "✅ Docker 环境就绪"
echo ""
echo "常用命令:"
echo "  colima start          # 启动 Docker 环境"
echo "  colima stop           # 停止 Docker 环境"
echo "  colima status         # 查看状态"
echo "  docker ps             # 查看运行中的容器"
echo "  docker run hello-world # 测试"
echo ""
