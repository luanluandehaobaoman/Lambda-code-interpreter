# 🛠️ Development Guide

This guide explains the development setup, virtual environment management, and contribution workflow for the Lambda Code Interpreter project.

## 📁 Project Structure

```
Lambda-code-interpreter/
├── setup.sh                           # 🚀 Automated setup script
├── run.sh                             # 🎯 Component runner script
├── .env.example                       # 📋 Environment template
├── .gitignore                         # 🚫 Git ignore rules
├── venv/                              # 🐍 Main project virtual environment
├── etc/environment.sh                 # ⚙️ AWS deployment configuration
├── src/dependencies/requirements.txt  # 📦 Lambda dependencies
├── src/mcpserver/                     # 🔄 MCP server implementation
└── src/chatbot/                       # 💬 Web chatbot interface
    ├── venv/                          # 🐍 Chatbot virtual environment
    └── requirements.txt               # 📦 Chatbot dependencies
├── simple_test_client.py              # 🧪 Test client
└── README.md                          # 📖 Main documentation
```

## 🐍 Virtual Environment Strategy

### Why Multiple Virtual Environments?

This project uses **2 separate virtual environments** to maintain clean dependency isolation:

1. **Main Project Environment** (`venv/`)
   - **Purpose**: MCP server development, local testing, and general utilities
   - **Dependencies**: FastAPI, FastMCP, MCP protocol libraries, test clients
   - **Usage**: `source venv/bin/activate`

2. **Chatbot Environment** (`src/chatbot/venv/`)
   - **Purpose**: Web interface with Flask and AWS Bedrock integration
   - **Dependencies**: Flask, Boto3, SocketIO, web-specific libraries
   - **Usage**: Isolated from server dependencies for clean deployment

### Benefits of This Architecture

- 🔒 **Dependency Isolation**: Each component has only necessary packages
- 📦 **Smaller Lambda Layers**: Only MCP-related packages in Lambda deployment
- 🚀 **Faster Deployments**: Reduced package sizes and build times
- 🛡️ **Security**: Minimal attack surface per component
- 🧪 **Easier Testing**: Clear separation of concerns
- 💰 **Cost Optimization**: Smaller Lambda packages = lower costs

## 🚀 Quick Start for Developers

### 1. Manual Setup

```bash
# Clone the repository
git clone <repository-url>
cd Lambda-code-interpreter

# Setup main virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup chatbot virtual environment  
cd src/chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r ../../requirements.txt
cd ../..

# Copy configuration templates
cp .env.example .env
cp etc/environment.sh.example etc/environment.sh
```


## 🎯 Component Development

### Working with the MCP Server

```bash
# Activate main project environment
source venv/bin/activate

# Run server locally (FastAPI mode)
cd src/mcpserver
python server.py --mode fastapi --port 8000

# Run server in stdio mode (for MCP Inspector)
python server.py --mode stdio

```

### Working with the Chatbot

```bash
# Activate chatbot environment
cd src/chatbot
source venv/bin/activate

# Configure environment (copy from main .env)
cp ../../.env .env

# Run chatbot
python app.py

```

### Testing Components

```bash
# Test MCP server functionality
python simple_test_client.py

# Manual testing with curl
curl -X POST "http://localhost:8000/lambda/mcp/" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

## 📦 Dependency Management

### Adding New Dependencies

**For Lambda Server:**
```bash
source venv/bin/activate
pip install new-package
pip freeze > src/dependencies/requirements.txt
```

**For Chatbot:**
```bash
cd src/chatbot
source venv/bin/activate
pip install new-package
pip freeze > requirements.txt
```

**For Main Project:**
```bash
source venv/bin/activate
pip install new-package
# Create requirements.txt if needed
pip freeze > requirements.txt
```

### Package Versions

Key dependencies and their purposes:

**Lambda Server (`src/dependencies/requirements.txt`):**
- `fastapi` - Web framework for HTTP/REST API
- `fastmcp` - FastAPI integration for MCP protocol
- `mcp` - Model Context Protocol implementation
- `pydantic` - Data validation and serialization
- `uvicorn` - ASGI server for FastAPI

**Chatbot (`src/chatbot/requirements.txt`):**
- `flask` - Web framework for chatbot interface
- `flask-socketio` - WebSocket support for real-time chat
- `boto3` - AWS SDK for Bedrock integration
- `requests` - HTTP client for MCP server communication
- `python-dotenv` - Environment variable management

## 🔄 Development Workflow

### 1. Making Changes

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Activate appropriate virtual environment
source venv/bin/activate                              # Main project (includes Lambda server)
# OR  
cd src/chatbot && source venv/bin/activate           # Chatbot

# Make your changes
# ... edit files ...

# Test locally
./run.sh mcp-server    # Test MCP server
./run.sh chatbot       # Test chatbot
./run.sh test-client   # Run test suite
```

