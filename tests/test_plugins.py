from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import MagicMock

from pytest import LogCaptureFixture

from bygge.contracts import Input, Payload, PluginResult
from bygge.plugins.basedpyright import Basedpyright
from bygge.plugins.hatchling import Hatchling
from bygge.plugins.pytest import Pytest
from bygge.plugins.pytest_cov import PytestCov
from bygge.plugins.setuptools import Setuptools
from bygge.util import load_toml
from bygge.workspace import Workspace


def test_hatchling_fetch_source_dirs(tmp_package: Path) -> None:
    """Test Hatchling plugin fetches source directories."""
    plugin = Hatchling()
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(pyproject_path=pyproject_path, optional_deps=["dev"])
    blob = load_toml(pyproject_path)

    source_dirs = plugin.fetch_source_dirs(input=input, blob=blob)

    assert source_dirs is not None
    assert len(source_dirs) == 1
    assert source_dirs[0].name == "test_pkg"


def test_hatchling_non_hatchling_backend(tmp_package: Path) -> None:
    """Test Hatchling plugin returns None for non-hatchling backend."""
    plugin = Hatchling()
    pyproject_path = tmp_package / "pyproject.toml"

    content = pyproject_path.read_text()
    content = content.replace("hatchling.build", "setuptools.build_meta")
    _ = pyproject_path.write_text(content)

    input = Input(pyproject_path=pyproject_path, optional_deps=["dev"])
    blob = load_toml(pyproject_path)

    source_dirs = plugin.fetch_source_dirs(input=input, blob=blob)
    assert source_dirs is None


def test_hatchling_missing_packages(tmp_package: Path, caplog: LogCaptureFixture) -> None:
    """Test Hatchling plugin handles missing packages config."""
    plugin = Hatchling()
    pyproject_path = tmp_package / "pyproject.toml"

    content = pyproject_path.read_text()
    lines = content.split("\n")
    filtered = [
        line
        for line in lines
        if not line.startswith("[tool.hatch.build.targets.wheel]") and "packages" not in line
    ]
    _ = pyproject_path.write_text("\n".join(filtered))

    input = Input(pyproject_path=pyproject_path, optional_deps=["dev"])
    blob = load_toml(pyproject_path)

    source_dirs = plugin.fetch_source_dirs(input=input, blob=blob)
    assert source_dirs is None
    assert "defines no source files" in caplog.text


def test_setuptools_fetch_source_dirs(tmp_workspace_dir: Path) -> None:
    """Test Setuptools plugin fetches source directories."""
    plugin = Setuptools()
    pkg_dir = tmp_workspace_dir / "packages" / "setuptools_pkg"
    pkg_dir.mkdir(parents=True)

    pyproject_path = pkg_dir / "pyproject.toml"
    _ = pyproject_path.write_text(
        "[build-system]\n"
        + 'requires = ["setuptools"]\n'
        + 'build-backend = "setuptools.build_meta"\n'
        + "\n"
        + "[tool.setuptools.packages.find]\n"
        + 'where = ["src"]\n'
    )

    (pkg_dir / "src").mkdir()

    input = Input(pyproject_path=pyproject_path, optional_deps=[])
    blob = load_toml(pyproject_path)

    source_dirs = plugin.fetch_source_dirs(input=input, blob=blob)
    assert source_dirs is not None
    assert len(source_dirs) == 1
    assert source_dirs[0].name == "src"


def test_setuptools_non_setuptools_backend(tmp_package: Path) -> None:
    """Test Setuptools plugin returns None for non-setuptools backend."""
    plugin = Setuptools()
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(pyproject_path=pyproject_path, optional_deps=["dev"])
    blob = load_toml(pyproject_path)

    source_dirs = plugin.fetch_source_dirs(input=input, blob=blob)
    assert source_dirs is None


def test_basedpyright_is_installed(tmp_package: Path) -> None:
    """Test Basedpyright plugin detects installation."""
    plugin = Basedpyright()
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(pyproject_path=pyproject_path, optional_deps=["dev"])
    blob = load_toml(pyproject_path)

    is_installed = plugin.is_installed(input=input, blob=blob)
    assert is_installed is True


