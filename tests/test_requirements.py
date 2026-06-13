from __future__ import annotations

from pathlib import Path

from bygge.requirements import get_requirements
from bygge.util import load_toml


def test_package_meta_get_requirements_with_optional_deps(tmp_package: Path) -> None:
    """Test PackageMeta._get_requirements includes optional dependencies."""
    pyproject_path = tmp_package / "pyproject.toml"
    blob = load_toml(pyproject_path)

    requirements = get_requirements(blob=blob, optional_deps=["dev"])

    req_names = {req.name for req in requirements}
    assert "pytest" in req_names
    assert "pytest-cov" in req_names
    assert "basedpyright" in req_names
    assert "ruff" in req_names


def test_package_meta_get_requirements_without_optional_deps(tmp_package: Path) -> None:
    """Test PackageMeta._get_requirements excludes optional deps when not specified."""
    pyproject_path = tmp_package / "pyproject.toml"
    blob = load_toml(pyproject_path)

    requirements = get_requirements(blob=blob, optional_deps=[])

    assert len(requirements) == 0
