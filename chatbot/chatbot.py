import json
import asyncio
import aiohttp
import gradio as gr
import boto3
import os
from typing import List, Dict, Any, AsyncGenerator
from datetime import datetime

class MCPChatbot:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
        self.mcp_url = os.getenv('MCP_SERVER_URL')
        self.conversation_history = []
        self.mcp_tools = []
        
        # 验证MCP服务器URL
        if not self.mcp_url:
            raise ValueError("MCP_SERVER_URL environment variable is required")
        
    async def initialize_mcp_tools(self):
        try:
            async with aiohttp.ClientSession() as session:
                list_tools_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list"
                }
                
                async with session.post(
                    self.mcp_url,
                    json=list_tools_request,
                    headers={"Accept": "application/json, text/event-stream"}
                ) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        
                        # Handle event-stream format
                        if 'event-stream' in response.headers.get('content-type', ''):
                            lines = response_text.strip().split('\n')
                            for line in lines:
                                if line.startswith('data: '):
                                    json_str = line[6:]  # Remove 'data: ' prefix
                                    try:
                                        result = json.loads(json_str)
                                        if "result" in result and "tools" in result["result"]:
                                            self.mcp_tools = result["result"]["tools"]
                                            return f"Successfully loaded {len(self.mcp_tools)} MCP tools"
                                    except json.JSONDecodeError:
                                        continue
                        else:
                            # Handle regular JSON
                            try:
                                result = json.loads(response_text)
                                if "result" in result and "tools" in result["result"]:
                                    self.mcp_tools = result["result"]["tools"]
                                    return f"Successfully loaded {len(self.mcp_tools)} MCP tools"
                            except json.JSONDecodeError:
                                pass
                    return f"Failed to load MCP tools (status: {response.status})"
        except Exception as e:
            return f"Error initializing MCP tools: {str(e)}"

    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                tool_call_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
                
                async with session.post(
                    self.mcp_url,
                    json=tool_call_request,
                    headers={"Accept": "application/json, text/event-stream"}
                ) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        
                        # Handle event-stream format
                        if 'event-stream' in response.headers.get('content-type', ''):
                            lines = response_text.strip().split('\n')
                            for line in lines:
                                if line.startswith('data: '):
                                    json_str = line[6:]  # Remove 'data: ' prefix
                                    try:
                                        result = json.loads(json_str)
                                        if "result" in result:
                                            content = result["result"].get("content", [])
                                            if content and isinstance(content, list) and len(content) > 0:
                                                return content[0].get("text", "No text content")
                                    except json.JSONDecodeError:
                                        continue
                        else:
                            # Handle regular JSON
                            try:
                                result = json.loads(response_text)
                                if "result" in result:
                                    content = result["result"].get("content", [])
                                    if content and isinstance(content, list) and len(content) > 0:
                                        return content[0].get("text", "No text content")
                            except json.JSONDecodeError:
                                pass
                        return "Tool executed but no content returned"
                    return f"Tool call failed with status {response.status}"
        except Exception as e:
            return f"Error calling MCP tool: {str(e)}"

    def format_tools_for_bedrock(self) -> List[Dict]:
        bedrock_tools = []
        for tool in self.mcp_tools:
            bedrock_tool = {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "input_schema": tool.get("inputSchema", {})
            }
            bedrock_tools.append(bedrock_tool)
        return bedrock_tools

    async def chat_with_tools(self, user_message: str) -> AsyncGenerator[str, None]:
        self.conversation_history.append({"role": "user", "content": user_message})
        
        yield f"🤖 Processing your message: {user_message}\n\n"
        
        if not self.mcp_tools:
            init_result = await self.initialize_mcp_tools()
            yield f"📋 {init_result}\n\n"
        
        # 构建包含工具使用指令的系统消息
        system_message = """You are an AI assistant with access to Python code execution tools. When users ask for calculations, data analysis, or code execution, you should USE THE AVAILABLE TOOLS to provide accurate results. 

For example:
- If asked to calculate something (like π, mathematical expressions, etc.), use the Python tool to calculate it
- If asked to generate and run code, use the Python tool
- Always prefer using tools for computational tasks rather than providing theoretical explanations only

Available tools will be provided in the function calling interface."""
        
        # 使用完整的对话历史，不仅仅是当前消息
        messages = self.conversation_history.copy()
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": messages,
            "max_tokens": int(os.getenv('MAX_TOKENS', '65536')),
            "temperature": 0.7,
            "system": system_message
        }
        
        if self.mcp_tools:
            request_body["tools"] = self.format_tools_for_bedrock()
            yield f"🔧 Available tools: {', '.join([tool['name'] for tool in self.mcp_tools])}\n\n"

        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            
            if response_body.get("stop_reason") == "tool_use":
                yield "🔨 Claude wants to use tools...\n\n"
                
                for content_block in response_body.get("content", []):
                    if content_block.get("type") == "tool_use":
                        tool_name = content_block.get("name")
                        tool_input = content_block.get("input", {})
                        tool_use_id = content_block.get("id")
                        
                        yield f"🛠️ Calling tool: {tool_name}\n"
                        yield f"📋 Parameters: {json.dumps(tool_input, indent=2)}\n\n"
                        
                        tool_result = await self.call_mcp_tool(tool_name, tool_input)
                        yield f"✅ Tool result:\n```\n{tool_result}\n```\n\n"
                        
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": response_body.get("content", [])
                        })
                        
                        self.conversation_history.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": tool_result
                            }]
                        })
                        
                        follow_up_messages = [{"role": msg["role"], "content": msg["content"]} for msg in self.conversation_history]
                        
                        follow_up_request = {
                            "anthropic_version": "bedrock-2023-05-31",
                            "messages": follow_up_messages,
                            "max_tokens": int(os.getenv('MAX_TOKENS', '65536')),
                            "temperature": 0.7,
                            "tools": self.format_tools_for_bedrock()
                        }
                        
                        follow_up_response = self.bedrock.invoke_model(
                            modelId=self.model_id,
                            body=json.dumps(follow_up_request),
                            contentType="application/json"
                        )
                        
                        follow_up_body = json.loads(follow_up_response['body'].read())
                        final_content = ""
                        
                        for content_block in follow_up_body.get("content", []):
                            if content_block.get("type") == "text":
                                final_content += content_block.get("text", "")
                        
                        yield f"💬 Claude's response:\n{final_content}\n"
                        
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": final_content
                        })
            else:
                assistant_message = ""
                for content_block in response_body.get("content", []):
                    if content_block.get("type") == "text":
                        assistant_message += content_block.get("text", "")
                
                yield f"💬 Claude's response:\n{assistant_message}\n"
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
        except Exception as e:
            yield f"❌ Error: {str(e)}\n"

