# 🚀 Serverless MCP Python Code Interpreter

A serverless Python code interpreter deployed on AWS Lambda that enables secure Python code execution through the Model Context Protocol (MCP).

## 🎯 Overview

This repository provides a complete MCP server implementation for executing Python code on AWS Lambda, featuring:

- **🐍 Python Code Interpreter**: Execute Python code with pre-installed data science libraries
- **🌐 Web Interface**: Interactive demo interface for testing
- **🤖 AI Integration**: AWS Bedrock Claude integration for intelligent conversations  
- **☁️ Serverless Architecture**: AWS Lambda for automatic scaling and cost optimization
- **🔒 Security Sandboxing**: Secure execution in Lambda's isolated environment

## 🏗️ Architecture

**Stateless Design (Recommended):**
```
Client (Claude/Web UI) → API Gateway → Lambda Function → Python Interpreter → Results
```

Benefits:
- Horizontal scaling across multiple instances
- No session affinity requirements  
- Pay-per-use cost model
- High availability and fault tolerance

## 🔧 Features & Tools

### Core Capabilities
- **📝 Safe Python Execution**: Security patterns blocking with timeout protection
- **📦 Dynamic Package Installation**: Runtime package installation capability
- **🔬 Pre-installed Data Science Stack**: pandas, numpy, matplotlib, scipy, scikit-learn, seaborn
- **🌐 RESTful API**: Interface via Amazon API Gateway

### Available MCP Tools
1. **`execute_python`**: Execute Python code with optional dependency installation
2. **`list_preinstalled_packages`**: List available pre-installed packages  
3. **`get_environment_info`**: Get Python environment information

## 🚀 Quick Start Guide

### Prerequisites
- AWS CLI configured with proper permissions
- Python 3.9+
- Docker (for SAM builds)
- AWS SAM CLI
- Make utility
- A unique S3 bucket name

### Step 1: Manual Setup
```bash
# Clone and navigate to project
git clone <repository-url>
cd Lambda-code-interpreter

# Create main virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create chatbot virtual environment
cd src/chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r ../../requirements.txt
cd ../..

# Setup environment configuration
cp .env.example .env
cp etc/environment.sh.example etc/environment.sh
```

Edit your configuration files with your actual values:

Required .env settings:
```bash
# MCP Server Configuration
MCP_ENDPOINT_URL=https://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/dev/lambda/mcp/

# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default
S3_BUCKET=your-unique-bucket-name

# Bedrock Configuration
BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5002
FLASK_DEBUG=true
```

### Step 2: Deploy MCP Server

**Manual Deployment**
```bash
# Build and deploy Lambda layer
make layer
# Copy Layer ARN from output to O_LAYER_ARN in etc/environment.sh

# Deploy API Gateway and Lambda function
make apigw
# Copy API Gateway URL from output and update .env
```

### Step 3: Run Components

**Start Chatbot:**
```bash
cd src/chatbot
python app.py
```

**Test MCP Server Locally:**
```bash
# FastAPI mode (web interface)
cd src/mcpserver
python server.py --mode fastapi --port 8000

# Stdio mode (for MCP Inspector)
python server.py --mode stdio
```

### Step 4: Test
```bash
# Test the deployment
python simple_test_client.py

# Or open web interface
# Navigate to http://localhost:5002 and ask: "计算 2+2 并用Python验证"
```

### Troubleshooting
- Ensure AWS credentials are configured: `aws sts get-caller-identity`
- Check S3 bucket is unique and accessible
- Verify .env file has correct API Gateway URL with `/dev/lambda/mcp/` suffix
- Check logs for MCP connection errors
- If build fails, check Docker is running and SAM CLI is installed

### Build Process Notes
- The `build/` directory (~23MB) is **automatically generated** and **excluded from git**
- It contains Lambda layer dependencies and is recreated by `make layer`
- Don't manually edit or commit build artifacts - they're platform-specific and version-dependent

## 💡 Usage Examples

### Python Code Execution
```python
# Data analysis
import pandas as pd
data = {'name': ['Alice', 'Bob'], 'age': [25, 30]}
df = pd.DataFrame(data)
print(df.describe())

# Visualization
import matplotlib.pyplot as plt
import numpy as np
x = np.linspace(0, 10, 100)
plt.plot(x, np.sin(x))
plt.show()
```

## 🌐 Interfaces

