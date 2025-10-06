"""Amplifier CLI - Command-line interface for the Amplifier platform."""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import click
import toml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from amplifier_core import AmplifierSession, ModuleCoordinator

console = Console()


class CommandProcessor:
    """Process slash commands and special directives."""

    COMMANDS = {
        "/think": {"action": "enable_plan_mode", "description": "Enable read-only planning mode"},
        "/do": {
            "action": "disable_plan_mode",
            "description": "Exit plan mode and allow modifications",
        },
        "/stop": {"action": "halt_execution", "description": "Stop current execution"},
        "/save": {"action": "save_transcript", "description": "Save conversation transcript"},
        "/status": {"action": "show_status", "description": "Show session status"},
        "/clear": {"action": "clear_context", "description": "Clear conversation context"},
        "/help": {"action": "show_help", "description": "Show available commands"},
        "/config": {"action": "show_config", "description": "Show current configuration"},
        "/tools": {"action": "list_tools", "description": "List available tools"},
    }

    def __init__(self, session: AmplifierSession):
        self.session = session
        self.plan_mode = False
        self.halted = False
        self.plan_mode_unregister = None  # Store unregister function

    def process_input(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process user input and extract commands.

        Returns:
            (action, data) tuple
        """
        # Check for commands
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command in self.COMMANDS:
                cmd_info = self.COMMANDS[command]
                return cmd_info["action"], {"args": args, "command": command}
            else:
                return "unknown_command", {"command": command}

        # Regular prompt
        return "prompt", {"text": user_input, "plan_mode": self.plan_mode}

    async def handle_command(self, action: str, data: Dict[str, Any]) -> str:
        """Handle a command action."""

        if action == "enable_plan_mode":
            self.plan_mode = True
            self._configure_plan_mode(True)
            return "✓ Plan Mode enabled - all modifications disabled"

        elif action == "disable_plan_mode":
            self.plan_mode = False
            self._configure_plan_mode(False)
            return "✓ Plan Mode disabled - modifications enabled"

        elif action == "halt_execution":
            self.halted = True
            # Signal orchestrator to stop
            if hasattr(self.session, "halt"):
                await self.session.halt()
            return "✓ Execution halted"

        elif action == "save_transcript":
            path = await self._save_transcript(data.get("args", ""))
            return f"✓ Transcript saved to {path}"

        elif action == "show_status":
            status = await self._get_status()
            return status

        elif action == "clear_context":
            await self._clear_context()
            return "✓ Context cleared"

        elif action == "show_help":
            return self._format_help()

        elif action == "show_config":
            return await self._get_config_display()

        elif action == "list_tools":
            return await self._list_tools()

        elif action == "unknown_command":
            return f"Unknown command: {data['command']}. Use /help for available commands."

        else:
            return f"Unhandled action: {action}"

    def _configure_plan_mode(self, enabled: bool):
        """Configure session for plan mode."""
        # Import HookResult here to avoid circular import
        from amplifier_core.models import HookResult

        # Access hooks via the coordinator
        hooks = self.session.coordinator.get("hooks")
        if hooks:
            if enabled:
                # Register plan mode hook that denies write operations
                async def plan_mode_hook(event: str, data: Dict[str, Any]) -> HookResult:
                    tool_name = data.get("tool")
                    if tool_name in ["write", "edit", "bash", "task"]:
                        return HookResult(
                            action="deny",
                            reason="Write operations disabled in Plan Mode",
                        )
                    return HookResult(action="continue")

                # Register the hook with the hooks registry and store unregister function
                if hasattr(hooks, "register"):
                    self.plan_mode_unregister = hooks.register(
                        "tool:pre", plan_mode_hook, priority=0, name="plan_mode"
                    )
            else:
                # Unregister plan mode hook if we have the unregister function
                if self.plan_mode_unregister:
                    self.plan_mode_unregister()
                    self.plan_mode_unregister = None

    async def _save_transcript(self, filename: str) -> str:
        """Save current transcript."""
        # Default filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcript_{timestamp}.json"

        # Get messages from context
        context = self.session.coordinator.get("context")
        if context and hasattr(context, "get_messages"):
            messages = await context.get_messages()

            # Save to file
            path = Path(".amplifier/transcripts") / filename
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "w") as f:
                json.dump(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "messages": messages,
                        "config": self.session.config,
                    },
                    f,
                    indent=2,
                )

            return str(path)

        return "No transcript available"

    async def _get_status(self) -> str:
        """Get session status information."""
        lines = ["Session Status:"]

        # Plan mode status
        lines.append(f"  Plan Mode: {'ON' if self.plan_mode else 'OFF'}")

        # Context size
        context = self.session.coordinator.get("context")
        if context and hasattr(context, "get_messages"):
            messages = await context.get_messages()
            lines.append(f"  Messages: {len(messages)}")

        # Active providers
        providers = self.session.coordinator.get("providers")
        if providers:
            provider_names = list(providers.keys())
            lines.append(f"  Providers: {', '.join(provider_names)}")

        # Available tools
        tools = self.session.coordinator.get("tools")
        if tools:
            lines.append(f"  Tools: {len(tools)}")

        return "\n".join(lines)

    async def _clear_context(self):
        """Clear the conversation context."""
        context = self.session.coordinator.get("context")
        if context and hasattr(context, "clear"):
            await context.clear()

    def _format_help(self) -> str:
        """Format help text."""
        lines = ["Available Commands:"]
        for cmd, info in self.COMMANDS.items():
            lines.append(f"  {cmd:<12} - {info['description']}")
        return "\n".join(lines)

    async def _get_config_display(self) -> str:
        """Display current configuration."""
        config_str = json.dumps(self.session.config, indent=2)
        return f"Current Configuration:\n{config_str}"

    async def _list_tools(self) -> str:
        """List available tools."""
        tools = self.session.coordinator.get("tools")
        if not tools:
            return "No tools available"

        lines = ["Available Tools:"]
        for name, tool in tools.items():
            desc = getattr(tool, "description", "No description")
            lines.append(f"  {name:<20} - {desc}")

        return "\n".join(lines)


@click.group()
@click.version_option()
def cli():
    """Amplifier - AI-powered modular development platform."""
    pass


@cli.command()
@click.argument("prompt", required=False)
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.option("--provider", "-p", default=None, help="LLM provider to use")
@click.option("--model", "-m", help="Model to use (provider-specific)")
@click.option(
    "--mode", type=click.Choice(["chat", "single"]), default="single", help="Execution mode"
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def run(
    prompt: Optional[str],
    config: Optional[str],
    provider: str,
    model: Optional[str],
    mode: str,
    verbose: bool,
):
    """Execute a prompt or start an interactive session."""

    # Load configuration
    config_data = {}
    if config:
        config_path = Path(config)
        if config_path.suffix == ".toml":
            config_data = toml.load(config_path)
        elif config_path.suffix == ".json":
            with open(config_path) as f:
                config_data = json.load(f)

    # Override with CLI options
    if provider:
        config_data.setdefault("provider", {})["name"] = provider
    if model:
        config_data.setdefault("provider", {})["model"] = model

    if mode == "chat":
        asyncio.run(interactive_chat(config_data, verbose))
    else:
        if not prompt:
            console.print("[red]Error:[/red] Prompt required in single mode")
            sys.exit(1)
        asyncio.run(execute_single(prompt, config_data, verbose))


def transform_toml_to_session_config(toml_config: dict[str, Any]) -> dict[str, Any]:
    """
    Transform TOML config format to AmplifierSession expected format.

    TOML format:
        [provider]
        name = "anthropic"
        model = "claude-sonnet-4-5"

        [modules]
        orchestrator = "loop-basic"
        context = "context-simple"
        tools = ["filesystem", "bash"]

    AmplifierSession format:
        {
            "session": {
                "orchestrator": "loop-basic",
                "context": "context-simple"
            },
            "providers": [
                {
                    "module": "provider-anthropic",
                    "config": {"model": "claude-sonnet-4-5"}
                }
            ],
            "tools": [
                {"module": "tool-filesystem"},
                {"module": "tool-bash"}
            ]
        }
    """
    # Start with default structure
    session_config = {
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

    # Transform orchestrator and context from modules section
    if "modules" in toml_config:
        if "orchestrator" in toml_config["modules"]:
            session_config["session"]["orchestrator"] = toml_config["modules"]["orchestrator"]
        if "context" in toml_config["modules"]:
            session_config["session"]["context"] = toml_config["modules"]["context"]

        # Transform tools list
        if "tools" in toml_config["modules"]:
            tools = toml_config["modules"]["tools"]
            if isinstance(tools, list):
                session_config["tools"] = [{"module": f"tool-{tool}"} for tool in tools]

        # Transform hooks from modules section
        if "hooks" in toml_config["modules"]:
            hooks = toml_config["modules"]["hooks"]
            if isinstance(hooks, list):
                session_config["hooks"] = hooks

    # Transform provider configuration
    if "provider" in toml_config:
        provider = toml_config["provider"]
        provider_name = provider.get("name", "mock")

        # Build provider config
        provider_config: dict[str, Any] = {"module": f"provider-{provider_name}"}

        # Add provider-specific config
        config_dict: dict[str, Any] = {}
        if "model" in provider:
            config_dict["model"] = provider["model"]

        # Add any other provider settings
        extra_config = {k: v for k, v in provider.items() if k not in ["name", "model"]}
        if extra_config:
            config_dict.update(extra_config)

        if config_dict:
            provider_config["config"] = config_dict

        session_config["providers"] = [provider_config]

    # Transform hooks from top level (preferred location)
    if "hooks" in toml_config:
        hooks = toml_config["hooks"]
        if isinstance(hooks, list):
            session_config["hooks"] = hooks

    # Copy session settings if present
    if "session" in toml_config:
        # Context config specifically
        if "max_tokens" in toml_config["session"]:
            session_config["context"]["config"]["max_tokens"] = toml_config["session"]["max_tokens"]
        if "compact_threshold" in toml_config["session"]:
            session_config["context"]["config"]["compact_threshold"] = toml_config["session"][
                "compact_threshold"
            ]
        if "auto_compact" in toml_config["session"]:
            session_config["context"]["config"]["auto_compact"] = toml_config["session"][
                "auto_compact"
            ]

    # Transform agents if present
    if "agents" in toml_config:
        agents = toml_config["agents"]
        if isinstance(agents, list):
            session_config["agents"] = [{"module": f"agent-{agent}"} for agent in agents]

    # Transform hooks if present
    if "hooks" in toml_config:
        hooks = toml_config["hooks"]
        # Handle direct array format: hooks = [{module = "hooks-logging", config = {...}}]
        if isinstance(hooks, list):
            session_config["hooks"] = hooks
        # Handle nested format: hooks = {enabled = ["backup", "logging"]}
        elif "enabled" in hooks and isinstance(hooks["enabled"], list):
            session_config["hooks"] = [{"module": f"hooks-{hook}"} for hook in hooks["enabled"]]

    return session_config


async def interactive_chat(config: dict, verbose: bool):
    """Run an interactive chat session."""
    transformed_config = transform_toml_to_session_config(config)
    session = AmplifierSession(transformed_config)
    await session.initialize()

    # Create command processor
    command_processor = CommandProcessor(session)

    console.print(
        Panel.fit(
            "[bold cyan]Amplifier Interactive Session[/bold cyan]\n"
            "Type '/help' for commands, 'exit' or press Ctrl+C to quit",
            border_style="cyan",
        )
    )

    try:
        while True:
            try:
                prompt = console.input("\n[bold green]>[/bold green] ")
                if prompt.lower() in ["exit", "quit"]:
                    break

                if prompt.strip():
                    # Process input for commands
                    action, data = command_processor.process_input(prompt)

                    if action == "prompt":
                        # Normal prompt execution
                        console.print("[dim]Processing...[/dim]")
                        response = await session.execute(data["text"])
                        console.print("\n" + response)
                    else:
                        # Handle command
                        result = await command_processor.handle_command(action, data)
                        console.print(f"[cyan]{result}[/cyan]")

            except KeyboardInterrupt:
                # Allow /stop command or Ctrl+C to interrupt execution
                if command_processor.halted:
                    command_processor.halted = False
                    console.print("\n[yellow]Execution stopped[/yellow]")
                else:
                    break
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
                if verbose:
                    console.print_exception()
    finally:
        await session.cleanup()
        console.print("\n[yellow]Session ended[/yellow]")


async def execute_single(prompt: str, config: dict, verbose: bool):
    """Execute a single prompt and exit."""
    transformed_config = transform_toml_to_session_config(config)
    session = AmplifierSession(transformed_config)

    try:
        await session.initialize()

        if verbose:
            console.print(f"[dim]Executing: {prompt}[/dim]")

        response = await session.execute(prompt)
        if verbose:
            console.print(
                f"[dim]Response type: {type(response)}, length: {len(response) if response else 0}[/dim]"
            )
        console.print(response)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            console.print_exception()
        sys.exit(1)
    finally:
        await session.cleanup()


@cli.group()
def module():
    """Manage Amplifier modules."""
    pass


@module.command("list")
@click.option(
    "--type",
    "-t",
    type=click.Choice(["all", "orchestrator", "provider", "tool", "agent", "context", "hook"]),
    default="all",
    help="Module type to list",
)
def list_modules(type: str):
    """List installed modules."""
    coordinator = ModuleCoordinator()

    # Get loaded modules from coordinator
    table = Table(title="Installed Modules", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Mount Point")
    table.add_column("Description")

    # Module types we support
    module_types = ["orchestrator", "provider", "tool", "agent", "context", "hook"]

    for module_type in module_types:
        if type != "all" and type != module_type:
            continue

        # Get modules of this type from coordinator using mount_point names
        mount_point = module_type if module_type == "context" else f"{module_type}s"
        modules = coordinator.get(mount_point) if hasattr(coordinator, "get") else {}

        # Handle single vs multi module mount points
        if module_type in ["orchestrator", "context"]:
            # Single module mount points
            if modules:
                table.add_row(
                    module_type,
                    module_type,
                    module_type,
                    getattr(modules, "description", "N/A") if modules else "N/A",
                )
        elif isinstance(modules, dict):
            # Multi-module mount points
            for mod_name, mod_instance in modules.items():
                table.add_row(
                    mod_name,
                    module_type,
                    mod_name,
                    getattr(mod_instance, "description", "N/A") if mod_instance else "N/A",
                )

    console.print(table)


@module.command("info")
@click.argument("module_name")
def module_info(module_name: str):
    """Show detailed information about a module."""
    coordinator = ModuleCoordinator()

    # Module types to search
    module_types = ["orchestrator", "provider", "tool", "agent", "context", "hook"]

    # Find module
    module = None
    module_type_found = None
    for module_type in module_types:
        mount_point = module_type if module_type == "context" else f"{module_type}s"
        modules = coordinator.get(mount_point) if hasattr(coordinator, "get") else {}

        if module_type in ["orchestrator", "context"]:
            # Single module mount points - check if this is the one
            if modules and module_name == module_type:
                module = modules
                module_type_found = module_type
                break
        elif isinstance(modules, dict) and module_name in modules:
            module = modules[module_name]
            module_type_found = module_type
            break

    if not module:
        console.print(f"[red]Module '{module_name}' not found[/red]")
        sys.exit(1)

    # Display module info
    panel_content = f"""[bold]Name:[/bold] {module_name}
[bold]Type:[/bold] {module_type_found}
[bold]Description:[/bold] {getattr(module, "description", "N/A") if module else "N/A"}
[bold]Mount Point:[/bold] {module_name}"""

    console.print(Panel(panel_content, title=f"Module: {module_name}", border_style="cyan"))


@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output path for configuration")
def init(output: Optional[str]):
    """Initialize a new Amplifier configuration."""
    config_template = {
        "provider": {"name": "mock", "model": "mock-model"},
        "modules": {"orchestrator": "loop-basic", "context": "context-simple"},
        "hooks": {"enabled": ["backup"]},
        "session": {"max_tokens": 100000, "auto_compact": True, "compact_threshold": 0.9},
    }

    output_path = Path(output if output else "amplifier.toml")

    with open(output_path, "w") as f:
        toml.dump(config_template, f)

    console.print(f"[green]✓[/green] Configuration created at {output_path}")

    # Show the created config
    with open(output_path) as f:
        syntax = Syntax(f.read(), "toml", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Configuration", border_style="green"))


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
