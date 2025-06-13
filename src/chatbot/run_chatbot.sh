#!/bin/bash

# MCP Python Code Interpreter Chatbot Startup Script

set -e  # Exit on error

echo "🤖 Starting MCP Python Code Interpreter Chatbot..."

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not installed. Please install Python3 first."
    exit 1
fi

# Check AWS configuration
check_aws_config() {
    if command -v aws &> /dev/null && aws configure list &> /dev/null; then
        echo "✅ AWS CLI configured"
    else
        echo "⚠️  AWS configuration not detected"
        echo "   Run: aws configure"
        echo "   Or set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
    fi
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Virtual environment setup
VENV_PATH="$SCRIPT_DIR/venv"
echo "📦 Using virtual environment: $VENV_PATH"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

echo "🔄 Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Install dependencies
echo "📦 Installing Python dependencies..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    echo "Installing basic dependencies..."
    pip install --upgrade pip
    pip install flask flask-socketio boto3 python-dotenv eventlet
fi

# Load environment variables
ENV_FILE="$PROJECT_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
    echo "🔧 Loading environment configuration: $ENV_FILE"
    set -a  # automatically export all variables
    source "$ENV_FILE"
    set +a  # stop automatically exporting
else
    echo "⚠️  .env file not found, using default configuration"
    export MCP_ENDPOINT_URL="${MCP_ENDPOINT_URL:-https://your-api-gateway-id.execute-api.us-east-1.amazonaws.com/dev/lambda/mcp/}"
    export FLASK_PORT="${FLASK_PORT:-5002}"
    export FLASK_HOST="${FLASK_HOST:-0.0.0.0}"
    export FLASK_DEBUG="${FLASK_DEBUG:-true}"
fi

# Check AWS configuration
check_aws_config

# Display configuration
echo "🔗 MCP Endpoint: ${MCP_ENDPOINT_URL}"
echo "🔗 Server Port: ${FLASK_PORT:-5002}"
echo "🔗 Server Host: ${FLASK_HOST:-0.0.0.0}"

# Start chatbot
echo "🚀 Starting chatbot server..."
echo "📱 Open browser at: http://localhost:${FLASK_PORT:-5002}"
echo "🛑 Press Ctrl+C to stop server"
echo ""

cd "$SCRIPT_DIR"
python app.py