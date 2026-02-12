#!/usr/bin/env python3
"""
Simple Copilot MCP (Model Context Protocol) Server

This is a basic implementation of an MCP server that demonstrates
the core concepts of the Model Context Protocol for GitHub Copilot.
"""

import json
import sys
from typing import Dict, List, Any


class MCPServer:
    """A simple MCP server implementation."""
    
    def __init__(self, name: str = "simple-mcp-server", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools = {}
        self.resources = {}
        
    def register_tool(self, name: str, description: str, handler):
        """Register a tool with the MCP server."""
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler
        }
        
    def register_resource(self, uri: str, name: str, description: str, content: str):
        """Register a resource with the MCP server."""
        self.resources[uri] = {
            "uri": uri,
            "name": name,
            "description": description,
            "content": content
        }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming MCP request."""
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "initialize":
            return self._handle_initialize(params)
        elif method == "tools/list":
            return self._handle_list_tools()
        elif method == "tools/call":
            return self._handle_call_tool(params)
        elif method == "resources/list":
            return self._handle_list_resources()
        elif method == "resources/read":
            return self._handle_read_resource(params)
        else:
            return {"error": f"Unknown method: {method}"}
    
    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request."""
        return {
            "protocolVersion": "1.0",
            "serverInfo": {
                "name": self.name,
                "version": self.version
            },
            "capabilities": {
                "tools": {},
                "resources": {}
            }
        }
    
    def _handle_list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        return {
            "tools": [
                {
                    "name": tool["name"],
                    "description": tool["description"]
                }
                for tool in self.tools.values()
            ]
        }
    
    def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a registered tool."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return {"error": f"Tool not found: {tool_name}"}
        
        try:
            result = self.tools[tool_name]["handler"](arguments)
            return {"content": [{"type": "text", "text": result}]}
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_list_resources(self) -> Dict[str, Any]:
        """List available resources."""
        return {
            "resources": [
                {
                    "uri": resource["uri"],
                    "name": resource["name"],
                    "description": resource["description"]
                }
                for resource in self.resources.values()
            ]
        }
    
    def _handle_read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a resource."""
        uri = params.get("uri")
        
        if uri not in self.resources:
            return {"error": f"Resource not found: {uri}"}
        
        resource = self.resources[uri]
        return {
            "contents": [
                {
                    "uri": resource["uri"],
                    "mimeType": "text/plain",
                    "text": resource["content"]
                }
            ]
        }
    
    def run(self):
        """Run the MCP server (stdio mode)."""
        print(f"Starting {self.name} v{self.version}...", file=sys.stderr)
        
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = self.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError as e:
                error_response = {"error": f"Invalid JSON: {str(e)}"}
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                error_response = {"error": f"Server error: {str(e)}"}
                print(json.dumps(error_response))
                sys.stdout.flush()


def example_tool_handler(args: Dict[str, Any]) -> str:
    """Example tool handler - echoes back the input."""
    message = args.get("message", "Hello from MCP!")
    return f"Echo: {message}"


def main():
    """Main entry point for the MCP server."""
    # Create and configure the server
    server = MCPServer(name="simple-mcp-server", version="1.0.0")
    
    # Register example tool
    server.register_tool(
        name="echo",
        description="Echoes back the provided message",
        handler=example_tool_handler
    )
    
    # Register example resource
    server.register_resource(
        uri="file:///example.txt",
        name="Example Resource",
        description="An example resource for demonstration",
        content="This is an example resource content."
    )
    
    # Run the server
    server.run()


if __name__ == "__main__":
    main()
