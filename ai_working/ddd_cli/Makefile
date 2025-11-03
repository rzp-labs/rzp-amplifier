.PHONY: install check test format clean help

help:
	@echo "Available targets:"
	@echo "  install  - Install package and dependencies"
	@echo "  check    - Run linting and type checking"
	@echo "  test     - Run tests with coverage"
	@echo "  format   - Format code with ruff"
	@echo "  clean    - Remove build artifacts"

install:
	uv pip install -e ".[dev]"

check:
	@echo "Running ruff check..."
	ruff check amplifier_ddd/
	@echo "Running ruff format check..."
	ruff format --check amplifier_ddd/
	@echo "Running pyright..."
	pyright amplifier_ddd/

test:
	uv run pytest tests/ -v --cov=amplifier_ddd --cov-report=term-missing

format:
	ruff format amplifier_ddd/ tests/
	ruff check --fix amplifier_ddd/ tests/

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
