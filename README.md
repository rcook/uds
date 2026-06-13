# bygge

[![CI](https://github.com/rcook/bygge/actions/workflows/ci.yml/badge.svg)](https://github.com/rcook/bygge/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/bygge)](https://pypi.org/project/bygge/)
[![Python Version](https://img.shields.io/pypi/pyversions/bygge)](https://pypi.org/project/bygge/)
[![License](https://img.shields.io/github/license/rcook/bygge)](LICENSE)

**bygge** (pronounced *BYG-eh*, Norwegian for "to build") — A CLI tool for Python project development and workspace management.

`bygge` simplifies development workflows for Python projects by providing a consistent interface for common tasks: testing, linting, type-checking, formatting, and more. It works with both single-package projects and multi-package monorepos.

## Features

- 🔧 **Unified CLI** — One command (`bygge check`) runs all your quality checks
- 📦 **Monorepo support** — Manages multiple packages with inter-dependencies
- 🔌 **Plugin-based** — Automatically detects and configures tools (pytest, ruff, basedpyright)
- 🎯 **Convention over configuration** — Works out-of-the-box with standard Python project layouts
- 🚀 **Fast** — Runs checks in topological order for correct dependency resolution
- 🪝 **Git hooks** — Built-in pre-commit hook support

## Installation

```bash
pip install bygge
```

For development:

```bash
pip install bygge[dev]
```

## Quick Start

Initialize your project:

```bash
# Create .bygge.toml configuration
cat > .bygge.toml << 'EOF'
[workspace]
venv_dir = ".venv"
optional_deps = ["dev"]
coverage_baseline = 100
EOF

# Install git hooks
bygge hooks

# Run all checks (format, lint, typecheck, test with coverage)
bygge check
```

## Usage

### Common commands

```bash
bygge test              # Run tests
bygge coverage          # Run tests with coverage report
bygge fmt               # Format code and sort imports
bygge lint              # Lint code
bygge typecheck         # Type-check code
bygge check             # Run all checks (same as pre-commit)
```

### Check modes

Most commands support `--check` mode for CI/validation:

```bash
bygge fmt --check       # Verify formatting without changes
bygge lint --check      # Verify linting without changes
```

### Environment setup

```bash
bygge init              # Create venv and install packages
bygge info              # Show environment information
```

### Git integration

```bash
bygge hooks             # Install pre-commit hook
bygge unhook            # Remove pre-commit hook
bygge commit-unchecked  # Commit bypassing hooks (use sparingly)
```

## Configuration

Create a `.bygge.toml` file at your project root:

### Single package project

```toml
[workspace]
venv_dir = ".venv"
optional_deps = ["dev"]
coverage_baseline = 100
```

### Monorepo (multiple packages)

```toml
[workspace]
package_root_dir = "packages"  # Directory containing your packages
venv_dir = ".venv"
optional_deps = ["dev"]
coverage_baseline = 95
```

## Tool Detection

`bygge` automatically detects and uses tools from your project dependencies:

| Tool | Purpose | Detected from |
|------|---------|---------------|
| **pytest** | Unit testing | `pytest` in dependencies |
| **pytest-cov** | Coverage reporting | `pytest-cov` in dependencies |
| **basedpyright** | Type checking | `basedpyright` in dependencies |
| **ruff** | Linting & formatting | Built-in (no detection needed) |

Configuration is read from your `pyproject.toml`:
- Pytest: `[tool.pytest.ini_options]`
- Basedpyright: `[tool.basedpyright]`
- Ruff: `[tool.ruff]`

## Monorepo Support

For projects with multiple packages, `bygge` handles:

- **Topological sorting** — Installs packages in dependency order
- **Multi-package discovery** — Finds all packages under `package_root_dir`
- **Unified testing** — Runs tests across all packages
- **Cross-package coverage** — Reports combined coverage

Example monorepo structure:

```
myproject/
├── .bygge.toml
├── pyproject.toml
├── packages/
│   ├── common/
│   │   ├── pyproject.toml
│   │   ├── src/common/
│   │   └── tests/
│   ├── lib/
│   │   ├── pyproject.toml
│   │   ├── src/lib/
│   │   └── tests/
│   └── app/
│       ├── pyproject.toml
│       ├── src/app/
│       └── tests/
└── .venv/
```

## Why bygge?

- **Consistency** — Same commands work across all your projects
- **Simplicity** — No need to remember different tool invocations
- **Reliability** — Runs checks in the right order for monorepos
- **Speed** — No overhead from meta-build systems; direct tool invocation
- **Transparency** — Just a thin wrapper; you can always call tools directly

## Name

**bygge** is Norwegian for "to build" — fitting for a build and development tool. Pronounced *BYG-eh* (rhymes with "dig-eh").

## Contributing

See [DEV.md](DEV.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
