from __future__ import annotations

from pathlib import Path

from pytest import raises

from bygge import ByggeError
from bygge.contracts import Input
from bygge.package_info import PackageInfo
from bygge.package_info.package_info import SkinnyContext
from bygge.package_meta import PackageMeta
from bygge.plugins import (
    Basedpyright,
    Hatchling,
    MagicSources,
    Plugins,
    Pytest,
    PytestCov,
    PytestDiscovery,
    RuffCheckPlugin,
    RuffFormatPlugin,
    Setuptools,
)
from bygge.util import load_toml


def test_package_meta_load(tmp_package: Path) -> None:
    """Test PackageMeta.load parses pyproject.toml."""
    pyproject_path = tmp_package / "pyproject.toml"

    meta = PackageMeta.load(pyproject_path=pyproject_path, optional_deps=["dev"])

    assert meta is not None
    assert meta.name == "test_pkg"
    assert meta.package_dir == tmp_package
    assert meta.build_backend == "hatchling.build"
    assert len(meta.build_requires) > 0
    assert len(meta.requirements) > 0


def test_package_meta_load_missing_name(tmp_workspace_dir: Path) -> None:
    """Test PackageMeta.load returns None when name is missing."""
    pyproject_path = tmp_workspace_dir / "invalid.toml"
    _ = pyproject_path.write_text("[project]\nversion = '0.1.0'\n")

    meta = PackageMeta.load(pyproject_path=pyproject_path, optional_deps=[])

    assert meta is None


def test_package_meta_load_missing_build_backend(tmp_workspace_dir: Path) -> None:
    """Test PackageMeta.load returns None when build backend is missing."""
    pyproject_path = tmp_workspace_dir / "invalid.toml"
    _ = pyproject_path.write_text("[project]\nname = 'test'\n")

    meta = PackageMeta.load(pyproject_path=pyproject_path, optional_deps=[])

    assert meta is not None
    assert meta.name == "test"
    assert meta.package_dir == tmp_workspace_dir
    assert meta.build_backend is None
    assert len(meta.build_requires) == 0
    assert len(meta.requirements) == 0


def test_package_meta_load_invalid_toml(tmp_workspace_dir: Path) -> None:
    """Test PackageMeta.load handles invalid TOML with user-friendly error."""
    pyproject_path = tmp_workspace_dir / "invalid.toml"
    _ = pyproject_path.write_text("invalid toml content [[[")

    # load_toml should raise ByggeError with a user-friendly message
    with raises(ByggeError, match=r"Error parsing.*invalid.toml"):
        _ = PackageMeta.load(pyproject_path=pyproject_path, optional_deps=[])


def test_package_info_make(tmp_package: Path) -> None:
    """Test PackageInfo.make creates package info."""
    plugins = Plugins(
        source_dir_plugins=[Hatchling(), Setuptools(), MagicSources()],
        test_dir_plugins=[PytestDiscovery()],
        test_plugins=[Pytest()],
        coverage_plugins=[PytestCov()],
        type_check_plugins=[Basedpyright()],
        format_plugins=[RuffFormatPlugin()],
        lint_plugins=[RuffCheckPlugin()],
    )
    pyproject_path = tmp_package / "pyproject.toml"
    input = Input(
        pyproject_path=pyproject_path, optional_deps=["dev"], blob=load_toml(pyproject_path)
    )

    info = PackageInfo.make(plugins=plugins, input=input)

    assert info is not None
    assert info.name == "test_pkg"


def test_package_info_make_invalid_toml(tmp_workspace_dir: Path) -> None:
    """Test that loading invalid TOML raises a user-friendly ByggeError."""
    pyproject_path = tmp_workspace_dir / "invalid.toml"
    _ = pyproject_path.write_text("invalid toml [[[")

    # load_toml should raise ByggeError with a user-friendly message
    with raises(ByggeError, match=r"Error parsing.*invalid.toml"):
        _ = load_toml(pyproject_path)


