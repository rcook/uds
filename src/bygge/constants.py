from __future__ import annotations

import re
import sys
from pathlib import Path
from platform import system
from re import Pattern

BOOTSTRAP_PYTHON_PATH: Path = Path(sys.executable)

IS_WINDOWS = system().lower() == "windows"

IGNORE_DIR_GLOBS: set[str] = {
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".vscode",
    "*.egg-info",
    "htmlcov",
}

TEST_DIRS: set[str] = {"test", "tests"}

PYPROJECT_FILE_NAME: str = "pyproject.toml"

VENV_DIR_NAME: str = ".venv"

REQUIREMENTS_PATTERN: Pattern[str] = re.compile("^(.*)requirements(.*).txt$")

DOT_FILE_NAME: str = ".bygge.toml"

INIT_FILE_NAME: str = "__init__.py"
