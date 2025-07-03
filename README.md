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
- Enable API Gateway to write logs to CloudWatch in the corresponding
  region. Follow the AWS documentation for [setting up CloudWatch API
  logging using the API Gateway console](https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-logging.html#set-up-access-logging-using-console).

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