def test_package_info_make_missing_name(tmp_workspace_dir: Path) -> None:
    """Test PackageInfo.make returns None when name is missing."""
    plugins = Plugins(
        source_dir_plugins=[Hatchling(), Setuptools(), MagicSources()],
        test_dir_plugins=[PytestDiscovery()],
        test_plugins=[Pytest()],
        coverage_plugins=[PytestCov()],
        type_check_plugins=[Basedpyright()],
        format_plugins=[RuffFormatPlugin()],
        lint_plugins=[RuffCheckPlugin()],
    )
    pyproject_path = tmp_workspace_dir / "invalid.toml"
    _ = pyproject_path.write_text("[project]\nversion = '0.1.0'\n")
    input = Input(pyproject_path=pyproject_path, optional_deps=[], blob=load_toml(pyproject_path))

    info = PackageInfo.make(plugins=plugins, input=input)

    assert info is None


def test_package_info_get_name(tmp_package: Path) -> None:
    """Test PackageInfo._get_name extracts package name."""
    plugins = Plugins(
        source_dir_plugins=[Hatchling(), Setuptools(), MagicSources()],
        test_dir_plugins=[PytestDiscovery()],
        test_plugins=[Pytest()],
        coverage_plugins=[PytestCov()],
        type_check_plugins=[Basedpyright()],
        format_plugins=[RuffFormatPlugin()],
        lint_plugins=[RuffCheckPlugin()],
    )
    pyproject_path = tmp_package / "pyproject.toml"
    blob = load_toml(pyproject_path)
    skinny_ctx = SkinnyContext(
        plugins=plugins,
        input=Input(
            pyproject_path=pyproject_path, optional_deps=[], blob=load_toml(pyproject_path)
        ),
        blob=blob,
    )

    name = skinny_ctx.get_name()

    assert name == "test_pkg"


def test_package_info_get_source_dirs(tmp_package: Path) -> None:
    """Test PackageInfo._get_source_dirs finds source directories."""
    plugins = Plugins(
        source_dir_plugins=[Hatchling(), Setuptools(), MagicSources()],
        test_dir_plugins=[PytestDiscovery()],
        test_plugins=[Pytest()],
        coverage_plugins=[PytestCov()],
        type_check_plugins=[Basedpyright()],
        format_plugins=[RuffFormatPlugin()],
        lint_plugins=[RuffCheckPlugin()],
    )
    pyproject_path = tmp_package / "pyproject.toml"
    blob = load_toml(pyproject_path)
    skinny_ctx = SkinnyContext(
        plugins=plugins,
        input=Input(
            pyproject_path=pyproject_path, optional_deps=["dev"], blob=load_toml(pyproject_path)
        ),
        blob=blob,
    )

    source_dirs = skinny_ctx.get_source_dirs()

    assert source_dirs is not None
    assert len(source_dirs) > 0


def test_package_info_get_test_dirs(tmp_package: Path) -> None:
    """Test PackageInfo._get_test_dirs finds test directories."""
    plugins = Plugins(
        source_dir_plugins=[Hatchling(), Setuptools(), MagicSources()],
        test_dir_plugins=[PytestDiscovery()],
        test_plugins=[Pytest()],
        coverage_plugins=[PytestCov()],
        type_check_plugins=[Basedpyright()],
        format_plugins=[RuffFormatPlugin()],
        lint_plugins=[RuffCheckPlugin()],
    )
    pyproject_path = tmp_package / "pyproject.toml"
    blob = load_toml(pyproject_path)
    skinny_ctx = SkinnyContext(
        plugins=plugins,
        input=Input(
            pyproject_path=pyproject_path, optional_deps=["dev"], blob=load_toml(pyproject_path)
        ),
        blob=blob,
    )

    test_dirs = skinny_ctx.get_test_dirs()

    assert test_dirs is not None
    assert len(test_dirs) > 0
