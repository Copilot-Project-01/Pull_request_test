# Simple Copilot MCP Server

A simple implementation of a Model Context Protocol (MCP) server for GitHub Copilot and other AI assistants.

## What is MCP?

The Model Context Protocol (MCP) is a standard for communication between AI assistants and external tools/resources. This server provides a simple example of how to create an MCP server with basic tools and resources.

## Features

This MCP server provides three basic tools:

1. **Echo Tool** - Echoes back any message you send
2. **Calculate Tool** - Performs basic arithmetic operations (add, subtract, multiply, divide)
3. **Get Timestamp Tool** - Returns the current timestamp in various formats (ISO, Unix, Locale)

And two resources:

1. **Server Information** - Details about the server
2. **Server Capabilities** - JSON description of available tools and resources

## Installation

```bash
npm install
```

## Usage

### Running the Server

The MCP server runs on stdio (standard input/output):

```bash
npm start
```

Or directly:

```bash
node mcp-server.js
```

### Configuring with Copilot

To use this server with GitHub Copilot or other MCP clients, add it to your MCP configuration file (typically `~/.config/copilot/mcp.json` or similar):

```json
{
  "mcpServers": {
    "simple-server": {
      "command": "node",
      "args": ["/path/to/Pull_request_test/mcp-server.js"]
    }
  }
}
```

### Testing the Server

You can test the server using the included test client:

```bash
npm test
```

## Available Tools

### Echo Tool

Echoes back the provided message.

**Parameters:**
- `message` (string, required): The message to echo back

**Example:**
```json
{
  "name": "echo",
  "arguments": {
    "message": "Hello, MCP!"
  }
}
```

### Calculate Tool

Performs basic arithmetic operations.

**Parameters:**
- `operation` (string, required): One of "add", "subtract", "multiply", "divide"
- `a` (number, required): First number
- `b` (number, required): Second number

**Example:**
```json
{
  "name": "calculate",
  "arguments": {
    "operation": "add",
    "a": 10,
    "b": 5
  }
}
```

### Get Timestamp Tool

Returns the current timestamp in the specified format.

**Parameters:**
- `format` (string, optional): One of "iso", "unix", "locale" (default: "iso")

**Example:**
```json
{
  "name": "get_timestamp",
  "arguments": {
    "format": "iso"
  }
}
```

## Available Resources

### Server Information

- **URI:** `info://server`
- **Description:** General information about the MCP server

### Server Capabilities

- **URI:** `info://capabilities`
- **Description:** JSON description of server capabilities, tools, and resources

## Development

The server is built using the official MCP SDK:
- [@modelcontextprotocol/sdk](https://github.com/modelcontextprotocol/sdk)

## Architecture

The server follows the MCP specification:

1. **Transport Layer**: Uses stdio for communication
2. **Protocol Layer**: Implements MCP message protocol
3. **Tool Layer**: Provides callable tools with defined schemas
4. **Resource Layer**: Exposes queryable resources

## License

MIT
