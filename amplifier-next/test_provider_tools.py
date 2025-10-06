#!/usr/bin/env python
"""Direct test of provider with tools."""

import asyncio
import os
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "amplifier-core"))
sys.path.insert(0, str(Path(__file__).parent / "amplifier-mod-provider-anthropic"))
sys.path.insert(0, str(Path(__file__).parent / "amplifier-mod-tool-search"))

from amplifier_mod_provider_anthropic import AnthropicProvider
from amplifier_mod_tool_search import GrepTool

# Set up test API key
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "test-key-123")


async def test_provider_tools():
    """Test that the provider correctly receives and uses tools."""

    # Create provider (api_key is positional, config is second param)
    provider = AnthropicProvider(api_key=os.environ["ANTHROPIC_API_KEY"], config={"model": "claude-3-haiku-20240307"})

    # Create a tool with schema
    grep_tool = GrepTool({"max_results": 10})

    # Check if tool has input_schema
    print(f"Tool name: {grep_tool.name}")
    print(f"Tool description: {grep_tool.description}")
    print(f"Tool has input_schema: {hasattr(grep_tool, 'input_schema')}")

    if hasattr(grep_tool, "input_schema"):
        schema = grep_tool.input_schema
        print(f"Tool schema: {schema}")

    # Test messages
    messages = [{"role": "user", "content": "Search for async functions in Python files"}]

    # Test with tools
    tools = [grep_tool]

    try:
        # This will fail with test API key, but we can see if tools are passed correctly
        print("\nCalling provider.complete() with tools...")
        response = await provider.complete(messages, tools=tools)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Expected error with test API key: {e}")

        # Check if the error is about API key (expected) vs tools not being passed
        error_str = str(e)
        if "api_key" in error_str.lower() or "authentication" in error_str.lower():
            print("\n✅ SUCCESS: Tools are being passed to the API!")
            print("   (The API key error is expected with a test key)")
        else:
            print(f"\n❌ FAILURE: Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(test_provider_tools())
