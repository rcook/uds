from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from bygge.cmd import recode
from bygge.workspace import Workspace

_RESOURCE_DIR: Path = Path(__file__).parent / "resources"


def test_recode_basics(tmp_workspace: Path) -> None:
    @dataclass(frozen=True, slots=True)
    class FileInfo:
        input_bytes: bytes
        output_bytes: bytes
        test_path: Path

    workspace = Workspace.find(cwd=tmp_workspace, workspace_dir=None)

    files: list[FileInfo] = []
    for i in range(3):
        input_file_name = f"example{i}-input.txt"
        input_path = _RESOURCE_DIR / input_file_name
        output_file_name = f"example{i}-output.txt"
        output_path = _RESOURCE_DIR / output_file_name

        test_path = tmp_workspace / f"{input_file_name}.py"
        _ = shutil.copyfile(input_path, test_path)
        files.append(
            FileInfo(
                input_bytes=input_path.read_bytes(),
                output_bytes=output_path.read_bytes(),
                test_path=test_path,
            )
        )

    file0 = files[0]
    file1 = files[1]
    file2 = files[2]

    recode(workspace=workspace, fix=True)

    assert file0.test_path.read_bytes() == file0.output_bytes
    assert file1.test_path.read_bytes() == file1.output_bytes
    assert file2.test_path.read_bytes() == file2.output_bytes
