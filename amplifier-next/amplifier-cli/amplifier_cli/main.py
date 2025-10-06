"""Amplifier CLI - Command-line interface for the Amplifier platform."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click
import toml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from amplifier_core import AmplifierSession, ModuleCoordinator
from amplifier_core.interfaces import ModuleType
from amplifier_core.models import SessionConfig

console = Console()


@click.group()
@click.version_option()
def cli():
    """Amplifier - AI-powered modular development platform."""
    pass


@cli.command()
@click.argument("prompt", required=False)
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.option("--provider", "-p", default="mock", help="LLM provider to use")
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

    # Create session config
    session_config = SessionConfig(**config_data)

    if mode == "chat":
        asyncio.run(interactive_chat(session_config, verbose))
    else:
        if not prompt:
            console.print("[red]Error:[/red] Prompt required in single mode")
            sys.exit(1)
        asyncio.run(execute_single(prompt, session_config, verbose))


async def interactive_chat(config: SessionConfig, verbose: bool):
    """Run an interactive chat session."""
    session = AmplifierSession(config)
    await session.initialize()

    console.print(
        Panel.fit(
            "[bold cyan]Amplifier Interactive Session[/bold cyan]\n"
            "Type 'exit' or press Ctrl+C to quit",
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
                    console.print("[dim]Processing...[/dim]")
                    response = await session.execute(prompt)
                    console.print("\n" + response)

            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
                if verbose:
                    console.print_exception()
    finally:
        await session.cleanup()
        console.print("\n[yellow]Session ended[/yellow]")


async def execute_single(prompt: str, config: SessionConfig, verbose: bool):
    """Execute a single prompt and exit."""
    session = AmplifierSession(config)

    try:
        await session.initialize()

        if verbose:
            console.print(f"[dim]Executing: {prompt}[/dim]")

        response = await session.execute(prompt)
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
    type=click.Choice(["all", "orchestrator", "provider", "tool", "agent", "context", "hooks"]),
    default="all",
    help="Module type to list",
)
def list_modules(type: str):
    """List installed modules."""
    coordinator = ModuleCoordinator()

    # Discover modules
    asyncio.run(coordinator.discover_modules())

    table = Table(title="Installed Modules", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Version")
    table.add_column("Description")

    for module_type in ModuleType:
        if type != "all" and type != module_type.value:
            continue

        modules = coordinator.get_modules(module_type)
        for mod_name, mod_info in modules.items():
            table.add_row(
                mod_name,
                module_type.value,
                mod_info.get("version", "unknown"),
                mod_info.get("description", ""),
            )

    console.print(table)


@module.command("info")
@click.argument("module_name")
def module_info(module_name: str):
    """Show detailed information about a module."""
    coordinator = ModuleCoordinator()
    asyncio.run(coordinator.discover_modules())

    # Find module
    module = None
    for module_type in ModuleType:
        modules = coordinator.get_modules(module_type)
        if module_name in modules:
            module = modules[module_name]
            break

    if not module:
        console.print(f"[red]Module '{module_name}' not found[/red]")
        sys.exit(1)

    # Display module info
    panel_content = f"""[bold]Name:[/bold] {module_name}
[bold]Type:[/bold] {module.get("type", "unknown")}
[bold]Version:[/bold] {module.get("version", "unknown")}
[bold]Description:[/bold] {module.get("description", "N/A")}
[bold]Author:[/bold] {module.get("author", "unknown")}
[bold]Path:[/bold] {module.get("path", "N/A")}"""

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