def test_basedpyright_run_type_check_success(
    tmp_workspace: Workspace, tmp_package: Path, mock_subprocess: MagicMock
) -> None:
    """Test Basedpyright run_type_check with success."""
    plugin = Basedpyright()
    payload = Payload(
        source_dirs=[tmp_package / "src" / "test_pkg"],
        test_dirs=[tmp_package / "tests"],
    )

    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    result = plugin.run_type_check(workspace=tmp_workspace, payload=payload, args=())
    assert result is PluginResult.PASSED


def test_basedpyright_run_type_check_failure(
    tmp_workspace: Workspace, tmp_package: Path, mock_subprocess: MagicMock
) -> None:
    """Test Basedpyright run_type_check with failure."""
    plugin = Basedpyright()
    payload = Payload(
        source_dirs=[tmp_package / "src" / "test_pkg"],
        test_dirs=[tmp_package / "tests"],
    )

    mock_subprocess.return_value = CompletedProcess(args=[], returncode=1, stdout="", stderr="")

    result = plugin.run_type_check(workspace=tmp_workspace, payload=payload, args=())
    assert result is PluginResult.FAILED


def test_pytest_is_installed(tmp_package: Path) -> None:
    """Test Pytest plugin detects installation."""
    plugin = Pytest()
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(pyproject_path=pyproject_path, optional_deps=["dev"])
    blob = load_toml(pyproject_path)

    is_installed = plugin.is_installed(input=input, blob=blob)
    assert is_installed is True


def test_pytest_run_test_success(
    tmp_workspace: Workspace, tmp_package: Path, mock_subprocess: MagicMock
) -> None:
    """Test Pytest run_test with success."""
    plugin = Pytest()
    payload = Payload(
        source_dirs=[tmp_package / "src" / "test_pkg"],
        test_dirs=[tmp_package / "tests"],
    )

    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    result = plugin.run_test(workspace=tmp_workspace, payload=payload, args=())
    assert result is PluginResult.PASSED


def test_pytest_run_test_failure(
    tmp_workspace: Workspace, tmp_package: Path, mock_subprocess: MagicMock
) -> None:
    """Test Pytest run_test with failure."""
    plugin = Pytest()
    payload = Payload(
        source_dirs=[tmp_package / "src" / "test_pkg"],
        test_dirs=[tmp_package / "tests"],
    )

    mock_subprocess.return_value = CompletedProcess(args=[], returncode=1, stdout="", stderr="")

    result = plugin.run_test(workspace=tmp_workspace, payload=payload, args=())
    assert result is PluginResult.FAILED


def test_pytest_cov_is_installed(tmp_package: Path) -> None:
    """Test PytestCov plugin detects installation."""
    plugin = PytestCov()
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(pyproject_path=pyproject_path, optional_deps=["dev"])
    blob = load_toml(pyproject_path)

    is_installed = plugin.is_installed(input=input, blob=blob)
    assert is_installed is True


def test_pytest_cov_run_coverage_success(
    tmp_workspace: Workspace, tmp_package: Path, mock_subprocess: MagicMock
) -> None:
    """Test PytestCov run_coverage with success."""
    plugin = PytestCov()
    payload = Payload(
        source_dirs=[tmp_package / "src" / "test_pkg"],
        test_dirs=[tmp_package / "tests"],
    )

    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    result = plugin.run_coverage(
        workspace=tmp_workspace, payload=payload, args=(), coverage_baseline=100
    )
    assert result is PluginResult.PASSED
    call_args = mock_subprocess.call_args_list[0]
    assert "--cov-fail-under=100" in call_args[0][0]


def test_pytest_cov_run_coverage_no_baseline(
    tmp_workspace_dir: Path, tmp_package: Path, mock_subprocess: MagicMock
) -> None:
    """Test PytestCov run_coverage without baseline."""
    _ = PytestCov()
    _ = Workspace.open(tmp_workspace_dir)
    _ = Payload(
        source_dirs=[tmp_package / "src" / "test_pkg"],
        test_dirs=[tmp_package / "tests"],
    )

    mock_subprocess.return_value = CompletedProcess(args=[], returncode=0, stdout="", stderr="")
