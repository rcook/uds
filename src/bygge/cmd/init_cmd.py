from __future__ import annotations

import shutil
from logging import info
from pathlib import Path

from bygge.constants import BOOTSTRAP_PYTHON_PATH
from bygge.package_meta import PackageMeta
from bygge.run import run_subprocess
from bygge.target_info import TargetInfo
from bygge.workspace import Workspace


def init(workspace: Workspace, reinit: bool, install: bool, yes: bool) -> None:
    _ensure_venv(workspace=workspace, reinit=reinit, yes=yes)

    if install:
        target_info = TargetInfo.build(workspace)

        for meta in target_info.ordered_metas:
            _install_package(workspace=workspace, meta=meta, yes=yes)

        for p in target_info.requirements_paths:
            _install_requirements(workspace=workspace, requirements_path=p, yes=yes)


def _ensure_venv(workspace: Workspace, reinit: bool, yes: bool) -> None:
    if workspace.venv_dir.is_dir() and reinit and yes:
        shutil.rmtree(workspace.venv_dir)

    if not workspace.venv_dir.is_dir():
        info(f"Creating Python virtual environment at {workspace.venv_dir}")
        _ = run_subprocess(
            [str(BOOTSTRAP_PYTHON_PATH), "-m", "venv", str(workspace.venv_dir), "--upgrade-deps"],
            cwd=workspace.cwd,
            check=True,
            yes=yes,
        )
    else:
        info(f"Using existing Python virtual environment at {workspace.venv_dir}")


def _install_package(workspace: Workspace, meta: PackageMeta, yes: bool) -> None:
    info(f"Installing package {meta.name} in editable mode")

    python_path = workspace.make_bin_path("python")
    deps = (
        ""
        if len(workspace.optional_deps) == 0
        else "[" + ",".join(sorted(workspace.optional_deps)) + "]"
    )

    _ = run_subprocess(
        [
            str(python_path),
            "-m",
            "pip",
            "install",
            "--require-virtualenv",
            "--editable",
            f"{meta.package_dir}{deps}",
        ],
        cwd=workspace.cwd,
        check=True,
        yes=yes,
    )


def _install_requirements(workspace: Workspace, requirements_path: Path, yes: bool) -> None:
    info(f"Installing requirements from {requirements_path}")

    python_path = workspace.make_bin_path("python")

    _ = run_subprocess(
        [
            str(python_path),
            "-m",
            "pip",
            "install",
            "--require-virtualenv",
            "--requirement",
            str(requirements_path),
        ],
        cwd=workspace.cwd,
        check=True,
        yes=yes,
    )
