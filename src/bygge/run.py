from __future__ import annotations

import logging
import shlex
import subprocess
from logging import debug
from pathlib import Path
from subprocess import CompletedProcess


def run_subprocess(cmd: list[str], cwd: Path, check: bool, yes: bool) -> CompletedProcess[str]:
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        for c in cmd:
            debug(c)
        debug({"cmd": shlex.join(cmd), "cwd": str(cwd), "check": str(check).lower()})
    if yes:
        return subprocess.run(cmd, cwd=cwd, check=check, text=True)
    else:
        return CompletedProcess(args=cwd, returncode=0)
