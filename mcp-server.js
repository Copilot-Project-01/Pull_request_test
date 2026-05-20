#!/usr/bin/env node

/**
 * Simple Copilot MCP (Model Context Protocol) Server
 * 
 * This server provides basic tools and resources that can be used
 * by AI assistants through the Model Context Protocol.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

/**
 * Create and configure the MCP server
 */
class SimpleMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: "simple-copilot-mcp-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
          resources: {},
        },
      }
    );

    this.setupHandlers();
  }

  /**
   * Setup request handlers for the MCP server
   */
  setupHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "echo",
          description: "Echoes back the provided message",
          inputSchema: {
            type: "object",
            properties: {
              message: {
                type: "string",
                description: "The message to echo back",
              },
            },
            required: ["message"],
          },
        },
        {
          name: "calculate",
          description: "Performs basic arithmetic operations (add, subtract, multiply, divide)",
          inputSchema: {
            type: "object",
            properties: {
              operation: {
                type: "string",
                enum: ["add", "subtract", "multiply", "divide"],
                description: "The arithmetic operation to perform",
              },
              a: {
                type: "number",
                description: "First number",
              },
              b: {
                type: "number",
                description: "Second number",
              },
            },
            required: ["operation", "a", "b"],
          },
        },
        {
          name: "get_timestamp",
          description: "Returns the current timestamp",
          inputSchema: {
            type: "object",
            properties: {
              format: {
                type: "string",
                enum: ["iso", "unix", "locale"],
                description: "Format of the timestamp (default: iso)",
              },
            },
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "echo":
            return {
              content: [
                {
                  type: "text",
                  text: `Echo: ${args.message}`,
                },
              ],
            };

          case "calculate":
            const { operation, a, b } = args;
            let result;
            
            switch (operation) {
              case "add":
                result = a + b;
                break;
              case "subtract":
                result = a - b;
                break;
              case "multiply":
                result = a * b;
                break;
              case "divide":
                if (b === 0) {
                  throw new Error("Division by zero is not allowed");
                }
                result = a / b;
                break;
              default:
                throw new Error(`Unknown operation: ${operation}`);
            }

            return {
              content: [
                {
                  type: "text",
                  text: `Result: ${a} ${operation} ${b} = ${result}`,
                },
              ],
            };

          case "get_timestamp":
            const format = args.format || "iso";
            const now = new Date();
            let timestamp;

            switch (format) {
              case "iso":
                timestamp = now.toISOString();
                break;
              case "unix":
                timestamp = Math.floor(now.getTime() / 1000).toString();
                break;
              case "locale":
                timestamp = now.toLocaleString();
                break;
              default:
                timestamp = now.toISOString();
            }

            return {
              content: [
                {
                  type: "text",
                  text: `Current timestamp (${format}): ${timestamp}`,
                },
              ],
            };

          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `Error: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    });

    // List available resources
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
      resources: [
        {
          uri: "info://server",
          name: "Server Information",
          description: "Information about this MCP server",
          mimeType: "text/plain",
        },
        {
          uri: "info://capabilities",
          name: "Server Capabilities",
          description: "List of server capabilities",
          mimeType: "application/json",
        },
      ],
    }));

    // Handle resource reads
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;

      switch (uri) {
        case "info://server":
          return {
            contents: [
              {
                uri,
                mimeType: "text/plain",
                text: "Simple Copilot MCP Server v1.0.0\n\n" +
                      "This is a basic MCP server implementation that provides:\n" +
                      "- Echo tool: Echoes back messages\n" +
                      "- Calculate tool: Performs basic arithmetic\n" +
                      "- Get timestamp tool: Returns current time in various formats\n\n" +
                      "For more information, visit the repository.",
              },
            ],
          };

        case "info://capabilities":
          return {
            contents: [
              {
                uri,
                mimeType: "application/json",
                text: JSON.stringify(
                  {
                    tools: ["echo", "calculate", "get_timestamp"],
                    resources: ["info://server", "info://capabilities"],
                    version: "1.0.0",
                  },
                  null,
                  2
                ),
              },
            ],
          };

        default:
          throw new Error(`Unknown resource: ${uri}`);
      }
    });
  }

  /**
   * Start the MCP server
   */
  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Simple Copilot MCP Server running on stdio");
  }
}

// Start the server
const server = new SimpleMCPServer();
server.run().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
