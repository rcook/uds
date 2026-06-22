from __future__ import annotations

from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from unittest.mock import MagicMock

from pytest import raises

from bygge.contracts import Input, PluginResult
from bygge.plugins.pytest_run_mixin import PytestRunMixin
from bygge.plugins.util import check_requirements, fetch_pytest_test_dirs, get_requirements
from bygge.util import load_toml


def test_get_requirements_with_dependencies(tmp_package: Path) -> None:
    """Test get_requirements extracts dependencies."""
    pyproject_path = tmp_package / "pyproject.toml"
    blob = load_toml(pyproject_path)
    input = Input(pyproject_path=pyproject_path, optional_deps=["dev"], blob=blob)

    requirements = get_requirements(input=input, blob=blob)

    req_names = {req.name for req in requirements}
    assert "pytest" in req_names
    assert "pytest-cov" in req_names


def test_get_requirements_no_optional_deps(tmp_package: Path) -> None:
    """Test get_requirements without optional dependencies."""
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(pyproject_path=pyproject_path, optional_deps=[], blob=load_toml(pyproject_path))
    blob = load_toml(pyproject_path)

    requirements = get_requirements(input=input, blob=blob)

    assert len(requirements) == 0


def test_fetch_pytest_test_dirs_success(tmp_package: Path) -> None:
    """Test fetch_pytest_test_dirs finds test directories."""
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(
        pyproject_path=pyproject_path, optional_deps=["dev"], blob=load_toml(pyproject_path)
    )
    blob = load_toml(pyproject_path)

    test_dirs = fetch_pytest_test_dirs(input=input, blob=blob)

    assert test_dirs is not None
    assert len(test_dirs) == 1
    assert test_dirs[0].name == "tests"


def test_check_requirements_missing_required_dep(tmp_package: Path) -> None:
    """Test fetch_pytest_test_dirs returns None when required dep is missing."""
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(pyproject_path=pyproject_path, optional_deps=[], blob=load_toml(pyproject_path))
    blob = load_toml(pyproject_path)

    assert not check_requirements(input=input, blob=blob, required_deps=["pytest"])


def test_fetch_pytest_test_dirs_no_testpaths(tmp_workspace_dir: Path) -> None:
    """Test fetch_pytest_test_dirs returns None when testpaths is missing."""
    pkg_dir = tmp_workspace_dir / "packages" / "no_testpaths_pkg"
    pkg_dir.mkdir(parents=True)

    pyproject_path = pkg_dir / "pyproject.toml"
    _ = pyproject_path.write_text(
        "[project]\n"
        + 'name = "no_testpaths_pkg"\n'
        + 'version = "0.1.0"\n'
        + "\n"
        + "[project.optional-dependencies]\n"
        + 'dev = ["pytest"]\n'
    )

    input = Input(
        pyproject_path=pyproject_path, optional_deps=["dev"], blob=load_toml(pyproject_path)
    )
    blob = load_toml(pyproject_path)

    test_dirs = fetch_pytest_test_dirs(input=input, blob=blob)

    assert test_dirs is None


def test_pytest_run_mixin_success(mock_subprocess: MagicMock) -> None:
    """Test PytestRunMixin.run_pytest with success."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")
    mixin = PytestRunMixin()

    result = mixin.run_pytest(cmd=["pytest"], cwd=Path("/tmp"))

    assert result is PluginResult.PASSED


def test_pytest_run_mixin_test_failure(mock_subprocess: MagicMock) -> None:
    """Test PytestRunMixin.run_pytest with test failure."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=1, stdout="", stderr="")
    mixin = PytestRunMixin()

    result = mixin.run_pytest(cmd=["pytest"], cwd=Path("/tmp"))

    assert result is PluginResult.FAILED


def test_pytest_run_mixin_no_test_dirs(mock_subprocess: MagicMock) -> None:
    """Test PytestRunMixin.run_pytest with missing test directories."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=4, stdout="", stderr="")
    mixin = PytestRunMixin()

    result = mixin.run_pytest(cmd=["pytest"], cwd=Path("/tmp"))

    assert result is PluginResult.PLUGIN_ERROR


def test_pytest_run_mixin_no_tests_found(mock_subprocess: MagicMock) -> None:
    """Test PytestRunMixin.run_pytest with no tests found."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=5, stdout="", stderr="")
    mixin = PytestRunMixin()

    result = mixin.run_pytest(cmd=["pytest"], cwd=Path("/tmp"))

    assert result is PluginResult.PLUGIN_ERROR


def test_pytest_run_mixin_unexpected_returncode(mock_subprocess: MagicMock) -> None:
    """Test PytestRunMixin.run_pytest with unexpected return code."""
    mock_subprocess.return_value = CompletedProcess(args=[], returncode=99, stdout="", stderr="")
    mixin = PytestRunMixin()

    with raises(CalledProcessError):
        _ = mixin.run_pytest(cmd=["pytest"], cwd=Path("/tmp"))