### AI Chatbot (Port 5002) 
- AWS Bedrock Claude 3.7 Sonnet integration
- Natural language to code generation
- Real-time status monitoring
- Conversational interface for complex requests
- Interactive MCP Python code execution
- Environment-based configuration
- Clean logging (only MCP calls and LLM interactions)

## 🔧 Configuration & Deployment Guide

### 📋 Quick Setup Checklist

- [ ] Replace `YOUR_API_GATEWAY_ID` with your actual API Gateway ID
- [ ] Replace `YOUR_REGION` with your AWS region (e.g., `us-east-1`)
- [ ] Configure AWS credentials
- [ ] Update environment variables
- [ ] Test MCP server connectivity

### 🌐 API Gateway Configuration

After deploying your Lambda function, you'll receive an API Gateway endpoint. Replace the placeholder URLs in these files:

#### Files to Update:
```
src/chatbot/app.py
src/web_demo/chatbot_app.py
src/chatbot/run_chatbot.sh
test_python_interpreter_client.py
simple_test_client.py
```

#### URL Pattern:
```
https://YOUR_API_GATEWAY_ID.execute-api.YOUR_REGION.amazonaws.com/dev/lambda/mcp/
```

#### Example:
```python
# Before (template)
self.base_url = "https://YOUR_API_GATEWAY_ID.execute-api.YOUR_REGION.amazonaws.com/dev/lambda/mcp/"

# After (your actual deployment)
self.base_url = "https://abc123def4.execute-api.us-east-1.amazonaws.com/dev/lambda/mcp/"
```

### ⚙️ Environment Variables

#### AWS Configuration
```bash
# AWS CLI configuration
export AWS_PROFILE=your-profile-name
export AWS_DEFAULT_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
```

#### Lambda Configuration (etc/environment.sh)

**Important**: Copy and modify the `environment.sh` file with your actual values:

```bash
# AWS Configuration - Replace with your actual values
PROFILE=default                            # Your AWS CLI profile name (default: default)
BUCKET=mcp-lambda-test-0610               # S3 bucket for deployment artifacts (use unique name)
REGION=us-east-1                          # Your preferred AWS region

# MCP Dependencies
P_DESCRIPTION="mcp==1.8.0"               # MCP package version for Lambda layer
LAYER_STACK=mcp-lambda-layer             # CloudFormation stack name for layer
LAYER_TEMPLATE=sam/layer.yaml            # SAM template for layer
LAYER_OUTPUT=sam/layer_output.yaml       # Generated layer output file
LAYER_PARAMS="ParameterKey=description,ParameterValue=${P_DESCRIPTION}"
# IMPORTANT: Set this after running 'make layer' - copy the ARN from output
O_LAYER_ARN=""                           # Lambda layer ARN (empty initially, filled after layer deployment)

# API Gateway and Lambda Stack Settings
P_API_STAGE=dev                          # API Gateway deployment stage
P_FN_MEMORY=128                          # Lambda memory allocation (MB) - increase for heavy computations
P_FN_TIMEOUT=15                          # Lambda timeout (seconds) - increase for package installs
APIGW_STACK=mcp-apigw                    # CloudFormation stack name for API Gateway
APIGW_TEMPLATE=sam/template.yaml         # SAM template for API Gateway and Lambda
APIGW_OUTPUT=sam/template_output.yaml    # Generated API Gateway output file
APIGW_PARAMS="ParameterKey=apiStage,ParameterValue=${P_API_STAGE} ParameterKey=fnMemory,ParameterValue=${P_FN_MEMORY} ParameterKey=fnTimeout,ParameterValue=${P_FN_TIMEOUT} ParameterKey=dependencies,ParameterValue=${O_LAYER_ARN}"
```

#### Configuration Steps:

1. **Create your environment file:**
   ```bash
   cd etc
   cp environment.sh environment.sh.example  # backup template
   # Edit environment.sh with your values
   ```

2. **Replace these values:**
   - `PROFILE`: Your AWS CLI profile (run `aws configure list-profiles`)
   - `BUCKET`: Create a unique S3 bucket name (e.g., `mcp-deploy-yourname-$(date +%s)`)
   - `REGION`: Your preferred AWS region
   - `O_LAYER_ARN`: Leave empty initially, will be filled after layer deployment

3. **Deploy in order:**
   ```bash
   make layer          # Creates layer, outputs ARN
   # Copy ARN to O_LAYER_ARN in environment.sh
   make apigw          # Creates API Gateway and Lambda
   ```

