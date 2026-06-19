# Development Guide

This guide covers development setup and contribution guidelines for the `bygge` project itself.

## Prerequisites

- Python 3.14+
- Git

## Setup

### 1. Clone and install

```bash
# Clone the repository
git clone https://github.com/rcook/bygge.git
cd bygge

# Create virtual environment
python3.14 -m venv .venv --upgrade-deps

# Install in editable mode with dev dependencies (Linux)
.venv/bin/pip install -e ".[dev]"

# Install in editable mode with dev dependencies (Windows)
.venv/Scripts/pip install -e ".[dev]"
```

Or in one command:

```bash
python3.14 -m venv .venv --upgrade-deps && .venv/bin/pip install -e ".[dev]"
```

### 2. Install Git hooks

```bash
bygge hooks
```

This configures git to run `bygge check` before each commit.

## Development Workflow

### Running checks

```bash
# Individual checks
bygge fmt               # Format code and sort imports
bygge lint              # Lint code (auto-fix enabled)
bygge typecheck         # Type-check with basedpyright
bygge test              # Run tests
bygge coverage          # Run tests with coverage report

# All checks (what pre-commit runs)
bygge check

# Verification mode (no changes, for CI)
bygge fmt --check
bygge lint --check
```

### Running tests

```bash
# Via bygge CLI (recommended)
bygge test              # Simple test run
bygge coverage          # With coverage report

# Directly with pytest
pytest                # Simple
pytest -v             # Verbose
pytest tests/test_main.py  # Single file
pytest --cov=bygge --cov-report=term-missing --cov-fail-under=100  # Full coverage
```

### Manual tool invocation

You can also run tools directly:

```bash
ruff format src/ tests/       # Format
ruff check src/ tests/        # Lint
basedpyright                  # Type-check
pytest                        # Test
```

## Project Structure

```
bygge/
├── src/bygge/            # Main package source
│   ├── cmd/              # CLI command implementations
│   ├── contracts/        # Protocol definitions for plugins
│   ├── package_info/     # Package discovery and metadata
│   ├── plugins/          # Tool plugins (pytest, basedpyright, etc.)
│   └── util/             # Utility functions
├── tests/                # Test suite
├── pyproject.toml        # Project metadata and tool configuration
├── .bygge.toml             # bygge workspace configuration
└── hooks/                # Git hooks
```

## Release Process

This project uses `bump-my-version` for versioning.

### Version bump

```bash
# Patch release (0.1.0 -> 0.1.1)
bump-my-version bump patch

# Minor release (0.1.0 -> 0.2.0)
bump-my-version bump minor

# Major release (0.1.0 -> 1.0.0)
bump-my-version bump major
```

Each command:
- Updates `version` in `pyproject.toml`
- Updates `VERSION` in `src/bygge/__init__.py`
- Creates a git commit: "Bump version: X.Y.Z -> X.Y.Z+1"
- Creates a git tag: `vX.Y.Z+1`

### Publish to PyPI

After bumping the version:

```bash
git push --follow-tags
```

This triggers the GitHub Actions publish workflow which:
1. Runs all checks (format, lint, typecheck, test)
2. Builds the package
3. Publishes to PyPI via trusted publisher

### Preview changes

```bash
bump-my-version bump patch --dry-run --verbose
```

## Code Style

### General guidelines

- **Type hints** — All functions must have complete type annotations
- **Docstrings** — Public APIs should have docstrings; internal code only when non-obvious
- **Imports** — Organized by ruff's isort rules
- **Line length** — 100 characters max
- **Testing** — 100% coverage required; all tests must pass

### Testing patterns

- Use `tmp_path` fixture for filesystem tests
- Use `mock_subprocess` fixture for subprocess tests
- Use `tmp_workspace` fixture for workspace-aware tests
- Prefer functional tests over mocking internal implementation details

### Type checking

The project uses basedpyright in `strict` mode. Key settings:

- `reportAny = "error"` — No implicit `Any` types
- `reportExplicitAny = "error"` — No explicit `Any` (except in specific cases)
- `reportUnusedParameter = "error"` — All parameters must be used

## Configuration

### Tool configuration locations

All tool configuration is in `pyproject.toml`:

- **Ruff** — `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.format]`
- **Basedpyright** — `[tool.basedpyright]`
- **Pytest** — `[tool.pytest.ini_options]`
- **Vulture** — `[tool.vulture]`
- **Bump-my-version** — `[tool.bumpversion]`

### Workspace configuration

The `.bygge.toml` file configures bygge itself:

```toml
[workspace]
venv_dir = ".venv"
optional_deps = ["dev"]
coverage_baseline = 100
```

Note: No `package_root_dir` because this is a single-package project (the tool supports both single-package and monorepo layouts).

## Common Tasks

### Adding a new command

1. Create a new module in `src/bygge/cmd/`
2. Implement the command function
3. Export it from `src/bygge/cmd/__init__.py`
4. Add the command to `src/bygge/main.py`
5. Write tests in `tests/test_*.py`

### Adding a new tool plugin

1. Create a new module in `src/bygge/plugins/`
2. Implement the required protocols from `src/bygge/contracts/`
3. Register it in `src/bygge/cmd/constants.py` (`PLUGINS`)
4. Write tests in `tests/test_plugins.py`

### Debugging

```bash
# Run bygge with debug logging
bygge --level debug test

# Run with Python debugger
python -m pdb .venv/bin/bygge test

# Get environment info
bygge info
```

## Troubleshooting

### Tests fail with import errors

```bash
# Reinstall in editable mode
pip install -e ".[dev]"
```

### Pre-commit hook blocks commit

```bash
# Fix issues
bygge check

# Or bypass hook (use sparingly)
bygge commit-unchecked -m "Your message"
```

### Type checker complains about missing types

The project requires strict typing. Options:
1. Add proper type hints
2. Use `# type: ignore[specific-error]` with a comment explaining why
3. Check if the issue is in dependencies (may need `reportPrivateImportUsage = false` for specific modules)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and run `bygge check`
4. Commit with descriptive messages
5. Push and create a pull request

### Pull request checklist

- [ ] All checks pass (`bygge check`)
- [ ] Tests added for new functionality
- [ ] Coverage remains at 100%
- [ ] Documentation updated (README.md, DEV.md, docstrings)
- [ ] Version bump not included (maintainers handle releases)

## License

MIT License - see [LICENSE](LICENSE) for details.
