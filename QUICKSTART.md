# Quick Start Guide

## Get Started in 3 Steps

### 1. Install Dependencies

```bash
npm install
```

### 2. Test the Server

Run the test client to verify everything works:

```bash
npm test
```

You should see output showing all 8 tests passing successfully.

### 3. Run the Server

Start the MCP server:

```bash
npm start
```

The server will run on stdio and wait for MCP protocol messages.

## Using with AI Assistants

### GitHub Copilot

1. Create or edit your MCP configuration file (location varies by platform):
   - **macOS/Linux**: `~/.config/github-copilot/mcp.json`
   - **Windows**: `%APPDATA%\GitHub Copilot\mcp.json`

2. Add the server configuration:

```json
{
  "mcpServers": {
    "simple-server": {
      "command": "node",
      "args": ["/full/path/to/mcp-server.js"]
    }
  }
}
```

3. Restart your IDE or Copilot extension

### Claude Desktop

1. Edit your Claude Desktop configuration:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the server:

```json
{
  "mcpServers": {
    "simple-server": {
      "command": "node",
      "args": ["/full/path/to/mcp-server.js"]
    }
  }
}
```

3. Restart Claude Desktop

## Example Interactions

Once configured, you can ask your AI assistant to:

- "Echo the message 'Hello World'"
- "Calculate 25 + 17"
- "What's 8 multiplied by 9?"
- "Get the current timestamp in ISO format"
- "Show me the server information"

The AI will use the MCP tools automatically to fulfill these requests!

## Troubleshooting

### Server won't start
- Make sure Node.js is installed: `node --version` (requires v18+)
- Verify dependencies are installed: `npm install`
- Check for error messages in the console

### AI assistant can't find the server
- Double-check the path in your MCP configuration
- Use absolute paths, not relative paths
- Restart your IDE/application after changing config

### Tools not working
- Run `npm test` to verify the server works
- Check the AI assistant's logs for error messages
- Ensure you're using the latest version of the MCP SDK

## Next Steps

- Extend the server with custom tools for your use case
- Add more resources for your specific domain
- Explore the [MCP SDK documentation](https://github.com/modelcontextprotocol/sdk)