### 🤖 Chatbot Configuration

#### Bedrock Model Settings
```python
# In chatbot/app.py
self.model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
self.region = "us-east-1"
```

#### MCP Server URL
```python
# In chatbot/app.py
self.base_url = "https://YOUR_API_GATEWAY_ID.execute-api.YOUR_REGION.amazonaws.com/dev/lambda/mcp/"
```

### 🔐 Security Configuration

#### IAM Permissions Required
Your AWS user/role needs these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:*",
                "apigateway:*",
                "iam:*",
                "s3:*",
                "cloudformation:*",
                "bedrock:*"
            ],
            "Resource": "*"
        }
    ]
}
```

#### Bedrock Access
Ensure Bedrock Claude model access is enabled in your AWS account:
1. Go to AWS Bedrock console
2. Navigate to "Model access"
3. Enable Claude 3.7 Sonnet model

### 🚀 Deployment Steps

#### 1. Configure Environment
```bash
cp etc/environment.sh.example etc/environment.sh
# Edit etc/environment.sh with your settings
```

#### 2. Deploy Lambda Layer
```bash
make layer
# Copy the layer ARN to O_LAYER_ARN in environment.sh
```

#### 3. Deploy Infrastructure
```bash
make apigw
# Note the API Gateway endpoint from output
```

#### 4. Update Client URLs
Replace `YOUR_API_GATEWAY_ID` and `YOUR_REGION` in client files with actual values.

#### 5. Test Deployment
```bash
# Test with Python client
python test_python_interpreter_client.py

# Test web interface
cd src/web_demo
./run_demo.sh

# Test chatbot
cd src/chatbot  
./run_chatbot.sh
```

### 🔍 Verification

#### Test MCP Server
```bash
curl -X POST "https://YOUR_API_GATEWAY_ID.execute-api.YOUR_REGION.amazonaws.com/dev/lambda/mcp/" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

#### Expected Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "execute_python",
        "description": "Execute Python code and return the result"
      },
      {
        "name": "list_preinstalled_packages", 
        "description": "List all pre-installed Python packages"
      },
      {
        "name": "get_environment_info",
        "description": "Get Python environment information"
      }
    ]
  }
}
```

## 📁 Repository Structure

**Active Implementation:** Current directory - Python code interpreter on AWS Lambda  
**Archived:** Multiple Node.js and ECS implementations available in other directories

### Detailed Structure
```
Lambda-code-interpreter/
├── requirements.txt           # Unified Python dependencies
├── .env.example              # Environment configuration template
├── etc/
│   └── environment.sh.example # AWS deployment configuration template
├── sam/
│   ├── layer.yaml            # Lambda layer template
│   ├── template.yaml         # Main infrastructure template
│   └── openapi.yaml          # API documentation
├── src/
│   ├── mcpserver/
│   │   ├── server.py         # FastAPI server entry point
│   │   ├── python_interpreter.py # Core interpreter functionality
│   │   └── run.sh           # Lambda runtime script
│   └── chatbot/
│       ├── app.py           # Web chatbot interface
│       ├── templates/       # HTML templates
│       └── run_chatbot.sh   # Chatbot startup script
└── makefile                 # Build and deployment commands
```

## 🛠️ Prerequisites & Development

### Requirements
- AWS CLI configured
- Python 3.9+
- AWS SAM CLI  
- Docker/Podman
- Make utility

### Virtual Environment Management

This project uses **multiple virtual environments** to isolate dependencies:

```
Lambda-code-interpreter/
├── venv/                                    # Main project environment (Lambda server)
└── src/chatbot/venv/                       # Chatbot environment
```

**Why separate environments?**
- 🔒 **Isolation**: Each component has specific dependencies
- 📦 **Clean builds**: Lambda layer only includes necessary packages
- 🚀 **Faster deployment**: Smaller package sizes
- 🛡️ **Security**: Reduced attack surface per component

### Working with Virtual Environments

**Main Project (General utilities):**
```bash
source venv/bin/activate
# Work with general project scripts
```

**Lambda Server (MCP Server development):**
```bash
source venv/bin/activate
pip install -r requirements.txt

# Run locally with FastAPI
cd src/mcpserver
python server.py --mode fastapi --port 8000

# Test with stdio mode
python server.py --mode stdio
```

**Chatbot (Web interface development):**
```bash
cd src/chatbot
source venv/bin/activate
pip install -r ../../requirements.txt

