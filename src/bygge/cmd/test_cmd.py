from __future__ import annotations

from bygge import ByggeError
from bygge.cmd.constants import PLUGINS
from bygge.workspace import Workspace

from .runner import Runner


def test(workspace: Workspace, args: tuple[str, ...]) -> None:
    runner = Runner(workspace=workspace, plugins=PLUGINS)
    result = runner.run_test(args)
    if not result.ran:
        raise ByggeError("No test tool found")
    if not result.succeeded:
        raise ByggeError("Test run failed")
