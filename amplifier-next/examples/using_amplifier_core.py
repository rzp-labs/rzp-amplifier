#!/usr/bin/env python3
"""
Example: Using Amplifier programmatically

This demonstrates how to use amplifier-core as a library
to build custom applications.
"""

import asyncio
from typing import Any

from amplifier_core import AmplifierSession


async def basic_example():
    """Basic usage with default configuration."""
    # Create session with minimal config using plain dict
    config: dict[str, Any] = {
        "session": {
            "orchestrator": "loop-basic",
            "context": "context-simple",
        },
        "context": {"config": {"max_tokens": 200_000, "compact_threshold": 0.92}},
        "providers": [{"name": "mock", "model": "mock-model"}],
        "tools": [],
        "agents": [],
        "hooks": [],
    }

    session = AmplifierSession(config)
    await session.initialize()

    # Execute a simple prompt
    result = await session.execute("Write a hello world function in Python")
    print("Result:", result)

    await session.cleanup()


async def custom_modules_example():
    """Using custom module configuration."""
    config: dict[str, Any] = {
        "session": {
            "orchestrator": "loop-streaming",  # Use streaming orchestrator
            "context": "context-simple",
        },
        "context": {
            "config": {
                "max_tokens": 150000,
                "auto_compact": True,
                "compact_threshold": 0.85,
            }
        },
        "providers": [
            {
                "name": "anthropic",
                "model": "claude-sonnet-4.5",
                "api_key": "your-api-key",  # Or use env var ANTHROPIC_API_KEY
            }
        ],
        "tools": ["filesystem", "bash", "web"],  # Specify tools
        "agents": ["architect", "debugger"],  # Available agents
        "hooks": [],
    }

    session = AmplifierSession(config)
    await session.initialize()

    # Use with context manager for automatic cleanup
    async with session:
        # Multiple interactions
        await session.execute("Design a REST API for a blog")
        await session.execute("Now implement the user authentication endpoint")
        await session.execute("Add rate limiting to the endpoints")

    print("Session completed and cleaned up")


async def programmatic_integration():
    """Integrating Amplifier into your application."""

    class MyApp:
        def __init__(self):
            self.amplifier: AmplifierSession | None = None

        async def setup(self):
            """Initialize Amplifier for the app."""
            # Could load from TOML file, but for this example we'll use a dict
            # In real app, you'd use: config = load_toml("app-config.toml")
            config: dict[str, Any] = {
                "session": {
                    "orchestrator": "loop-basic",
                    "context": "context-simple",
                },
                "context": {"config": {"max_tokens": 200_000, "compact_threshold": 0.92}},
                "providers": [],
                "tools": [],
                "agents": [],
                "hooks": [],
            }
            self.amplifier = AmplifierSession(config)
            await self.amplifier.initialize()  # pyright: ignore[reportOptionalMemberAccess]

        async def process_user_request(self, user_input: str) -> str:
            """Process user input through Amplifier."""
            if not self.amplifier:
                raise RuntimeError("Amplifier not initialized. Call setup() first.")

            try:
                # Add your business logic here
                enhanced_prompt = f"Help the user with: {user_input}"

                # Get AI response
                response = await self.amplifier.execute(enhanced_prompt)

                # Post-process if needed
                return self.format_response(response)

            except Exception as e:
                return f"Error processing request: {e}"

        def format_response(self, response: str) -> str:
            """Format the AI response for your application."""
            # Your formatting logic
            return response.strip()

        async def shutdown(self):
            """Clean up resources."""
            if self.amplifier:
                await self.amplifier.cleanup()

    # Use the app
    app = MyApp()
    await app.setup()

    # Simulate user requests
    result = await app.process_user_request("Create a Python class for managing todos")
    print("App response:", result)

    await app.shutdown()


async def hook_example():
    """Using hooks to extend behavior."""
    # Note: HookRegistry and LifecycleEvent would need to be implemented
    # This is a placeholder example showing the concept

    # Define a custom hook
    async def log_tool_usage(data):
        """Log whenever a tool is used."""
        print(f"Tool used: {data.get('tool')} with input: {data.get('input')}")
        return {"action": "continue"}

    # Config with hooks defined
    config: dict[str, Any] = {
        "session": {
            "orchestrator": "loop-basic",
            "context": "context-simple",
        },
        "context": {"config": {"max_tokens": 200_000, "compact_threshold": 0.92}},
        "providers": [],
        "tools": [],
        "agents": [],
        "hooks": [{"event": "pre_tool_use", "handler": log_tool_usage}],
    }

    session = AmplifierSession(config)
    await session.initialize()

    await session.execute("Read the README.md file")

    await session.cleanup()


async def parallel_agents_example():
    """Using multiple specialized agents in parallel."""

    config: dict[str, Any] = {
        "session": {
            "orchestrator": "loop-basic",
            "context": "context-simple",
        },
        "context": {"config": {"max_tokens": 200_000, "compact_threshold": 0.92}},
        "providers": [{"name": "anthropic", "model": "claude-sonnet-4.5"}],
        "tools": [],
        "agents": ["architect", "reviewer", "tester"],
        "hooks": [],
    }

    session = AmplifierSession(config)
    await session.initialize()

    # Get the agent manager
    agent_manager = session.get_agent_manager()

    # Define tasks for different agents
    tasks = [
        {"agent": "architect", "task": "Design a microservices architecture for an e-commerce platform"},
        {"agent": "reviewer", "task": "Review the architecture for scalability and security"},
        {"agent": "tester", "task": "Create test strategies for the architecture"},
    ]

    # Execute in parallel
    results = await agent_manager.execute_parallel(tasks)

    for task, result in zip(tasks, results, strict=False):
        print(f"\n{task['agent']} result:")
        print(result.summary)

    await session.cleanup()


if __name__ == "__main__":
    print("Amplifier Core Examples\n" + "=" * 50)

    print("\n1. Basic Example:")
    asyncio.run(basic_example())

    print("\n2. Custom Modules Example:")
    # asyncio.run(custom_modules_example())

    print("\n3. App Integration Example:")
    # asyncio.run(programmatic_integration())

    print("\n4. Hook Example:")
    # asyncio.run(hook_example())

    print("\n5. Parallel Agents Example:")
    # asyncio.run(parallel_agents_example())

    print("\nUncomment examples to run them!")
