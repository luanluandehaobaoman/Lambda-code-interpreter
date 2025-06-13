#!/usr/bin/env python3
"""
MCP Python Code Interpreter Chatbot

An intelligent chatbot that demonstrates MCP Python code interpreter functionality
using AWS Bedrock Claude 3.7 Sonnet model.
"""

import json
import logging
import os
import re
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

# Load environment variables from .env file in project root
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
load_dotenv(dotenv_path=env_path)


# Configure logging - show only important MCP and LLM interactions
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set specific module log levels
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Suppress verbose logs from third-party libraries
for lib in ['werkzeug', 'flask', 'botocore', 'boto3', 'urllib3', 'requests', 'socketio', 'engineio']:
    logging.getLogger(lib).setLevel(logging.WARNING)

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'mcp-chatbot-secret-key-2024')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuration constants
BEDROCK_TIMEOUT = 30
MCP_TIMEOUT = 60
MAX_LOG_ENTRIES = 100
DEFAULT_LOG_LIMIT = 50


class BedrockClient:
    """AWS Bedrock Claude client for natural language processing."""
    
    def __init__(self):
        """Initialize Bedrock client with configuration from environment variables."""
        try:
            self.bedrock = boto3.client(
                'bedrock-runtime',
                region_name=os.environ.get('AWS_REGION', 'us-east-1')
            )
            self.model_id = os.environ.get(
                'BEDROCK_MODEL_ID', 
                'us.anthropic.claude-3-7-sonnet-20250219-v1:0'
            )
            logger.info(f"Bedrock client initialized with model: {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.bedrock = None
    
    def generate_response(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response using Claude model."""
        if not self.bedrock:
            return "Bedrock service unavailable. Please check AWS configuration."
        
        logger.info(f"🤖 Claude request: {message[:100]}...")
        start_time = time.time()
        
        try:
            system_prompt = self._get_system_prompt()
            user_message = self._build_user_message(message, context)
            
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_message}],
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            elapsed = time.time() - start_time
            
            if response_body.get('content'):
                response_text = response_body['content'][0]['text']
                logger.info(f"✅ Claude response completed ({elapsed:.2f}s, {len(response_text)} chars)")
                return response_text
            else:
                logger.warning("⚠️ Claude returned empty response")
                return "Sorry, I cannot generate a response at the moment."
                
        except ClientError as e:
            return self._handle_client_error(e, time.time() - start_time)
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ Claude request exception ({elapsed:.2f}s): {str(e)}")
            return f"Error generating response: {str(e)}"
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for Claude."""
        return """You are a professional Python code assistant that can execute Python code through an MCP server.

Your capabilities:
1. Execute Python code and return results
2. Data analysis and visualization
3. Mathematical and scientific computing
4. Get Python environment information
5. List pre-installed Python packages

When users need to execute Python code, wrap it with <python_code> tags:
<python_code>
print("Hello, World!")
result = 2 + 2
</python_code>

Please respond in Chinese and provide useful, detailed explanations."""
    
    def _build_user_message(self, message: str, context: Optional[Dict[str, Any]]) -> str:
        """Build user message with optional context."""
        if context:
            return f"{message}\n\nCurrent context: {json.dumps(context, ensure_ascii=False, indent=2)}"
        return message
    
    def _handle_client_error(self, error: ClientError, elapsed: float) -> str:
        """Handle AWS client errors with appropriate messages."""
        error_code = error.response['Error']['Code']
        error_messages = {
            'AccessDeniedException': "Access denied. Please check AWS permissions.",
            'ThrottlingException': "Request rate too high. Please try again later.",
        }
        
        message = error_messages.get(error_code, f"Bedrock API error: {error_code}")
        logger.error(f"❌ Claude error ({elapsed:.2f}s): {error_code}")
        return message

class MCPClient:
    """MCP client for connecting to Lambda-based MCP server."""
    
    def __init__(self):
        """Initialize MCP client with environment configuration."""
        self.base_url = os.environ.get('MCP_ENDPOINT_URL')
        if not self.base_url:
            raise ValueError("MCP_ENDPOINT_URL environment variable is required")
        
        self.interaction_logs: List[Dict[str, Any]] = []
        self.session_id = str(uuid.uuid4())
        logger.info(f"MCP Client initialized - Session: {self.session_id}, URL: {self.base_url}")
    
    def _make_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send MCP request to Lambda server."""
        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time()),
            "method": method
        }
        
        if params:
            payload["params"] = params
        
        start_time = time.time()
        self._log_interaction("REQUEST", {
            "method": method,
            "params": params,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = Request(
                self.base_url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json, text/event-stream'
                }
            )
            
            with urlopen(req, timeout=MCP_TIMEOUT) as response:
                elapsed = time.time() - start_time
                response_text = response.read().decode('utf-8')
                result = self._parse_response(response_text, response.headers)
                
                self._log_interaction("RESPONSE", {
                    "method": method,
                    "result": result,
                    "elapsed": elapsed,
                    "status": response.code
                })
                
                return result
                
        except Exception as e:
            elapsed = time.time() - start_time
            error_msg = str(e)
            self._log_interaction("ERROR", {
                "method": method,
                "error": error_msg,
                "elapsed": elapsed
            })
            return {"error": error_msg}
    
    def _parse_response(self, response_text: str, headers) -> Dict[str, Any]:
        """Parse response handling both JSON and SSE formats."""
        content_type = headers.get('content-type', '')
        
        if content_type.startswith('text/event-stream'):
            lines = response_text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    return json.loads(line[6:])
            return {"error": "No data found in SSE response"}
        else:
            return json.loads(response_text)
    
    def execute_python(self, code: str, requirements: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute Python code via MCP server."""
        return self._make_request("tools/call", {
            "name": "execute_python",
            "arguments": {
                "code": code,
                "requirements": requirements or []
            }
        })
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get Python environment information."""
        return self._make_request("tools/call", {
            "name": "get_environment_info",
            "arguments": {}
        })
    
    def list_packages(self) -> Dict[str, Any]:
        """List pre-installed Python packages."""
        return self._make_request("tools/call", {
            "name": "list_preinstalled_packages", 
            "arguments": {}
        })
    
    def _log_interaction(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log MCP interaction with automatic cleanup."""
        log_entry = {
            "id": len(self.interaction_logs) + 1,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "type": event_type,
            "data": data
        }
        self.interaction_logs.append(log_entry)
        
        # Limit log entries to prevent memory bloat
        if len(self.interaction_logs) > MAX_LOG_ENTRIES:
            self.interaction_logs = self.interaction_logs[-DEFAULT_LOG_LIMIT:]
        
        # Log key information only
        self._log_summary(event_type, data)
    
    def _log_summary(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log summary information for different event types."""
        method = data.get("method", "unknown")
        
        if event_type == "REQUEST":
            params = data.get("params", {})
            tool_name = params.get("name", "") if params else ""
            target = f" -> {tool_name}" if tool_name else ""
            logger.info(f"🔄 MCP call: {method}{target}")
        elif event_type == "RESPONSE":
            elapsed = data.get("elapsed", 0)
            status = data.get("status", "unknown")
            logger.info(f"✅ MCP response: {method} ({elapsed:.2f}s, status={status})")
        elif event_type == "ERROR":
            error = data.get("error", "unknown")
            logger.error(f"❌ MCP error: {method} - {error}")
    
    def get_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent interaction logs."""
        return self.interaction_logs[-limit:] if self.interaction_logs else []
    
    def clear_logs(self) -> None:
        """Clear interaction logs."""
        self.interaction_logs = []

class ChatbotEngine:
    """Main chatbot engine coordinating Bedrock and MCP clients."""
    
    def __init__(self):
        """Initialize chatbot with Bedrock and MCP clients."""
        self.bedrock_client = BedrockClient()
        self.mcp_client = MCPClient()
        self.conversation_history: List[Dict[str, Any]] = []
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """Process user message and generate response with optional code execution."""
        try:
            # Record user message
            self._add_to_history("user", message)
            
            # Generate Claude response
            claude_response = self.bedrock_client.generate_response(message)
            
            # Execute Python code if present
            python_results = []
            if "<python_code>" in claude_response:
                python_results = self._execute_python_from_response(claude_response)
            
            # Record assistant response
            self._add_to_history("assistant", claude_response, python_results)
            
            return {
                "success": True,
                "response": claude_response,
                "python_results": python_results,
                "logs": self.mcp_client.get_logs(5)
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "success": False,
                "error": str(e),
                "logs": self.mcp_client.get_logs(5)
            }
    
    def _add_to_history(self, role: str, content: str, python_results: Optional[List[Dict[str, Any]]] = None) -> None:
        """Add message to conversation history."""
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if python_results:
            entry["python_results"] = python_results
        
        self.conversation_history.append(entry)
    
    def _execute_python_from_response(self, response: str) -> List[Dict[str, Any]]:
        """Extract and execute Python code blocks from Claude response."""
        code_blocks = re.findall(r'<python_code>(.*?)</python_code>', response, re.DOTALL)
        
        if not code_blocks:
            return []
        
        logger.info(f"🐍 Found {len(code_blocks)} Python code blocks, executing...")
        results = []
        
        for i, code in enumerate(code_blocks):
            code = code.strip()
            if not code:
                continue
                
            block_index = i + 1
            try:
                logger.info(f"🐍 Executing block {block_index}: {code[:50]}...")
                result = self.mcp_client.execute_python(code)
                
                # Check execution result
                success = result.get('result', {}).get('success', False)
                status = "success" if success else "failed"
                logger.info(f"{'✅' if success else '⚠️'} Block {block_index} {status}")
                
                results.append({
                    "block_index": block_index,
                    "code": code,
                    "result": result
                })
                
            except Exception as e:
                logger.error(f"❌ Block {block_index} execution error: {str(e)}")
                results.append({
                    "block_index": block_index,
                    "code": code,
                    "error": str(e)
                })
        
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            env_info = self.mcp_client.get_environment_info()
            packages_info = self.mcp_client.list_packages()
            
            return {
                "mcp_status": "connected" if not env_info.get("error") else "error",
                "bedrock_status": "connected" if self.bedrock_client.bedrock else "error",
                "environment": env_info,
                "packages": packages_info,
                "conversation_length": len(self.conversation_history),
                "log_count": len(self.mcp_client.interaction_logs)
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}

# Global chatbot instance
chatbot = ChatbotEngine()


# Flask Routes
@app.route('/')
def index():
    """Serve main chatbot interface."""
    return render_template('chatbot.html')


@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Handle chat requests."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data provided"})
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({"success": False, "error": "Message cannot be empty"})
        
        result = chatbot.process_message(message)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/status')
def status_api():
    """Get system status."""
    return jsonify(chatbot.get_system_status())


@app.route('/api/logs')
def logs_api():
    """Get MCP interaction logs."""
    try:
        limit = int(request.args.get('limit', 20))
        limit = min(max(limit, 1), 100)  # Clamp between 1 and 100
        logs = chatbot.mcp_client.get_logs(limit)
        return jsonify({"success": True, "logs": logs})
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid limit parameter"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/logs/clear', methods=['POST'])
def clear_logs_api():
    """Clear MCP logs."""
    try:
        chatbot.mcp_client.clear_logs()
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Clear logs error: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/conversation/clear', methods=['POST'])  
def clear_conversation_api():
    """Clear conversation history."""
    try:
        chatbot.conversation_history.clear()
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Clear conversation error: {e}")
        return jsonify({"success": False, "error": str(e)})

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    logger.info('Client connected')
    emit('status', chatbot.get_system_status())


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    logger.info('Client disconnected')


def main():
    """Main application entry point."""
    print("=" * 60)
    print("🤖 MCP Python Code Interpreter Chatbot")
    print("=" * 60)
    
    # Check AWS configuration
    try:
        credentials = boto3.Session().get_credentials()
        if credentials:
            logger.info("✅ AWS credentials configured")
        else:
            logger.warning("⚠️ AWS credentials not found")
    except Exception as e:
        logger.warning(f"⚠️ AWS credential check failed: {e}")
        logger.warning("Please configure AWS credentials to use Bedrock")
    
    # Start application
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5002))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    
    logger.info(f"🚀 Starting server at http://{host}:{port}")
    logger.info("📝 Log level: Showing MCP calls and LLM interactions only")
    logger.info("🛑 Press Ctrl+C to stop server")
    
    socketio.run(
        app, 
        debug=debug, 
        host=host, 
        port=port, 
        allow_unsafe_werkzeug=True
    )


if __name__ == '__main__':
    main()