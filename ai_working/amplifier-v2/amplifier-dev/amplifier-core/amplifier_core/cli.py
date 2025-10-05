#!/usr/bin/env python3
"""
Command-line interface for Amplifier.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from amplifier_core import AmplifierSession


def setup_logging(debug: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")


async def execute_prompt(prompt: str, config_path: Path | None = None, debug: bool = False):
    """Execute a single prompt."""
    setup_logging(debug)

    config = None
    if config_path and config_path.exists():
        import tomli

        from amplifier_core.utils.config import interpolate_env_vars

        with open(config_path, "rb") as f:
            config = tomli.load(f)
            # Apply environment variable interpolation
            config = interpolate_env_vars(config)

    async with AmplifierSession(config) as session:
        result = await session.execute(prompt)
        print(result)


async def interactive_mode(config_path: Path | None = None):
    """Run in interactive chat mode."""
    setup_logging(False)

    config = None
    if config_path and config_path.exists():
        import tomli

        from amplifier_core.utils.config import interpolate_env_vars

        with open(config_path, "rb") as f:
            config = tomli.load(f)
            # Apply environment variable interpolation
            config = interpolate_env_vars(config)

    print("Amplifier Interactive Mode")
    print("Type 'exit' or 'quit' to end the session")
    print("-" * 40)

    async with AmplifierSession(config) as session:
        while True:
            try:
                prompt = input("\n> ").strip()

                if prompt.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break

                if not prompt:
                    continue

                result = await session.execute(prompt)
                print(result)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Amplifier - Modular AI Agent System")

    # Mode selection
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute a prompt")
    execute_parser.add_argument("prompt", help="Prompt to execute")
    execute_parser.add_argument("--config", type=Path, help="Config file path")
    execute_parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Interactive chat mode")
    chat_parser.add_argument("--config", type=Path, help="Config file path")

    # Module commands
    module_parser = subparsers.add_parser("modules", help="Module management")
    module_subparsers = module_parser.add_subparsers(dest="module_command")

    list_parser = module_subparsers.add_parser("list", help="List available modules")
    install_parser = module_subparsers.add_parser("install", help="Install a module")
    install_parser.add_argument("module", help="Module to install")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("project", help="Project name")

    # Parse arguments
    args = parser.parse_args()

    # Default to execute if prompt provided without command
    if not args.command and len(sys.argv) > 1:
        # Assume first arg is prompt
        asyncio.run(execute_prompt(" ".join(sys.argv[1:]), config_path=None, debug=False))
        return

    # Handle commands
    if args.command == "execute":
        asyncio.run(execute_prompt(args.prompt, config_path=args.config, debug=args.debug))
    elif args.command == "chat":
        asyncio.run(interactive_mode(args.config))
    elif args.command == "modules":
        if args.module_command == "list":
            print("Available modules:")
            print("  - loop-basic (orchestrator)")
            print("  - provider-anthropic")
            print("  - provider-openai")
            print("  - tool-filesystem")
            print("  - tool-bash")
            print("  - context-simple")
            print("  - hooks-formatter")
        elif args.module_command == "install":
            print(f"Installing module: {args.module}")
            print("(Not implemented yet)")
    elif args.command == "init":
        project_dir = Path(args.project)
        project_dir.mkdir(exist_ok=True)
        config_dir = project_dir / ".amplifier"
        config_dir.mkdir(exist_ok=True)

        # Create default config
        config_file = config_dir / "config.toml"
        config_file.write_text("""# Amplifier project configuration

[session]
orchestrator = "loop-basic"
context = "context-simple"

[context.config]
max_tokens = 200_000
compact_threshold = 0.92

# Add providers, tools, etc. as needed
""")
        print(f"Initialized Amplifier project in {project_dir}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
