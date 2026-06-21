from __future__ import annotations

from bygge import ByggeError
from bygge.cmd.constants import PLUGINS
from bygge.workspace import Workspace

from .plugin_runner import PluginRunner


def test(workspace: Workspace, args: tuple[str, ...]) -> None:
    runner = PluginRunner(workspace=workspace, plugins=PLUGINS)
    result = runner.run_test(args)
    if not result.ran:
        raise ByggeError("No test plugin found")
    if not result.succeeded:
        raise ByggeError("Test run failed")
