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

    if mode == "chat":
        asyncio.run(interactive_chat(config_data, verbose))
    else:
        if not prompt:
            console.print("[red]Error:[/red] Prompt required in single mode")
            sys.exit(1)
        asyncio.run(execute_single(prompt, config_data, verbose))


async def interactive_chat(config: dict, verbose: bool):
    """Run an interactive chat session."""
    session = AmplifierSession()
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


async def execute_single(prompt: str, config: dict, verbose: bool):
    """Execute a single prompt and exit."""
    session = AmplifierSession()

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

        # Get modules of this type from coordinator
        modules = getattr(coordinator, f"{module_type}s", {})
        for mod_name, mod_instance in modules.items():
            # Extract info from module instance if available
            table.add_row(
                mod_name,
                module_type,
                mod_name,  # Mount point is typically the module name
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
        modules = getattr(coordinator, f"{module_type}s", {})
        if module_name in modules:
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
