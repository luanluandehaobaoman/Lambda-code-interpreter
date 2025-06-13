# 🐍 Lambda Code Interpreter

A serverless Python code interpreter built on AWS Lambda that provides secure Python code execution through the MCP (Model Context Protocol). Perfect for AI-powered code interpretation, data science computations, and educational Python environments.

## 🎯 Features

- **🐍 Secure Python Execution**: Execute Python code in a secure, isolated AWS Lambda environment
- **📊 Data Science Ready**: Pre-installed with pandas, numpy, matplotlib, scipy, scikit-learn, and more
- **🤖 MCP Protocol Support**: Full Model Context Protocol compliance for AI integration
- **☁️ Serverless Architecture**: AWS Lambda with auto-scaling and pay-per-use
- **🔒 Security Sandbox**: Multiple layers of security including Lambda isolation and code pattern blocking
- **⚡ Dynamic Dependencies**: Runtime package installation with timeout protection
- **🌐 HTTP API**: RESTful API through AWS API Gateway

## 🏗️ Architecture

```
Client/AI Agent
    ↓ MCP Protocol (JSON-RPC 2.0)
AWS API Gateway 
    ↓ HTTP Proxy Integration
AWS Lambda Function (Python 3.12)
    ├── FastAPI Server
    ├── MCP Protocol Handler  
    ├── Python Code Interpreter
    └── Dependency Manager
        └── Pre-installed Libraries Layer
```

## 🚀 Quick Start

### Prerequisites

- **AWS CLI** configured with permissions for Lambda, API Gateway, CloudFormation, S3, and IAM
- **Python 3.9+** and **pip**
- **Docker** (required for SAM to build Lambda layers)
- **AWS SAM CLI** (`pip install aws-sam-cli`)
- **S3 Bucket** for deployment artifacts

### Installation & Deployment

#### 1. Clone and Setup

```bash
git clone <repository-url>
cd Lambda-code-interpreter

# Install Python dependencies (for local development)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Configure AWS Environment

```bash
# Copy and edit the AWS deployment configuration
cp etc/environment.sh.example etc/environment.sh

# Edit etc/environment.sh with your values:
# PROFILE=default                    # Your AWS CLI profile
# BUCKET=your-unique-s3-bucket-name  # S3 bucket for deployment
# REGION=us-east-1                   # Your preferred AWS region
# O_LAYER_ARN=""                     # Leave empty for first deployment
```

#### 3. Deploy Lambda Layer (Dependencies)

```bash
make layer
```

After successful deployment, copy the Layer ARN from the output and update `O_LAYER_ARN` in `etc/environment.sh`.

#### 4. Deploy API Gateway and Lambda Function

```bash
make apigw
```

The deployment will output an API Gateway endpoint URL like:
`https://abc123.execute-api.us-east-1.amazonaws.com/dev`

#### 5. Configure Environment Variables

```bash
# Copy and edit application configuration
cp .env.example .env

# Update .env with your API Gateway endpoint:
# MCP_ENDPOINT_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/lambda/mcp/
```

### 🧪 测试部署

#### 使用测试脚本

项目包含了一个综合测试脚本（`test_deployment.sh`）来验证 MCP 服务器部署：

```bash
# 给测试脚本添加执行权限
chmod +x test_deployment.sh

# 使用你的 API Gateway 端点运行综合测试
./test_deployment.sh https://your-api-gateway-endpoint.execute-api.us-east-1.amazonaws.com/dev
```

**使用示例：**
```bash
# 部署成功后，你会得到类似这样的端点：
# https://gjtr49tm58.execute-api.us-east-1.amazonaws.com/dev

# 运行测试
./test_deployment.sh https://gjtr49tm58.execute-api.us-east-1.amazonaws.com/dev
```

#### 测试脚本验证内容

测试脚本执行三个综合测试：

1. **📋 测试1：环境信息获取**
   - 调用 `get_environment_info` 工具
   - 验证 Python 版本获取
   - 确认 MCP 服务器正在响应

2. **🐍 测试2：Python 代码执行**
   - 执行示例 Python 代码：`result = 2 + 3; print(f"计算结果: {result}")`
   - 验证输出包含 "计算结果: 5"
   - 确认执行成功状态

