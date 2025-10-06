#!/usr/bin/env python3
"""Test script to verify OpenAI provider works."""

import asyncio
import logging

from amplifier_core import AmplifierSession

# Enable logging to see what's happening
logging.basicConfig(level=logging.INFO)


async def test_openai():
    """Test OpenAI provider."""
    config = {
        "session": {"orchestrator": "loop-basic", "context": "context-simple"},
        "context": {"config": {"max_tokens": 200_000, "compact_threshold": 0.92}},
        "providers": [{"module": "provider-openai", "config": {"model": "gpt-4o"}}],
        "tools": [],
        "agents": [],
        "hooks": [],
    }

    print("\n=== Creating session ===")
    session = AmplifierSession(config)

    print("\n=== Initializing session ===")
    await session.initialize()

    # Check what was mounted
    providers = session.coordinator.get("providers")
    print(f"\n=== Mounted providers: {list(providers.keys()) if providers else 'None'} ===")

    print("\n=== Executing prompt ===")
    result = await session.execute("Write a simple hello world function in Python")

    print("\n=== Result ===")
    print(f"Type: {type(result)}")
    print(f"Length: {len(result)}")
    print(f"Content:\n{result}\n")

    await session.cleanup()
    print("\n=== Session cleaned up ===")


if __name__ == "__main__":
    asyncio.run(test_openai())
