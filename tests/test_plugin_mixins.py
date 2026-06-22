from __future__ import annotations

from pathlib import Path

from bygge.contracts import Input
from bygge.plugins.magic_sources import MagicSources
from bygge.plugins.test_dirs_mixin import TestDirsMixin
from bygge.util import load_toml


def test_test_dirs_mixin_with_pytest(tmp_package: Path) -> None:
    """Test TestDirsMixin.fetch_test_dirs finds test dirs when pytest is installed."""
    mixin = TestDirsMixin()
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(
        pyproject_path=pyproject_path, optional_deps=["dev"], blob=load_toml(pyproject_path)
    )
    blob = load_toml(pyproject_path)

    test_dirs = mixin.fetch_test_dirs(input=input, blob=blob)

    assert test_dirs is not None
    assert len(test_dirs) == 1
    assert test_dirs[0].name == "tests"


def test_test_dirs_mixin_without_pytest(tmp_package: Path) -> None:
    """Test TestDirsMixin.fetch_test_dirs returns None when pytest is not installed."""
    mixin = TestDirsMixin()
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(pyproject_path=pyproject_path, optional_deps=[], blob=load_toml(pyproject_path))
    blob = load_toml(pyproject_path)

    test_dirs = mixin.fetch_test_dirs(input=input, blob=blob)

    assert test_dirs is None


def test_test_dirs_mixin_no_testpaths(tmp_workspace_dir: Path) -> None:
    """Test TestDirsMixin.fetch_test_dirs returns None when testpaths is missing."""
    pkg_dir = tmp_workspace_dir / "packages" / "no_testpaths"
    pkg_dir.mkdir(parents=True)

    pyproject_path = pkg_dir / "pyproject.toml"
    _ = pyproject_path.write_text(
        "[project]\n"
        + 'name = "no_testpaths"\n'
        + 'version = "0.1.0"\n'
        + "\n"
        + "[project.optional-dependencies]\n"
        + 'dev = ["pytest"]\n'
    )

    mixin = TestDirsMixin()
    input = Input(
        pyproject_path=pyproject_path, optional_deps=["dev"], blob=load_toml(pyproject_path)
    )
    blob = load_toml(pyproject_path)

    test_dirs = mixin.fetch_test_dirs(input=input, blob=blob)

    assert test_dirs is None


def test_magic_sources_finds_src_dir(tmp_package: Path) -> None:
    """Test MagicSources.fetch_source_dirs finds src directory."""
    plugin = MagicSources()
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(pyproject_path=pyproject_path, optional_deps=[], blob=load_toml(pyproject_path))
    blob = load_toml(pyproject_path)

    source_dirs = plugin.fetch_source_dirs(input=input, blob=blob)

    assert source_dirs is not None
    assert len(source_dirs) == 1
    assert source_dirs[0].name == "src"


def test_magic_sources_no_src_dir(tmp_workspace_dir: Path) -> None:
    """Test MagicSources.fetch_source_dirs returns None when src dir doesn't exist."""
    pkg_dir = tmp_workspace_dir / "packages" / "no_src"
    pkg_dir.mkdir(parents=True)

    pyproject_path = pkg_dir / "pyproject.toml"
    _ = pyproject_path.write_text('[project]\nname = "no_src"\nversion = "0.1.0"\n')

    plugin = MagicSources()
    input = Input(pyproject_path=pyproject_path, optional_deps=[], blob=load_toml(pyproject_path))
    blob = load_toml(pyproject_path)

    source_dirs = plugin.fetch_source_dirs(input=input, blob=blob)

    assert source_dirs is None
