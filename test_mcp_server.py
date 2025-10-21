#!/usr/bin/env python3
"""
Test script for the Simple MCP Server

This script demonstrates how to interact with the MCP server
by sending various requests and displaying the responses.
"""

import subprocess
import json
import sys


def test_mcp_server(request, description):
    """Send a request to the MCP server and display the response."""
    print(f"\n{'='*60}")
    print(f"Test: {description}")
    print(f"{'='*60}")
    print(f"Request: {json.dumps(request, indent=2)}")
    
    try:
        # Run the MCP server and send the request
        process = subprocess.Popen(
            ['python3', 'mcp_server.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send request and get response
        stdout, stderr = process.communicate(input=json.dumps(request) + '\n', timeout=5)
        
        # Parse and display response (skip the startup message in stderr)
        response_lines = stdout.strip().split('\n')
        for line in response_lines:
            if line:
                try:
                    response = json.loads(line)
                    print(f"\nResponse: {json.dumps(response, indent=2)}")
                except json.JSONDecodeError:
                    print(f"Raw output: {line}")
        
        print(f"\n✓ Test passed")
        return True
        
    except subprocess.TimeoutExpired:
        print(f"\n✗ Test failed: Timeout")
        process.kill()
        return False
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        return False


def main():
    """Run all MCP server tests."""
    print("="*60)
    print("Simple MCP Server Test Suite")
    print("="*60)
    
    tests = [
        (
            {"method": "initialize", "params": {}},
            "Initialize Server"
        ),
        (
            {"method": "tools/list", "params": {}},
            "List Available Tools"
        ),
        (
            {"method": "tools/call", "params": {"name": "echo", "arguments": {"message": "Hello from test!"}}},
            "Call Echo Tool"
        ),
        (
            {"method": "resources/list", "params": {}},
            "List Available Resources"
        ),
        (
            {"method": "resources/read", "params": {"uri": "file:///example.txt"}},
            "Read Example Resource"
        ),
        (
            {"method": "unknown_method", "params": {}},
            "Test Unknown Method (Error Handling)"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for request, description in tests:
        if test_mcp_server(request, description):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    print("="*60)
    
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
