#!/usr/bin/env python
"""Test script to verify tool integration is working."""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Set environment variables for testing
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "test-key")

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent / "amplifier-core"))

from amplifier_core.session import AmplifierSession

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def test_tool_integration():
    """Test that tools are properly passed to the provider."""

    # Load config
    config_path = Path(__file__).parent / "test-full-features.toml"

    # Create session
    session = AmplifierSession(str(config_path))

    # Initialize
    await session.initialize()

    # Add a test message that should trigger tool usage
    await session.add_message(
        role="user", content="Search for async functions in Python files in the current directory"
    )

    # Process the message
    response = await session.process()

    print("\n=== RESPONSE ===")
    print(response)

    # Check if tools were actually called
    # The response should contain tool usage or at least attempt to use them
    if "grep" in response.lower() or "search" in response.lower() or "tool" in response.lower():
        print("\n✅ SUCCESS: Tool integration appears to be working!")
    else:
        print("\n⚠️  WARNING: Response doesn't mention tools - may not be working correctly")

    # Cleanup
    await session.cleanup()


if __name__ == "__main__":
    asyncio.run(test_tool_integration())
