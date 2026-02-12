# Simple Copilot MCP Server

A basic Python implementation of a Model Context Protocol (MCP) server for GitHub Copilot.

## What is MCP?

The Model Context Protocol (MCP) is a standard for communication between AI applications (like GitHub Copilot) and external tools/data sources. It allows AI assistants to interact with various resources and execute tools in a standardized way.

## Features

- **Tool Registration**: Register custom tools that can be called by the AI
- **Resource Management**: Manage and serve resources (files, data, etc.)
- **JSON-RPC Communication**: Standard JSON-based request/response protocol
- **Stdio Interface**: Communicates via standard input/output

## Installation

No external dependencies required! This implementation uses only Python standard library.

```bash
# Make the script executable
chmod +x mcp_server.py
```

## Usage

### Running the Server

```bash
python3 mcp_server.py
```

The server runs in stdio mode, reading JSON requests from stdin and writing JSON responses to stdout.

### Example Requests

#### Initialize the Server
```json
{"method": "initialize", "params": {}}
```

#### List Available Tools
```json
{"method": "tools/list", "params": {}}
```

#### Call a Tool
```json
{"method": "tools/call", "params": {"name": "echo", "arguments": {"message": "Hello MCP!"}}}
```

#### List Resources
```json
{"method": "resources/list", "params": {}}
```

#### Read a Resource
```json
{"method": "resources/read", "params": {"uri": "file:///example.txt"}}
```

## Testing the Server

You can test the server interactively:

```bash
# Start the server
python3 mcp_server.py

# Then type JSON requests (one per line):
{"method": "initialize", "params": {}}
{"method": "tools/list", "params": {}}
{"method": "tools/call", "params": {"name": "echo", "arguments": {"message": "Test"}}}
```

Or use echo and pipes:

```bash
echo '{"method": "initialize", "params": {}}' | python3 mcp_server.py
```

## Extending the Server

### Adding a Custom Tool

```python
def my_custom_tool(args: Dict[str, Any]) -> str:
    # Your tool logic here
    return "Result"

server.register_tool(
    name="my_tool",
    description="Description of what the tool does",
    handler=my_custom_tool
)
```

### Adding a Resource

```python
server.register_resource(
    uri="file:///my_resource.txt",
    name="My Resource",
    description="Description of the resource",
    content="Resource content here"
)
```

## Protocol Details

This implementation supports the following MCP methods:

- `initialize`: Initialize the server and return capabilities
- `tools/list`: List all available tools
- `tools/call`: Execute a registered tool
- `resources/list`: List all available resources
- `resources/read`: Read the content of a resource

## Requirements

- Python 3.6 or higher

## License

This is a simple demonstration implementation for educational purposes.
