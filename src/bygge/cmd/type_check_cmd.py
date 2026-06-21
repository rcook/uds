from __future__ import annotations

from bygge import ByggeError
from bygge.workspace import Workspace

from .constants import PLUGINS
from .plugin_runner import PluginRunner


def type_check(workspace: Workspace, args: tuple[str, ...]) -> None:
    runner = PluginRunner(workspace=workspace, plugins=PLUGINS)
    result = runner.run_type_check(args=args)
    if not result.ran:
        raise ByggeError("No type check plugin found")
    if not result.succeeded:
        raise ByggeError("Type check run failed")
