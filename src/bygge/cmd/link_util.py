from __future__ import annotations

from pathlib import Path

from bygge import ByggeError
from bygge.constants import IS_WINDOWS, PYPROJECT_FILE_NAME
from bygge.util import load_toml, query_toml, try_dict, walk_dir
from bygge.workspace import Workspace


def resolve_output_dir(output_dir: Path | None) -> Path:
    """Resolve the output directory for script links.

    If output_dir is provided, returns it resolved.
    Otherwise returns the platform default (~/.local/bin on POSIX).
    Raises ByggeError on Windows if output_dir is not provided.
    """
    if output_dir is not None:
        return output_dir.expanduser().resolve()

    if IS_WINDOWS:
        raise ByggeError(
            "The --output-dir option is required on Windows "
            + "(no standard location for user-installed executables exists)"
        )
    else:
        return (Path.home() / ".local" / "bin").resolve()


def discover_scripts(workspace: Workspace) -> dict[str, Path]:
    """Find all [project.scripts] entries across pyproject.toml files in the workspace.

    Returns a dict mapping script name to its expected binary path in the venv.
    """
    bin_dir = workspace.venv_dir / "Scripts" if IS_WINDOWS else workspace.venv_dir / "bin"
    ext = ".exe" if IS_WINDOWS else ""

    scripts: dict[str, Path] = {}

    for dir, file_names in walk_dir(workspace.workspace_dir):
        if PYPROJECT_FILE_NAME not in file_names:
            continue

        pyproject_path = dir / PYPROJECT_FILE_NAME
        blob = load_toml(pyproject_path)
        scripts_node = try_dict(query_toml(blob, "project.scripts"))
        if scripts_node is None:
            continue

        for name in scripts_node:
            target = bin_dir / (name + ext)
            scripts[name] = target

    return scripts