# Run chatbot
python app.py
# Or use the run script
./run_chatbot.sh
```

### Local Development
```bash
# Quick setup with automated script
./setup.sh

# Manual testing
python -m pytest tests/  # If tests directory exists
```

### Git Configuration

All virtual environments are **automatically excluded** from git via `.gitignore`:
```gitignore
# Virtual environments
venv/
env/
ENV/
src/chatbot/venv/
```

**Benefits:**
- ⚡ Faster git operations
- 💾 Smaller repository size  
- 🔄 Platform-independent setup
- 👥 Consistent development environment

### Environment Configuration
The project uses environment variables for secure configuration:
- **`.env`**: Your actual configuration (gitignored, not committed)
- **`.env.example`**: Template showing required variables
- All sensitive information (API URLs, keys) stored in `.env`

### MCP Inspector Testing

After deployment, test with [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector):

```bash
# Start MCP Inspector locally
mcp dev src/mcpserver/server.py

# Or test the deployed endpoint
# Use the outApiEndpoint from deployment: ${outApiEndpoint}/lambda/mcp/
```

### Adding New Tools
Extend `python_interpreter.py` with additional MCP tools:

```python
@mcp.tool(description="Your new tool description")
def your_new_tool(param: str) -> Dict[str, Any]:
    # Tool implementation
    return {"result": "success"}
```

## 🔒 Security & Monitoring

### Security Features
- **Lambda Sandbox**: Isolated execution environment
- **Code Pattern Blocking**: Prevents dangerous operations like `os.system()`
- **Subprocess Restrictions**: Blocks direct system command execution
- **Timeout Protection**: Package installation limited to 30 seconds
- **Resource Limits**: Configurable memory (512MB-3GB) and timeout (30-900s)
- **File System**: Write access limited to `/tmp` directory

### Monitoring
- **CloudWatch Logs**: `/aws/lambda/[function-name]` for execution logs
- **Performance**: Cold start ~2-3s, warm requests <100ms
- **Troubleshooting**: Increase timeout/memory in `etc/environment.sh`

### Pre-installed Packages

The server comes with these packages pre-installed:
- **Data Science**: pandas, numpy, matplotlib, scipy, scikit-learn, seaborn
- **Web**: requests, fastapi, pydantic, uvicorn
- **Standard Library**: json, os, re, datetime, math, random, collections

### Environment Information
Use the `get_environment_info` tool to check:
- Python version and platform
- Available memory
- Installed packages
- Temporary directory status

## 🛠️ Troubleshooting

### Common Issues

1. **API Gateway 403 Errors**
   - Check IAM permissions
   - Verify API Gateway deployment

2. **Lambda Cold Start Timeouts**
   - Increase timeout in environment.sh
   - Consider provisioned concurrency

3. **Package Installation Timeout**
   - Increase `P_FN_TIMEOUT` in configuration
   - Some packages may require more time to install

4. **Memory Errors**
   - Increase `P_FN_MEMORY` for large computations
   - Monitor memory usage in CloudWatch

5. **Permission Errors**
   - Verify IAM roles have necessary permissions
   - Check Lambda execution role

6. **Bedrock Access Denied**
   - Enable Claude model access in Bedrock console
   - Check IAM permissions for Bedrock

7. **MCP Connection Failures**
   - Verify API Gateway URL is correct
   - Check Lambda function logs in CloudWatch

### Getting Help

- Check CloudWatch logs for Lambda function errors
- Use AWS CLI to test API Gateway endpoints
- Verify network connectivity and DNS resolution

### Make Commands

- `make layer`: Build and deploy Lambda layer with dependencies
- `make apigw`: Deploy API Gateway and Lambda function
- `make apigw.delete`: Remove the deployed stack

## 💰 Cost & Resources

### Cost Optimization

- **Cold Start**: First request may take 2-3 seconds for initialization
- **Warm Requests**: Subsequent requests execute in <100ms
- **Pay-per-Use**: Lambda charges only for actual execution time
- **Memory Tuning**: Balance memory allocation with cost requirements

### Pricing Example
1000 requests/month, 512MB, 2s execution: ~$0.02/month

## 📚 Additional Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## 📜 License

MIT-0 License - See [LICENSE](LICENSE) file for details.

---

**Note**: Keep configuration files updated as your setup changes. Never commit actual credentials or API endpoints to version control.# Lambda-code-interpreter
