"""Configuration management for DDD CLI utilities."""

from typing import Any

DEFAULT_EXCLUSIONS = [
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "*.egg-info",
]

DEFAULT_EXTENSIONS = [".md", ".yaml", ".toml", ".json"]

DEFAULT_CHECKLIST_PATH = "ai_working/ddd/docs_checklist.txt"
DEFAULT_INDEX_PATH = "ai_working/ddd/docs_index.txt"
DEFAULT_REPORT_PATH = "ai_working/ddd/docs_status.md"


def get_default_config() -> dict[str, Any]:
    """Get default configuration."""
    return {
        "exclusions": DEFAULT_EXCLUSIONS,
        "extensions": DEFAULT_EXTENSIONS,
        "checklist_path": DEFAULT_CHECKLIST_PATH,
        "index_path": DEFAULT_INDEX_PATH,
        "report_path": DEFAULT_REPORT_PATH,
    }
