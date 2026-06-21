from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock

import pytest

from bygge.constants import IS_WINDOWS


@pytest.fixture
def mock_subprocess(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock subprocess.run to avoid actual shell commands in tests."""
    mock = MagicMock(return_value=CompletedProcess(args=[], returncode=0, stdout="", stderr=""))
    monkeypatch.setattr("subprocess.run", mock)
    return mock


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    """Create a minimal workspace with .bygge.toml."""
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()

    # Create .bygge.toml
    bygge_toml = workspace_dir / ".bygge.toml"
    _ = bygge_toml.write_text(
        "[workspace]\n"
        + 'package_root_dir = "packages"\n'
        + 'venv_dir = ".venv"\n'
        + 'optional_deps = ["dev"]\n'
        + "coverage_baseline = 100\n"
    )

    # Create packages directory
    (workspace_dir / "packages").mkdir()

    # Create venv bin directory with dummy binaries
    if IS_WINDOWS:
        venv_bin = workspace_dir / ".venv" / "Scripts"
        ext = ".exe"
    else:
        venv_bin = workspace_dir / ".venv" / "bin"
        ext = ""

    venv_bin.mkdir(parents=True)

    # Create dummy executables for common tools
    for tool in ["basedpyright", "pytest", "python", "ruff"]:
        tool_file_name = f"{tool}{ext}"
        tool_path = venv_bin / tool_file_name
        tool_path.touch()
        tool_path.chmod(0o755)

    return workspace_dir


@pytest.fixture
def tmp_package(tmp_workspace: Path) -> Path:
    """Create a minimal package with pyproject.toml inside tmp_workspace."""
    pkg_dir = tmp_workspace / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)

    src_dir = pkg_dir / "src" / "test_pkg"
    src_dir.mkdir(parents=True)
    _ = (src_dir / "__init__.py").write_text("VERSION = '0.1.0'\n")
    (src_dir / "py.typed").touch()

    tests_dir = pkg_dir / "tests"
    tests_dir.mkdir()
    _ = (tests_dir / "test_placeholder.py").write_text(
        "def test_example() -> None:\n    assert True\n"
    )

    pyproject = pkg_dir / "pyproject.toml"
    _ = pyproject.write_text(
        "[build-system]\n"
        + 'requires = ["hatchling"]\n'
        + 'build-backend = "hatchling.build"\n'
        + "\n"
        + "[project]\n"
        + 'name = "test_pkg"\n'
        + 'version = "0.1.0"\n'
        + 'requires-python = ">=3.14"\n'
        + "dependencies = []\n"
        + "\n"
        + "[project.optional-dependencies]\n"
        + 'dev = ["pytest", "pytest-cov", "basedpyright", "ruff"]\n'
        + "\n"
        + "[tool.pytest.ini_options]\n"
        + 'testpaths = ["tests"]\n'
        + "\n"
        + "[tool.hatch.build.targets.wheel]\n"
        + 'packages = ["src/test_pkg"]\n'
    )

    return pkg_dir


def create_pyproject(
    path: Path,
    name: str,
    build_backend: str = "hatchling.build",
    deps: list[str] | None = None,
    optional_deps: dict[str, list[str]] | None = None,
    **kwargs: dict[str, str | int | bool | dict[str, str]],
) -> None:
    """Helper to create a pyproject.toml with common patterns."""
    lines = [
        "[build-system]",
        f'requires = ["{build_backend.split(".")[0]}"]',
        f'build-backend = "{build_backend}"',
        "",
        "[project]",
        f'name = "{name}"',
        'version = "0.1.0"',
        'requires-python = ">=3.14"',
        f"dependencies = {deps or []}",
    ]

    if optional_deps:
        lines.append("")
        lines.append("[project.optional-dependencies]")
        for key, value in optional_deps.items():
            lines.append(f"{key} = {value}")

    for section, content in kwargs.items():
        lines.append("")
        lines.append(f"[{section}]")
        assert isinstance(content, dict)
        for k, v in content.items():
            lines.append(f"{k} = {v!r}")

    _ = path.write_text("\n".join(lines) + "\n")
