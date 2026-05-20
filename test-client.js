#!/usr/bin/env node

/**
 * Simple test client for the MCP server
 * This demonstrates how to interact with the MCP server
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function runTests() {
  console.log("🚀 Starting MCP Server Test Client\n");

  // Create transport with command and args
  const transport = new StdioClientTransport({
    command: "node",
    args: ["mcp-server.js"],
  });

  const client = new Client(
    {
      name: "test-client",
      version: "1.0.0",
    },
    {
      capabilities: {},
    }
  );

  try {
    await client.connect(transport);
    console.log("✓ Connected to MCP server\n");

    // Test 1: List available tools
    console.log("📋 Test 1: Listing available tools");
    const tools = await client.listTools();
    console.log(`Found ${tools.tools.length} tools:`);
    tools.tools.forEach((tool) => {
      console.log(`  - ${tool.name}: ${tool.description}`);
    });
    console.log();

    // Test 2: Echo tool
    console.log("💬 Test 2: Testing echo tool");
    const echoResult = await client.callTool({
      name: "echo",
      arguments: { message: "Hello, MCP Server!" },
    });
    console.log("Response:", echoResult.content[0].text);
    console.log();

    // Test 3: Calculate tool - Addition
    console.log("➕ Test 3: Testing calculate tool (addition)");
    const addResult = await client.callTool({
      name: "calculate",
      arguments: { operation: "add", a: 15, b: 7 },
    });
    console.log("Response:", addResult.content[0].text);
    console.log();

    // Test 4: Calculate tool - Multiplication
    console.log("✖️  Test 4: Testing calculate tool (multiplication)");
    const multiplyResult = await client.callTool({
      name: "calculate",
      arguments: { operation: "multiply", a: 6, b: 7 },
    });
    console.log("Response:", multiplyResult.content[0].text);
    console.log();

    // Test 5: Get timestamp tool
    console.log("🕐 Test 5: Testing get_timestamp tool");
    const timestampResult = await client.callTool({
      name: "get_timestamp",
      arguments: { format: "iso" },
    });
    console.log("Response:", timestampResult.content[0].text);
    console.log();

    // Test 6: List resources
    console.log("📚 Test 6: Listing available resources");
    const resources = await client.listResources();
    console.log(`Found ${resources.resources.length} resources:`);
    resources.resources.forEach((resource) => {
      console.log(`  - ${resource.name} (${resource.uri})`);
    });
    console.log();

    // Test 7: Read server info resource
    console.log("📖 Test 7: Reading server information resource");
    const serverInfo = await client.readResource({ uri: "info://server" });
    console.log("Server Info:");
    console.log(serverInfo.contents[0].text);
    console.log();

    // Test 8: Read capabilities resource
    console.log("⚙️  Test 8: Reading server capabilities resource");
    const capabilities = await client.readResource({ uri: "info://capabilities" });
    console.log("Capabilities:");
    console.log(capabilities.contents[0].text);
    console.log();

    console.log("✅ All tests completed successfully!");
  } catch (error) {
    console.error("❌ Test failed:", error);
    process.exit(1);
  } finally {
    await client.close();
  }
}

runTests().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