chatbot = MCPChatbot()

def create_gradio_interface():
    def chat_fn(message, history):
        """实时流式聊天函数 - 支持多轮对话"""
        if not message.strip():
            yield history, ""
            return
        
        # 同步UI历史到chatbot内部历史
        # 只有在UI历史与内部历史不同步时才更新
        if history:
            # 重建内部对话历史
            chatbot.conversation_history = []
            for msg in history:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    chatbot.conversation_history.append({
                        "role": msg["role"], 
                        "content": msg["content"]
                    })
        
        # 添加用户消息到历史（使用messages格式）
        history = history or []
        history.append({"role": "user", "content": message})
        
        # 立即显示用户消息
        yield history, ""
        
        # 添加助手消息占位符
        history.append({"role": "assistant", "content": ""})
        ai_response = ""
        
        # 创建新的事件循环处理异步调用
        import threading
        import queue
        import asyncio
        import time
        
        result_queue = queue.Queue()
        
        def run_async_chat():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def collect_chunks():
                async for chunk in chatbot.chat_with_tools(message):
                    result_queue.put(chunk)
                result_queue.put(None)  # 结束标记
            
            loop.run_until_complete(collect_chunks())
            loop.close()
        
        # 在新线程中运行异步函数
        thread = threading.Thread(target=run_async_chat)
        thread.start()
        
        # 实时流式收集和显示结果
        while True:
            try:
                chunk = result_queue.get(timeout=0.1)  # 减小超时时间以提高响应性
                if chunk is None:  # 结束标记
                    break
                ai_response += chunk
                # 更新最后一条回复并立即yield
                history[-1]["content"] = ai_response
                yield history, ""
                time.sleep(0.05)  # 小延迟让用户看到流式效果
            except queue.Empty:
                # 即使没有新内容也要yield保持连接
                yield history, ""
                continue
        
        thread.join()
        # 最终确认
        yield history, ""
    
    def clear_fn():
        chatbot.conversation_history = []
        return [], ""
    
    with gr.Blocks(title="Lambda-code-interpreter Chatbot Demo", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🤖 Lambda-code-interpreter Chatbot Demo")
        gr.Markdown("This chatbot uses AWS Bedrock Claude 3.7 Sonnet with MCP tools via streamableHttp")
        
        chatbot_ui = gr.Chatbot(
            label="Chat with Lambda-code-interpreter Bot",
            height=600,
            show_copy_button=True,
            placeholder="Welcome! Ask me to calculate something or run Python code...",
            type="messages",
            scale=1,
            min_height=300,
            max_height=800,
            autoscroll=True
        )
        
        with gr.Row():
            msg = gr.Textbox(
                label="Your message",
                placeholder="Type your message here... (e.g., '计算圆周率到10位小数')",
                scale=4,
                lines=2
            )
            send_btn = gr.Button("Send", variant="primary", scale=1)
            clear_btn = gr.Button("Clear Chat", variant="secondary", scale=1)
        
        # 事件绑定 - 简化版本
        msg.submit(
            chat_fn,
            inputs=[msg, chatbot_ui],
            outputs=[chatbot_ui, msg]
        )
        
        send_btn.click(
            chat_fn,
            inputs=[msg, chatbot_ui],
            outputs=[chatbot_ui, msg]
        )
        
        clear_btn.click(
            clear_fn,
            outputs=[chatbot_ui, msg]
        )
        
        gr.Markdown("""
        ### 使用说明:
        1. 输入消息并点击发送或按Enter
        2. 如果Claude需要使用工具，会显示工具调用过程
        3. 支持Python代码执行
        4. 点击"Clear Chat"清空对话历史
        """)
    
    return demo

if __name__ == "__main__":
    # 从环境变量获取配置
    server_host = os.getenv('GRADIO_SERVER_HOST', '0.0.0.0')
    server_port = int(os.getenv('GRADIO_SERVER_PORT', '7860'))
    debug_mode = os.getenv('DEBUG', 'true').lower() == 'true'
    
    print(f"🚀 Starting Lambda-code-interpreter Chatbot...")
    print(f"🌐 MCP Server: {os.getenv('MCP_SERVER_URL', 'default')}")
    print(f"📱 Interface: http://{server_host}:{server_port}")
    print(f"🔧 Debug mode: {'enabled' if debug_mode else 'disabled'}")
    
    demo = create_gradio_interface()
    demo.launch(
        server_name=server_host,
        server_port=server_port,
        share=False,
        debug=debug_mode
    )