3. **📦 测试3：预装包列表**
   - 调用 `list_preinstalled_packages` 工具
   - 验证关键库的存在（numpy, pandas, matplotlib）
   - 确认数据科学环境就绪

#### 预期测试输出

```bash
🧪 测试MCP部署
================================
MCP端点: https://gjtr49tm58.execute-api.us-east-1.amazonaws.com/dev/lambda/mcp/
================================
📋 测试1: 获取环境信息...
✅ 环境信息获取成功
   Python版本: 3.12.x

🐍 测试2: 执行Python代码...
✅ Python代码执行成功
   输出: 计算结果: 5

📦 测试3: 获取预装包列表...
✅ 预装包列表获取成功
   包含: numpy, pandas, matplotlib等数据科学包

🎉 所有测试通过！MCP服务器部署成功
================================
📝 下一步：
1. 更新 .env 文件中的 MCP_ENDPOINT_URL 为: https://your-endpoint/lambda/mcp/
2. 运行 chatbot: cd src/chatbot && ./run_chatbot.sh
3. 访问 http://localhost:5003 使用Web界面
```

#### 测试失败故障排除

如果测试失败，请检查以下内容：

1. **测试1失败（环境信息）**
   ```bash
   ❌ 环境信息获取失败
   ```
   - 验证 API Gateway 端点 URL 是否正确
   - 检查 Lambda 函数是否已部署并运行
   - 确保发送了正确的请求头

2. **测试2失败（Python执行）**
   ```bash
   ❌ Python代码执行失败
   ```
   - 检查 Lambda 日志中的执行错误
   - 验证 Python 解释器是否正常工作
   - 确保没有安全阻止执行

3. **测试3失败（包列表）**
   ```bash
   ❌ 预装包列表获取失败
   ```
   - 验证 Lambda 层是否正确附加
   - 检查依赖项是否正确安装在层中
   - 确保部署中的层 ARN 正确

#### 手动测试

你也可以手动测试各个组件：

```bash
# 测试环境信息
curl -X POST "https://your-endpoint/lambda/mcp/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_environment_info", "arguments": {}}}'

# 测试 Python 执行
curl -X POST "https://your-endpoint/lambda/mcp/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "execute_python", "arguments": {"code": "print(\"Hello World\")"}}}'

# 测试包列表
curl -X POST "https://your-endpoint/lambda/mcp/" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "list_preinstalled_packages", "arguments": {}}}'
```

## 🔧 MCP Server Capabilities

The Lambda Code Interpreter provides three main MCP tools:

### 1. `execute_python`
Execute Python code with optional package installation.

**Parameters:**
- `code` (string): Python code to execute
- `requirements` (array, optional): List of packages to install

**Example:**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "execute_python",
    "arguments": {
      "code": "import pandas as pd\ndf = pd.DataFrame({'x': [1,2,3], 'y': [4,5,6]})\nprint(df.describe())",
      "requirements": ["pandas"]
    }
  },
  "id": 1
}
```

### 2. `list_preinstalled_packages`
Get a list of pre-installed Python packages.

**Pre-installed Libraries:**
- **Data Science**: pandas, numpy, matplotlib, scipy, scikit-learn, seaborn
- **Web**: fastapi, pydantic, uvicorn, requests, httpx
- **Standard**: json, os, re, datetime, math, random, collections

### 3. `get_environment_info`
Retrieve Python environment information including version, platform, and installed packages.

## 🔒 Security Features

### Multi-Layer Security
1. **AWS Lambda Sandbox**: Isolated execution environment with read-only filesystem (except `/tmp`)
2. **Code Pattern Blocking**: Prevents dangerous operations:
   - `os.system()`, `subprocess.call()`, `subprocess.run()`
   - Direct system command execution
   - Malicious import patterns
3. **Resource Limits**: 
   - Configurable memory allocation (128MB - 10GB)
   - Execution timeout (15-900 seconds)
   - Package installation timeout (30 seconds)
4. **Network Restrictions**: Lambda execution environment controls

### Configuration Options
```bash
# In etc/environment.sh
P_FN_MEMORY=128      # Lambda memory in MB (128-10240)
P_FN_TIMEOUT=60      # Lambda timeout in seconds (15-900)
```

## 📁 Project Structure

```
Lambda-code-interpreter/
├── requirements.txt              # Unified Python dependencies
├── .env.example                 # Application configuration template
├── makefile                     # Build and deployment commands
├── test_deployment.sh          # Deployment testing script
├── simple_test_client.py       # Standalone MCP test client
├── etc/
│   └── environment.sh.example  # AWS deployment configuration
├── sam/                        # AWS SAM templates
│   ├── template.yaml          # Main infrastructure (Lambda + API Gateway)
│   ├── layer.yaml            # Lambda layer for dependencies
│   ├── openapi.yaml          # API Gateway specification
│   └── src/dependencies/     # Layer dependencies
└── src/
    └── mcpserver/           # MCP server implementation
        ├── server.py        # FastAPI server with MCP integration
        ├── python_interpreter.py  # Core interpreter and tools
        └── run.sh          # Lambda execution wrapper
