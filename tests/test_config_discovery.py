from __future__ import annotations

from pathlib import Path

from pytest import raises

from bygge import ByggeError
from bygge.constants import DOT_FILE_NAME
from bygge.dot_config import DotConfig
from bygge.target_info import TargetInfo
from bygge.workspace import Workspace


def test_dot_config_load_defaults(tmp_workspace_dir: Path) -> None:
    """Test DotConfig.load with default values."""
    dot_path = tmp_workspace_dir / DOT_FILE_NAME
    _ = dot_path.write_text("[workspace]\n")

    config = DotConfig.load(workspace_dir=tmp_workspace_dir, dot_path=dot_path)

    assert config.package_root_dir == tmp_workspace_dir
    assert config.venv_dir == tmp_workspace_dir / ".venv"
    assert config.optional_deps == []
    assert config.coverage_baseline is None


def test_dot_config_load_custom_values(tmp_workspace_dir: Path) -> None:
    """Test DotConfig.load with custom values."""
    dot_path = tmp_workspace_dir / DOT_FILE_NAME
    _ = dot_path.write_text(
        "[workspace]\n"
        + 'package_root_dir = "packages"\n'
        + 'venv_dir = ".venv"\n'
        + 'optional_deps = ["dev", "test"]\n'
        + "coverage_baseline = 80\n"
    )

    config = DotConfig.load(workspace_dir=tmp_workspace_dir, dot_path=dot_path)

    assert config.package_root_dir == tmp_workspace_dir / "packages"
    assert config.venv_dir == tmp_workspace_dir / ".venv"
    assert config.optional_deps == ["dev", "test"]
    assert config.coverage_baseline == 80


def test_dot_config_invalid_coverage_baseline(tmp_workspace_dir: Path) -> None:
    """Test DotConfig.load with invalid coverage baseline."""
    dot_path = tmp_workspace_dir / DOT_FILE_NAME
    _ = dot_path.write_text('[workspace]\ncoverage_baseline = "invalid"\n')

    with raises(ByggeError, match="Invalid code coverage baseline"):
        _ = DotConfig.load(workspace_dir=tmp_workspace_dir, dot_path=dot_path)


def test_workspace_find_from_cwd(tmp_workspace: Workspace) -> None:
    """Test Workspace.find discovers workspace from cwd."""
    assert tmp_workspace.cwd == tmp_workspace.workspace_dir
    assert tmp_workspace.package_root_dir == tmp_workspace.workspace_dir / "packages"
    assert tmp_workspace.optional_deps == ["dev"]
    assert tmp_workspace.coverage_baseline == 100


def test_workspace_find_explicit_dir_missing_config(tmp_path: Path) -> None:
    assert Workspace.probe(cwd=Path.cwd(), workspace_dir=tmp_path) is None


def test_workspace_make_bin_path(tmp_workspace: Workspace) -> None:
    """Test Workspace.make_bin_path constructs correct path."""
    bin_path = tmp_workspace.make_bin_path("pytest", must_exist=False)

    assert "pytest" in str(bin_path)
    assert ".venv" in str(bin_path)


def test_workspace_make_bin_path_must_exist(tmp_workspace: Workspace) -> None:
    """Test Workspace.make_bin_path raises when binary doesn't exist."""
    with raises(ByggeError, match="Cannot find binary"):
        _ = tmp_workspace.make_bin_path("nonexistent", must_exist=True)


def test_target_info_build(tmp_workspace: Workspace, tmp_package: Path) -> None:  # pyright: ignore[reportUnusedParameter]
    """Test TargetInfo.build discovers packages and requirements."""
    target_info = TargetInfo.build(workspace=tmp_workspace)

    assert len(target_info.ordered_metas) == 1
    assert target_info.ordered_metas[0].name == "test_pkg"
    assert isinstance(target_info.requirements_paths, list)


def test_target_info_ignores_directories(tmp_workspace_dir: Path, tmp_package: Path) -> None:  # pyright: ignore[reportUnusedParameter]
    """Test TargetInfo.build ignores common directories."""
    (tmp_workspace_dir / "packages" / ".venv").mkdir()
    _ = (tmp_workspace_dir / "packages" / ".venv" / "pyproject.toml").write_text(
        "[project]\nname = 'ignored'\n"
    )

    workspace = Workspace.open(tmp_workspace_dir)
    target_info = TargetInfo.build(workspace=workspace)

    package_names = [meta.name for meta in target_info.ordered_metas]
    assert "ignored" not in package_names


def test_target_info_topological_sort(tmp_workspace_dir: Path) -> None:
    """Test TargetInfo.build sorts packages by dependencies."""
    pkg_a_dir = tmp_workspace_dir / "packages" / "pkg_a"
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

    pkg_b_dir = tmp_workspace_dir / "packages" / "pkg_b"
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

    workspace = Workspace.open(tmp_workspace_dir)
    target_info = TargetInfo.build(workspace=workspace)

    package_names = [meta.name for meta in target_info.ordered_metas]
    assert package_names.index("pkg_a") < package_names.index("pkg_b")


def test_target_info_finds_requirements_files(tmp_workspace_dir: Path) -> None:
    """Test TargetInfo.build finds requirements files."""
    _ = (tmp_workspace_dir / "requirements.txt").write_text("pytest\n")
    _ = (tmp_workspace_dir / "requirements-dev.txt").write_text("black\n")

    workspace = Workspace.open(tmp_workspace_dir)
    target_info = TargetInfo.build(workspace=workspace)

    req_names = [p.name for p in target_info.requirements_paths]
    assert "requirements.txt" in req_names
    assert "requirements-dev.txt" in req_names


def test_target_info_filters_requirements_by_optional_deps(tmp_workspace_dir: Path) -> None:
    """Test TargetInfo.build filters requirements by optional deps."""
    _ = (tmp_workspace_dir / "requirements-prod.txt").write_text("requests\n")
    _ = (tmp_workspace_dir / "requirements-dev.txt").write_text("pytest\n")

    dot_path = tmp_workspace_dir / DOT_FILE_NAME
    content = dot_path.read_text()
    content = content.replace('optional_deps = ["dev"]', 'optional_deps = ["dev"]')
    _ = dot_path.write_text(content)

    workspace = Workspace.open(tmp_workspace_dir)
    target_info = TargetInfo.build(workspace=workspace)

    req_names = [p.name for p in target_info.requirements_paths]
    assert "requirements-dev.txt" in req_names
