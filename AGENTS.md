# Agent Instructions

## Tox

- Run tox via uv: `uv run tox -e <env>`
- `tox` + `tox-uv` are declared as the project's default dev dependencies in `pyproject.toml`, so uv installs them automatically into `.venv`.

## Package Manager

Use **tox** for testing (not pytest directly):
- Test configuration is in `tox.ini`
- Common tests: `uv run tox -e tests`
- Run specific test file: `TESTPATH=tests/integrations/logging/test_logging.py uv run tox -e py3.14-common`
- Run single test: `TESTPATH=tests/path/to/test_file.py uv run tox -e py3.14-common -- -k "test_name"`

## Type Checking

Mypy and its type stubs live in the opt-in `typing` dependency group:
- Run `uv run tox -e mypy` before committing (must pass with zero errors)
- Strict mode enabled (`check_untyped_defs`, `disallow_untyped_defs`)

## Linting & Formatting

Use **ruff** for linting and formatting:
- `uv run ruff check --fix tests bitcaster_sdk`
- `uv run ruff format tests bitcaster_sdk`
- `uv run tox -e mypy`
