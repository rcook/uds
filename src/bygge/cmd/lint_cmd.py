from __future__ import annotations

from bygge import ByggeError
from bygge.cmd.constants import PLUGINS
from bygge.cmd.plugin_runner import PluginRunner
from bygge.workspace import Workspace


def lint(workspace: Workspace, fix: bool, args: tuple[str, ...]) -> None:
    runner = PluginRunner(workspace=workspace, plugins=PLUGINS)
    result = runner.run_lint(fix=fix, args=args)
    if not result.ran:
        raise ByggeError("No lint plugin found")
    if not result.succeeded:  # pragma: nocover
        raise ByggeError("Lint run failed")