```

## 🛠️ Development & Testing

### Local Testing

For local development and testing, you can run the MCP server standalone:

```bash
# Activate virtual environment
source venv/bin/activate

# Navigate to MCP server directory
cd src/mcpserver

# Run in different modes:
python server.py --mode stdio           # Standard I/O mode
python server.py --mode streamable-http # HTTP streaming mode  
python server.py --mode fastapi         # FastAPI server mode
```

### Test Client

Use the provided test client for local development:

```bash
python simple_test_client.py https://your-endpoint.execute-api.us-east-1.amazonaws.com/dev/lambda/mcp/
```

### Make Commands

- `make layer` - Build and deploy Lambda layer with dependencies
- `make layer.build` - Build layer only (no deployment)
- `make layer.package` - Package layer for deployment
- `make layer.deploy` - Deploy layer to AWS
- `make apigw` - Deploy API Gateway and Lambda function
- `make apigw.package` - Package application for deployment
- `make apigw.deploy` - Deploy application stack
- `make apigw.delete` - Delete deployed stack

## 🌐 API Usage

### Endpoint Format
```
POST https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/lambda/mcp/
```

### Required Headers
```
Content-Type: application/json
Accept: application/json, text/event-stream
```

### Request Format (JSON-RPC 2.0)
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "execute_python",
    "arguments": {
      "code": "print('Hello, World!')"
    }
  },
  "id": 1
}
```

### Response Format (Server-Sent Events)
```
event: message
data: {"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"..."}]}}
```

## 🔍 Troubleshooting

### Common Issues

1. **"uvicorn module not found"**
   - Ensure Lambda layer is properly deployed and referenced
   - Check `O_LAYER_ARN` in `etc/environment.sh`

2. **API Gateway 403/404 errors**
   - Verify AWS permissions for API Gateway and Lambda
   - Check endpoint URL format (ensure trailing slash: `/mcp/`)

3. **Lambda timeout errors**
   - Increase `P_FN_TIMEOUT` in environment configuration
   - Consider increasing memory allocation for complex computations

4. **Package installation failures**
   - Some packages may not install in Lambda environment
   - Consider adding to pre-installed layer dependencies

5. **S3 Access Denied**
   - Verify S3 bucket permissions and AWS profile
   - Ensure bucket exists and is accessible

### Logs and Monitoring

View Lambda logs using AWS CLI:
```bash
# List log groups
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/mcp-apigw-Fn" --profile default

# Get recent logs
aws logs get-log-events --log-group-name "/aws/lambda/your-function-log-group" --log-stream-name "latest-stream" --profile default
```

## 📊 Performance Considerations

- **Cold Start**: ~2-3 second initialization for new Lambda containers
- **Memory**: 128MB minimum, 1GB+ recommended for data science workloads
- **Timeout**: 60 seconds default, up to 15 minutes maximum
- **Package Installation**: 30-second timeout, runs once per container lifecycle
- **Concurrent Executions**: AWS Lambda default limits apply

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with `test_deployment.sh`
5. Submit a pull request

## 📄 License

This project is licensed under the terms specified in the LICENSE file.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review AWS CloudWatch logs for detailed error information
3. Ensure all prerequisites are properly installed and configured
4. Verify AWS permissions and resource limits

---

**Note**: This is a serverless implementation designed for secure, isolated Python code execution. Always review code execution patterns and adjust security settings according to your use case requirements.