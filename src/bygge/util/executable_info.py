from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Self

from .fs import hackily_canonicalize


@dataclass(frozen=True, slots=True)
class ExecutableInfo:
    executable_unresolved: Path
    executable_resolved: Path
    executable_linked: bool
    python_version: str
    argv0_unresolved: Path
    argv0_resolved: Path
    argv0_linked: bool
    is_python_script: bool

    @classmethod
    def make(cls: type[Self]) -> Self:
        executable_unresolved = Path(sys.executable)
        executable_resolved = executable_unresolved.resolve()
        executable_linked = executable_unresolved != executable_resolved

        python_version = sys.version.split()[0]

        # Check if running as a script (python main.py) or as installed binary (bygge)
        argv0_unresolved = hackily_canonicalize(sys.argv[0])
        argv0_resolved = argv0_unresolved.resolve()
        argv0_linked = argv0_unresolved != argv0_resolved

        # If argv[0] is a .py file, we're running as a script
        is_python_script = argv0_resolved.suffix == ".py"

        return cls(
            executable_unresolved=executable_unresolved,
            executable_resolved=executable_resolved,
            executable_linked=executable_linked,
            python_version=python_version,
            argv0_unresolved=argv0_unresolved,
            argv0_resolved=argv0_resolved,
            argv0_linked=argv0_linked,
            is_python_script=is_python_script,
        )
