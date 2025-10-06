"""
Logging hook module for Amplifier.
Provides visibility into agent execution via lifecycle events.
"""

import logging
from pathlib import Path
from typing import Any

from amplifier_core import HookResult
from amplifier_core import ModuleCoordinator

logger = logging.getLogger(__name__)


async def mount(coordinator: ModuleCoordinator, config: dict[str, Any] | None = None):
    """
    Mount the logging hook.

    Args:
        coordinator: Module coordinator
        config: Hook configuration

    Returns:
        Optional cleanup function
    """
    # Immediate console output to verify module is loading
    print("🔍 [LOGGING MODULE] Mounting hooks-logging module...")
    config = config or {}
    hook = LoggingHook(config)
    await hook.register(coordinator)
    logger.info("Mounted LoggingHook")
    print("✓ [LOGGING MODULE] Logging hooks registered successfully")
    return


class LoggingHook:
    """Hook handlers for logging lifecycle events."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize logging hook.

        Args:
            config: Hook configuration with logging settings
        """
        self.config = config
        self.setup_logging()

    def setup_logging(self):
        """Configure Python logging from config."""
        # Get logging configuration
        log_level = self.config.get("level", "INFO").upper()
        output = self.config.get("output", "console")
        log_file = self.config.get("file", "amplifier.log")

        print(f"🔍 [LOGGING MODULE] Configuring logging: level={log_level}, output={output}")

        # Set up root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Remove existing handlers to avoid duplicates
        root_logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        # Add console handler
        if output in ("console", "both"):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        # Add file handler
        if output in ("file", "both"):
            file_path = Path(log_file)
            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        logger.info(f"Logging configured: level={log_level}, output={output}")

    async def register(self, coordinator: ModuleCoordinator):
        """Register hook handlers with the coordinator."""
        hooks = coordinator.get("hooks")
        if not hooks:
            logger.warning("No hook registry found in coordinator")
            return

        # Register handlers for standard lifecycle events
        hooks.register("session:start", self.on_session_start, priority=0, name="logging:session_start")
        hooks.register("session:end", self.on_session_end, priority=0, name="logging:session_end")
        hooks.register("tool:pre", self.on_tool_pre, priority=0, name="logging:tool_pre")
        hooks.register("tool:post", self.on_tool_post, priority=0, name="logging:tool_post")
        hooks.register("agent:spawn", self.on_agent_spawn, priority=0, name="logging:agent_spawn")
        hooks.register("agent:complete", self.on_agent_complete, priority=0, name="logging:agent_complete")

        logger.debug("Registered all logging hook handlers")

    # Hook event handlers

    async def on_session_start(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log session start."""
        prompt = data.get("prompt", "")
        logger.info("=== Session Started ===")
        logger.debug(f"Initial prompt: {prompt[:100]}...")
        return HookResult(action="continue")

    async def on_session_end(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log session end."""
        response = data.get("response", "")
        logger.info("=== Session Ended ===")
        logger.debug(f"Final response: {response[:100]}...")
        return HookResult(action="continue")

    async def on_tool_pre(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log tool invocation before execution."""
        tool_name = data.get("tool", "unknown")
        arguments = data.get("arguments", {})

        logger.info(f"Tool invoked: {tool_name}")
        logger.debug(f"Tool arguments: {arguments}")

        return HookResult(action="continue")

    async def on_tool_post(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log tool results after execution."""
        tool_name = data.get("tool", "unknown")
        result = data.get("result", {})

        # Extract success/error info
        if isinstance(result, dict):
            success = result.get("success", True)
            if success:
                logger.info(f"Tool completed: {tool_name} ✓")
                logger.debug(f"Tool result: {result}")
            else:
                error = result.get("error", "Unknown error")
                logger.warning(f"Tool failed: {tool_name} - {error}")
        else:
            logger.info(f"Tool completed: {tool_name}")
            logger.debug(f"Tool result: {result}")

        return HookResult(action="continue")

    async def on_agent_spawn(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log sub-agent spawning."""
        agent_type = data.get("agent_type", "unknown")
        task = data.get("task", "")

        logger.info(f"Sub-agent spawning: {agent_type}")
        logger.debug(f"Sub-agent task: {task[:100]}...")

        return HookResult(action="continue")

    async def on_agent_complete(self, event: str, data: dict[str, Any]) -> HookResult:
        """Log sub-agent completion."""
        agent_type = data.get("agent_type", "unknown")

        logger.info(f"Sub-agent completed: {agent_type}")

        return HookResult(action="continue")
