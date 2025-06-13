#!/usr/bin/env python3
"""
Simple MCP client for testing the deployed Lambda MCP server.

This client uses only standard library components to test basic MCP functionality.
"""

import json
import urllib.request
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError


class SimpleMCPClient:
    """Simple MCP client using standard library only."""
    
    def __init__(self, base_url: str):
        """Initialize client with MCP server base URL."""
        self.base_url = base_url.rstrip('/')
    
    def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send an MCP request to the server."""
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        data = json.dumps(request_data).encode('utf-8')
        
        req = urllib.request.Request(
            f"{self.base_url}/lambda/mcp/",
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream'
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                response_text = response.read().decode('utf-8')
                print(f"Response status: {response.code}")
                print(f"Response headers: {dict(response.headers)}")
                print(f"Raw response: {response_text}")
                
                return self._parse_response(response_text, response.headers)
                
        except (HTTPError, URLError) as e:
            return self._handle_error(e)
    
    def _parse_response(self, response_text: str, headers) -> Dict[str, Any]:
        """Parse response handling both JSON and SSE formats."""
        content_type = headers.get('content-type', '')
        
        if content_type.startswith('text/event-stream'):
            # Parse Server-Sent Events format
            lines = response_text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    return json.loads(line[6:])  # Remove 'data: ' prefix
            raise ValueError("No data found in SSE response")
        else:
            return json.loads(response_text)
    
    def _handle_error(self, error) -> Dict[str, Any]:
        """Handle HTTP and URL errors."""
        if isinstance(error, HTTPError):
            error_body = error.read().decode('utf-8') if error.fp else "No error body"
            print(f"HTTP Error {error.code}: {error_body}")
            print(f"Response headers: {dict(error.headers)}")
            if 'Location' in error.headers:
                print(f"Redirect location: {error.headers['Location']}")
        else:
            print(f"URL Error: {error}")
        
        raise error
    
    def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP session"""
        return self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "simple-test-client",
                "version": "1.0.0"
            }
        })
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        return self.send_request("tools/list")
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool"""
        return self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

def test_mcp_server():
    """Test the deployed MCP server with comprehensive checks."""
    api_endpoint = "https://YOUR_API_GATEWAY_ID.execute-api.YOUR_REGION.amazonaws.com/dev"
    
    print("🚀 MCP Server Test Suite")
    print(f"Testing MCP server at: {api_endpoint}")
    print("-" * 50)
    
    client = SimpleMCPClient(api_endpoint)
    
    tests = [
        ("Initialize MCP session", lambda: client.initialize()),
        ("List available tools", lambda: client.list_tools()),
        ("Execute Python code", lambda: client.call_tool("execute_python", {
            "code": "print('Hello from Python interpreter!')\nresult = 2 + 2\nprint(f'2 + 2 = {result}')"
        })),
        ("Get environment info", lambda: client.call_tool("get_environment_info", {})),
        ("List preinstalled packages", lambda: client.call_tool("list_preinstalled_packages", {}))
    ]
    
    passed = 0
    total = len(tests)
    
    for i, (test_name, test_func) in enumerate(tests, 1):
        try:
            print(f"{i}. {test_name}...")
            response = test_func()
            print(f"✅ {test_name} - PASSED")
            print(json.dumps(response, indent=2))
            print()
            passed += 1
            
        except Exception as e:
            print(f"❌ {test_name} - FAILED")
            print(f"   Error: {str(e)}")
            print()
    
    print("🏁 Test Results")
    print("-" * 20)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests completed successfully!")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")


def main():
    """Main entry point."""
    import os
    
    # Check for environment variable override
    api_endpoint = os.environ.get('MCP_ENDPOINT_URL')
    if api_endpoint:
        print(f"Using MCP endpoint from environment: {api_endpoint}")
        # Update the global endpoint for testing
        globals()['test_mcp_server'].__defaults__ = ()
        client = SimpleMCPClient(api_endpoint.replace('/lambda/mcp/', ''))
        # Run simplified test
        try:
            print("Testing connection...")
            response = client.list_tools()
            print("✅ Connection successful!")
            print(json.dumps(response, indent=2))
        except Exception as e:
            print(f"❌ Connection failed: {e}")
    else:
        test_mcp_server()


if __name__ == "__main__":
    main()