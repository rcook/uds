from __future__ import annotations

from bygge.contracts import Input, Payload, ToolResult
from bygge.run import run_subprocess
from bygge.util import TomlValue
from bygge.workspace import Workspace

from .test_dirs_mixin import TestDirsMixin
from .util import get_requirements


class Basedpyright(TestDirsMixin):
    def is_installed(self, input: Input, blob: TomlValue) -> bool:
        requirements = get_requirements(input=input, blob=blob)
        return any(map(lambda req: req.name == "basedpyright", requirements))

    def run_type_check(
        self,
        workspace: Workspace,
        payload: Payload,
        args: tuple[str, ...],
    ) -> ToolResult:
        cmd = [
            str(workspace.make_bin_path("basedpyright")),
            *[str(p) for p in payload.source_dirs],
            *[str(p) for p in payload.test_dirs],
            "--pythonpath",
            str(workspace.make_bin_path("python")),
            "--stats",
            *args,
        ]

        proc = run_subprocess(cmd=cmd, cwd=workspace.cwd, check=False, yes=True)
        match proc.returncode:
            case 0:
                # basedpyright completed successfully: no type errors
                return ToolResult.TEST_PASSED
            case 1:
                # basedpyright completed successfully: some type errors were detected
                return ToolResult.TEST_FAILED
            case 3:  # pragma: nocover
                # basedpyright reported bad configuration etc.
                return ToolResult.TOOL_ERROR
            case _:  # pragma: nocover
                proc.check_returncode()
                raise AssertionError()
