"""Tests for main CLI entry point."""

from click.testing import CliRunner

from amplifier_ddd.cli import ddd_cli


def test_ddd_cli_group_help() -> None:
    """Test main CLI group help text."""
    runner = CliRunner()
    result = runner.invoke(ddd_cli, ["--help"])

    assert result.exit_code == 0
    assert "Document-Driven Development utilities" in result.output
    assert "list-docs" in result.output
    assert "progress" in result.output
    assert "verify-retcon" in result.output
    assert "generate-report" in result.output
    assert "detect-conflicts" in result.output


def test_ddd_cli_version() -> None:
    """Test CLI version information."""
    runner = CliRunner()
    result = runner.invoke(ddd_cli, ["--version"])

    assert result.exit_code == 0
    # Version output should contain program name
    assert "ddd" in result.output.lower() or "version" in result.output.lower()


def test_list_docs_command_available() -> None:
    """Test list-docs command is registered."""
    runner = CliRunner()
    result = runner.invoke(ddd_cli, ["list-docs", "--help"])

    assert result.exit_code == 0
    assert "Generate checklist" in result.output or "documentation files" in result.output


def test_progress_command_available() -> None:
    """Test progress command group is registered."""
    runner = CliRunner()
    result = runner.invoke(ddd_cli, ["progress", "--help"])

    assert result.exit_code == 0
    assert "show" in result.output
    assert "mark-complete" in result.output


def test_verify_retcon_command_available() -> None:
    """Test verify-retcon command is registered."""
    runner = CliRunner()
    result = runner.invoke(ddd_cli, ["verify-retcon", "--help"])

    assert result.exit_code == 0
    assert "Verify retcon" in result.output or "rules compliance" in result.output


def test_generate_report_command_available() -> None:
    """Test generate-report command is registered."""
    runner = CliRunner()
    result = runner.invoke(ddd_cli, ["generate-report", "--help"])

    assert result.exit_code == 0
    assert "status report" in result.output.lower() or "progress" in result.output.lower()


def test_detect_conflicts_command_available() -> None:
    """Test detect-conflicts command is registered."""
    runner = CliRunner()
    result = runner.invoke(ddd_cli, ["detect-conflicts", "--help"])

    assert result.exit_code == 0
    assert "inconsistencies" in result.output.lower() or "terminology" in result.output.lower()


def test_cli_invalid_command() -> None:
    """Test CLI with invalid command shows error."""
    runner = CliRunner()
    result = runner.invoke(ddd_cli, ["invalid-command"])

    assert result.exit_code != 0
    assert "Error" in result.output or "no such command" in result.output.lower()


def test_cli_no_command_shows_help() -> None:
    """Test CLI with no command shows help."""
    runner = CliRunner()
    result = runner.invoke(ddd_cli, [])

    # Click exits with 2 when no command given to a command group
    assert result.exit_code in (0, 2)
    # But should still show usage/help info
    assert "Usage" in result.output or "Commands" in result.output


def test_all_commands_registered() -> None:
    """Test all expected commands are registered."""
    runner = CliRunner()
    result = runner.invoke(ddd_cli, ["--help"])

    assert result.exit_code == 0

    # All 5 commands should be present
    expected_commands = ["list-docs", "progress", "verify-retcon", "generate-report", "detect-conflicts"]
    for cmd in expected_commands:
        assert cmd in result.output, f"Command {cmd} not found in CLI help"


def test_progress_subcommands() -> None:
    """Test progress group has both subcommands."""
    runner = CliRunner()
    result = runner.invoke(ddd_cli, ["progress", "--help"])

    assert result.exit_code == 0
    assert "show" in result.output
    assert "mark-complete" in result.output


def test_cli_command_execution_paths() -> None:
    """Test that commands can be invoked (even if they fail without args)."""
    runner = CliRunner()

    # These should all be invocable (even if they exit with error due to missing args)
    commands_to_test = [
        ["list-docs"],
        ["progress", "show"],
        ["progress", "mark-complete"],
        ["verify-retcon"],
        ["generate-report"],
        ["detect-conflicts"],
    ]

    for cmd in commands_to_test:
        result = runner.invoke(ddd_cli, cmd)
        # Command should be recognized (not exit with "no such command" error)
        assert "no such command" not in result.output.lower()