### 2. Testing Changes

```bash
# Test MCP server
./run.sh mcp-server
curl -X POST "http://localhost:8000/lambda/mcp/" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'

# Test chatbot
./run.sh chatbot
# Open http://localhost:5002

# Test deployment (optional)
./run.sh deploy-all
```

### 3. Updating Dependencies

```bash
# Update Lambda dependencies
source venv/bin/activate
pip install --upgrade package-name
pip freeze > src/dependencies/requirements.txt

# Update chatbot dependencies
cd src/chatbot
source venv/bin/activate
pip install --upgrade package-name
pip freeze > requirements.txt
```

### 4. Committing Changes

```bash
# Only commit source code, not virtual environments
git add .
git commit -m "feat: your feature description"

# Virtual environments are automatically ignored by .gitignore
```

## 🚫 What NOT to Commit

The `.gitignore` file automatically excludes:

```gitignore
# Virtual environments (automatically excluded)
venv/
env/
ENV/
*/venv/
*/env/
src/chatbot/venv/

# Build and deployment artifacts (automatically generated)
build/                                           # SAM build output (~23MB)
sam/layer_output.yaml                            # Generated layer template
sam/template_output.yaml                         # Generated API template
.aws-sam/                                        # SAM build cache

# Configuration files with secrets
.env
etc/environment.sh

# Python build artifacts
build/
dist/
*.egg-info/

# Logs and temporary files
*.log
*.tmp
/tmp/
```

### Why Build Artifacts Are Excluded

The `build/` directory contains:
- **Python Dependencies**: All packages needed for Lambda layer (~23MB)
- **Platform-Specific Binaries**: Compiled extensions for Linux Lambda runtime
- **Generated Templates**: SAM output files with deployment parameters

**Why not commit these?**
- 💾 **Size**: Adds 23MB+ to repository
- 🔄 **Regeneratable**: Created automatically by `make layer`
- 🖥️ **Platform-Specific**: May not work across different systems
- 📦 **Version-Dependent**: Updates when dependencies change
- 🚀 **CI/CD Friendly**: Build process should be reproducible

## 🔧 Troubleshooting Development Issues

### Virtual Environment Issues

```bash
# If virtual environments are corrupted
rm -rf venv/
rm -rf src/chatbot/venv/
./setup.sh  # Recreate all environments

# If dependencies are missing
./run.sh mcp-server  # Will show missing dependency errors
# Then reinstall in appropriate environment
```

### Common Issues

1. **"ModuleNotFoundError"**
   - Ensure you're in the correct virtual environment
   - Check if dependencies are installed: `pip list`
   - Reinstall requirements: `pip install -r requirements.txt`

2. **"Command not found"**
   - Make sure scripts are executable: `chmod +x setup.sh run.sh`
   - Ensure you're in the project root directory

3. **AWS Deployment Issues**
   - Check AWS credentials: `aws sts get-caller-identity`
   - Verify S3 bucket exists and is accessible
   - Ensure Docker is running for SAM builds

4. **Port Already in Use**
   - Kill existing processes: `pkill -f "python.*server.py"`
   - Use different ports: `./run.sh mcp-server --port 8001`

### Environment Verification

```bash
# Check all environments are created
ls -la venv/
ls -la src/chatbot/venv/

# Check installed packages
source venv/bin/activate && pip list
cd src/chatbot && source venv/bin/activate && pip list
```

## 🤝 Contributing

1. Fork the repository
2. Run `./setup.sh` to setup development environment
3. Create a feature branch
4. Make your changes in the appropriate virtual environment
5. Test with `./run.sh` commands
6. Commit only source code (virtual environments are auto-ignored)
7. Submit a pull request

## 📚 Additional Resources

- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)

---

**Note**: This development guide focuses on the isolated virtual environment architecture. Always activate the appropriate environment before working on specific components.