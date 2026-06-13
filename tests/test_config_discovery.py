from __future__ import annotations

import re
from pathlib import Path

import pytest

from bygge import ByggeError
from bygge.dot_config import DotConfig
from bygge.target_info import TargetInfo
from bygge.workspace import Workspace


def test_dot_config_load_defaults(tmp_workspace: Path) -> None:
    """Test DotConfig.load with default values."""
    dot_path = tmp_workspace / ".bygge.toml"
    _ = dot_path.write_text("[workspace]\n")

    config = DotConfig.load(workspace_dir=tmp_workspace, dot_path=dot_path)

    assert config.package_root_dir == tmp_workspace
    assert config.venv_dir == tmp_workspace / ".venv"
    assert config.optional_deps == []
    assert config.coverage_baseline is None


def test_dot_config_load_custom_values(tmp_workspace: Path) -> None:
    """Test DotConfig.load with custom values."""
    dot_path = tmp_workspace / ".bygge.toml"
    _ = dot_path.write_text(
        "[workspace]\n"
        + 'package_root_dir = "packages"\n'
        + 'venv_dir = ".venv"\n'
        + 'optional_deps = ["dev", "test"]\n'
        + "coverage_baseline = 80\n"
    )

    config = DotConfig.load(workspace_dir=tmp_workspace, dot_path=dot_path)

    assert config.package_root_dir == tmp_workspace / "packages"
    assert config.venv_dir == tmp_workspace / ".venv"
    assert config.optional_deps == ["dev", "test"]
    assert config.coverage_baseline == 80


def test_dot_config_invalid_coverage_baseline(tmp_workspace: Path) -> None:
    """Test DotConfig.load with invalid coverage baseline."""
    dot_path = tmp_workspace / ".bygge.toml"
    _ = dot_path.write_text('[workspace]\ncoverage_baseline = "invalid"\n')

    with pytest.raises(ByggeError, match="Invalid code coverage baseline"):
        _ = DotConfig.load(workspace_dir=tmp_workspace, dot_path=dot_path)


def test_workspace_find_from_cwd(tmp_workspace: Path) -> None:
    """Test Workspace.find discovers workspace from cwd."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)

    assert workspace.cwd == tmp_workspace
    assert workspace.workspace_dir == tmp_workspace
    assert workspace.package_root_dir == tmp_workspace / "packages"
    assert workspace.optional_deps == ["dev"]
    assert workspace.coverage_baseline == 100


def test_workspace_find_explicit_dir(tmp_workspace: Path) -> None:
    """Test Workspace.find with explicit workspace_dir."""
    workspace = Workspace.find(cwd=Path.cwd(), workspace_dir=tmp_workspace)

    assert workspace.workspace_dir == tmp_workspace
    assert workspace.package_root_dir == tmp_workspace / "packages"


def test_workspace_find_missing_dot_file(tmp_path: Path) -> None:
    """Test Workspace.find raises when .bygge.toml is missing."""
    with pytest.raises(ByggeError, match=re.escape("Could not find .bygge.toml")):
        _ = Workspace.find(cwd=tmp_path, workspace_dir=None)


def test_workspace_find_explicit_dir_missing_config(tmp_path: Path) -> None:
    """Test Workspace.find raises when explicit dir has no .bygge.toml."""
    with pytest.raises(ByggeError, match=r"Configuration file .* not found"):
        _ = Workspace.find(cwd=Path.cwd(), workspace_dir=tmp_path)


def test_workspace_make_bin_path(tmp_workspace: Path) -> None:
    """Test Workspace.make_bin_path constructs correct path."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)

    bin_path = workspace.make_bin_path("pytest", must_exist=False)

    assert "pytest" in str(bin_path)
    assert ".venv" in str(bin_path)


def test_workspace_make_bin_path_must_exist(tmp_workspace: Path) -> None:
    """Test Workspace.make_bin_path raises when binary doesn't exist."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)

    with pytest.raises(ByggeError, match="Cannot find binary"):
        _ = workspace.make_bin_path("nonexistent", must_exist=True)


def test_target_info_build(tmp_workspace: Path, tmp_package: Path) -> None:  # pyright: ignore[reportUnusedParameter]
    """Test TargetInfo.build discovers packages and requirements."""
    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)

    target_info = TargetInfo.build(workspace=workspace)

    assert len(target_info.ordered_metas) == 1
    assert target_info.ordered_metas[0].name == "test_pkg"
    assert isinstance(target_info.requirements_paths, list)


def test_target_info_ignores_directories(tmp_workspace: Path, tmp_package: Path) -> None:  # pyright: ignore[reportUnusedParameter]
    """Test TargetInfo.build ignores common directories."""
    (tmp_workspace / "packages" / ".venv").mkdir()
    _ = (tmp_workspace / "packages" / ".venv" / "pyproject.toml").write_text(
        "[project]\nname = 'ignored'\n"
    )

    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    target_info = TargetInfo.build(workspace=workspace)

    package_names = [meta.name for meta in target_info.ordered_metas]
    assert "ignored" not in package_names


def test_target_info_topological_sort(tmp_workspace: Path) -> None:
    """Test TargetInfo.build sorts packages by dependencies."""
    pkg_a_dir = tmp_workspace / "packages" / "pkg_a"
    pkg_a_dir.mkdir(parents=True)
    _ = (pkg_a_dir / "pyproject.toml").write_text(
        "[build-system]\n"
        + 'requires = ["hatchling"]\n'
        + 'build-backend = "hatchling.build"\n'
        + "\n"
        + "[project]\n"
        + 'name = "pkg_a"\n'
        + 'version = "0.1.0"\n'
        + "dependencies = []\n"
    )

    pkg_b_dir = tmp_workspace / "packages" / "pkg_b"
    pkg_b_dir.mkdir(parents=True)
    _ = (pkg_b_dir / "pyproject.toml").write_text(
        "[build-system]\n"
        + 'requires = ["hatchling"]\n'
        + 'build-backend = "hatchling.build"\n'
        + "\n"
        + "[project]\n"
        + 'name = "pkg_b"\n'
        + 'version = "0.1.0"\n'
        + 'dependencies = ["pkg_a"]\n'
    )

    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    target_info = TargetInfo.build(workspace=workspace)

    package_names = [meta.name for meta in target_info.ordered_metas]
    assert package_names.index("pkg_a") < package_names.index("pkg_b")


def test_target_info_finds_requirements_files(tmp_workspace: Path) -> None:
    """Test TargetInfo.build finds requirements files."""
    _ = (tmp_workspace / "requirements.txt").write_text("pytest\n")
    _ = (tmp_workspace / "requirements-dev.txt").write_text("black\n")

    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    target_info = TargetInfo.build(workspace=workspace)

    req_names = [p.name for p in target_info.requirements_paths]
    assert "requirements.txt" in req_names
    assert "requirements-dev.txt" in req_names


def test_target_info_filters_requirements_by_optional_deps(tmp_workspace: Path) -> None:
    """Test TargetInfo.build filters requirements by optional deps."""
    _ = (tmp_workspace / "requirements-prod.txt").write_text("requests\n")
    _ = (tmp_workspace / "requirements-dev.txt").write_text("pytest\n")

    dot_path = tmp_workspace / ".bygge.toml"
    content = dot_path.read_text()
    content = content.replace('optional_deps = ["dev"]', 'optional_deps = ["dev"]')
    _ = dot_path.write_text(content)

    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)
    target_info = TargetInfo.build(workspace=workspace)

    req_names = [p.name for p in target_info.requirements_paths]
    assert "requirements-dev.txt" in req_names
