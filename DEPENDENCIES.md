# 📦 Dependencies Management Guide

This document explains how dependencies are managed in the Lambda Code Interpreter project.

## 🎯 Overview

The project now uses a unified dependency management system with automatic installation capabilities.

## 📋 Dependency Files

### **Main Requirements File**
- **`requirements.txt`** - Unified dependencies for the entire project
  - Contains all core MCP, FastAPI, AWS, and data science dependencies
  - Used by all components as the primary dependency source
  - Automatically resolves version conflicts

### **Unified Dependency Management**
All dependencies are now managed through a single `requirements.txt` file at the project root. This simplifies dependency management and reduces duplication.

## 🚀 Quick Start

### **Manual Setup**
```bash
# Create and setup main virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create and setup chatbot virtual environment
cd src/chatbot
python3 -m venv venv
source venv/bin/activate
pip install -r ../../requirements.txt
cd ../..
```



## 📋 Available Dependencies

### **Core MCP & FastAPI Stack**
- fastapi==0.115.12
- fastmcp==2.3.0
- mcp==1.8.0
- pydantic==2.11.4
- uvicorn==0.34.2

### **Web Framework (Chatbot)**
- flask==3.0.0
- flask-socketio==5.3.6
- python-socketio==5.9.0
- eventlet==0.33.3

### **AWS SDK**
- boto3==1.35.0
- botocore==1.35.0

### **Data Science Libraries**
- pandas>=1.5.0
- numpy>=1.24.0
- matplotlib>=3.6.0
- scipy>=1.10.0
- scikit-learn>=1.2.0
- seaborn>=0.12.0

### **Development & Testing**
- pytest>=7.0.0
- pytest-asyncio>=0.21.0

### **Utilities**
- requests==2.31.0
- httpx>=0.24.0
- python-dotenv>=1.1.0
- cryptography>=40.0.0

## 🔧 Troubleshooting

### **Dependency Conflicts**
If you encounter dependency conflicts:
```bash
# Remove and recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Missing Dependencies**
If a component complains about missing dependencies:
```bash
# Reinstall dependencies for specific component
source venv/bin/activate
pip install -r requirements.txt

# Or for chatbot specifically
source src/chatbot/venv/bin/activate
pip install -r requirements.txt
```

### **Update Dependencies**
To update to latest compatible versions:
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## 📝 Adding New Dependencies

### **For All Components**
Add to `requirements.txt`:
```
# Add your dependency here
new-package>=1.0.0
```

### **For Specific Use Cases**
Since all dependencies are unified, simply add new packages to the main `requirements.txt` file. If you need environment-specific packages, consider using optional dependencies or separate environments.

## 🎛️ Environment Management

### **Virtual Environments**
- **Main project**: `venv/` (contains all dependencies from unified requirements.txt)
- **Chatbot**: `src/chatbot/venv/` (contains same dependencies for isolation)
- Both are automatically created by `./setup.sh` using the unified requirements.txt

### **Environment Variables**
- **`.env`** - Created from `.env.example` during setup
- **`etc/environment.sh`** - AWS deployment configuration

## 🔒 Security Notes

- All virtual environments are ignored by git
- Sensitive configuration files are ignored
- Dependencies are pinned to specific versions for security
- Use `cryptography>=40.0.0` for security-sensitive operations

---

💡 **Pro Tip**: Use the unified `requirements.txt` for all components to ensure consistent dependencies across your development environment!