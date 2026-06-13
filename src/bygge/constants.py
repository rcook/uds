from __future__ import annotations

import re
import sys
from pathlib import Path
from platform import system
from re import Pattern

BOOTSTRAP_PYTHON_PATH: Path = Path(sys.executable)

IS_WINDOWS = system().lower() == "windows"

IGNORE_DIR_NAMES: set[str] = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    ".venv",
    "htmlcov",
}

PYPROJECT_FILE_NAME: str = "pyproject.toml"

VENV_DIR_NAME: str = ".venv"

REQUIREMENTS_PATTERN: Pattern[str] = re.compile("^(.*)requirements(.*).txt$")

DOT_FILE_NAME: str = ".bygge.toml"
