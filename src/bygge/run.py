from __future__ import annotations

import logging
import subprocess
from logging import debug
from pathlib import Path
from subprocess import CompletedProcess

from bygge.util.fs import shell_join


def run_subprocess(cmd: list[str], cwd: Path, check: bool, yes: bool) -> CompletedProcess[str]:
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        s = shell_join(cmd)
        debug(f"Command line: {s}")
        for i, c in enumerate(cmd):
            debug(f"cmd[{i}] = {c}")
        debug({"cwd": str(cwd), "check": str(check).lower()})
    if yes:
        return subprocess.run(cmd, cwd=cwd, check=check, text=True)
    else:
        return CompletedProcess(args=cwd, returncode=0)
