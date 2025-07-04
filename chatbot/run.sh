#!/bin/bash

# Lambda-code-interpreter Chatbot 启动脚本

# 设置错误处理
set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting Lambda-code-interpreter Chatbot..."

# 检查.env文件是否存在
if [ -f ".env" ]; then
    echo "📋 Loading environment variables from .env file..."
    # 导出环境变量（过滤掉注释和空行）
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
else
    echo "⚠️  Warning: .env file not found, using default values"
fi

# 显示当前配置
echo "🔧 Configuration:"
echo "   MCP Server URL: ${MCP_SERVER_URL:-'<not set>'}"
echo "   AWS Region: ${AWS_REGION:-'us-east-1'}"
echo "   AWS Profile: ${AWS_PROFILE:-'default'}"
echo "   Gradio Port: ${GRADIO_SERVER_PORT:-'7860'}"
echo "   Gradio Host: ${GRADIO_SERVER_HOST:-'0.0.0.0'}"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create it first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# 检查依赖
echo "📦 Checking dependencies..."
if ! python -c "import gradio, boto3, aiohttp" 2>/dev/null; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
fi

# 检查AWS凭证
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity --profile "${AWS_PROFILE:-default}" >/dev/null 2>&1; then
    echo "⚠️  Warning: AWS credentials not properly configured"
    echo "   Please run: aws configure --profile ${AWS_PROFILE:-default}"
fi

# 检查MCP服务器连接
echo "🌐 Testing MCP server connection..."
if [ -n "$MCP_SERVER_URL" ] && command -v curl >/dev/null 2>&1; then
    if curl -s --connect-timeout 5 "$MCP_SERVER_URL" >/dev/null; then
        echo "✅ MCP server is accessible"
    else
        echo "⚠️  Warning: MCP server may not be accessible"
    fi
elif [ -z "$MCP_SERVER_URL" ]; then
    echo "⚠️  Warning: MCP_SERVER_URL not set, skipping connection test"
else
    echo "⚠️  Warning: curl not available, skipping connection test"
fi

# 启动应用
echo "🎉 Starting chatbot application..."
echo "📱 Access the interface at: http://${GRADIO_SERVER_HOST:-0.0.0.0}:${GRADIO_SERVER_PORT:-7860}"
echo "🛑 Press Ctrl+C to stop"
echo ""

python chatbot.py