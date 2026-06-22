from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from pytest import raises

from bygge import ByggeError
from bygge.cmd import recode
from bygge.workspace import Workspace

_RESOURCE_DIR: Path = Path(__file__).parent / "resources"


def test_recode_fix(tmp_workspace_dir: Path) -> None:
    @dataclass(frozen=True, slots=True)
    class FileInfo:
        input_bytes: bytes
        output_bytes: bytes
        test_path: Path

    workspace = Workspace.open(tmp_workspace_dir)

    files: list[FileInfo] = []
    for i in range(3):
        input_file_name = f"example{i}-input.txt"
        input_path = _RESOURCE_DIR / input_file_name
        output_file_name = f"example{i}-output.txt"
        output_path = _RESOURCE_DIR / output_file_name

        test_path = tmp_workspace_dir / f"{input_file_name}.py"
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


def test_recode_check(tmp_workspace_dir: Path) -> None:
    @dataclass(frozen=True, slots=True)
    class FileInfo:
        input_bytes: bytes
        output_bytes: bytes
        test_path: Path

    workspace = Workspace.open(tmp_workspace_dir)

    files: list[FileInfo] = []
    for i in range(3):
        input_file_name = f"example{i}-input.txt"
        input_path = _RESOURCE_DIR / input_file_name
        output_file_name = f"example{i}-output.txt"
        output_path = _RESOURCE_DIR / output_file_name

        test_path = tmp_workspace_dir / f"{input_file_name}.py"
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

    with raises(ByggeError, match="Detected non-ASCII characters in 3 files"):
        recode(workspace=workspace, fix=False)

    assert file0.test_path.read_bytes() == file0.input_bytes
    assert file1.test_path.read_bytes() == file1.input_bytes
    assert file2.test_path.read_bytes() == file2.input_bytes
