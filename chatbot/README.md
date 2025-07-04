# Lambda-code-interpreter Chatbot Demo

这是一个演示chatbot，展示了如何通过MCP streamableHttp协议与AWS Bedrock Claude模型集成，实现工具调用功能。

## 功能特性

- 🤖 使用AWS Bedrock Claude 3.7 Sonnet模型
- 🔧 通过MCP streamableHttp协议连接到lambda-python-interpreter服务
- ⚡ 实时流式显示工具调用过程
- 🌐 Gradio Web界面，简洁易用
- 📋 支持环境变量配置
- 🔐 AWS凭证集成

## 环境变量配置

1. 复制环境变量模板:
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，配置你的MCP服务器URL:
```bash
# 必须配置：你的MCP服务器URL
MCP_SERVER_URL=https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/dev/lambda/mcp/

# 可选配置
AWS_REGION=us-east-1
AWS_PROFILE=default
GRADIO_SERVER_PORT=7860
GRADIO_SERVER_HOST=0.0.0.0
DEBUG=true
```

## 安装运行

### 方法1: 使用启动脚本（推荐）
```bash
# 直接运行启动脚本，会自动检查依赖和配置
./run.sh
```

### 方法2: 手动运行
```bash
# 1. 激活虚拟环境并安装依赖
source venv/bin/activate
pip install -r requirements.txt

# 2. 确保AWS凭证配置正确
aws configure --profile default

# 3. 设置环境变量（如果没有.env文件）
export MCP_SERVER_URL="https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/dev/lambda/mcp/"

# 4. 运行应用
python chatbot.py
```

## 访问界面

启动成功后，访问 http://localhost:7860 查看界面

## MCP服务器配置

支持的配置项：
- **MCP_SERVER_URL**: MCP服务器的API Gateway URL（必需）
- **AWS_REGION**: AWS区域设置
- **AWS_PROFILE**: AWS凭证配置文件名称
- 协议: streamableHttp
- 工具: Python代码执行器

## 使用说明

1. 在输入框中输入你的问题或请求
2. 如果Claude需要使用工具，界面会显示：
   - 工具名称和参数
   - 工具执行结果
   - Claude基于结果的最终回答
3. 支持连续对话，保持上下文
4. 点击"Clear Chat"清空对话历史

## 示例对话

"请计算1+1的结果"
"帮我生成一个简单的Python函数来计算斐波那契数列"
"运行这段代码: print('Hello World')"