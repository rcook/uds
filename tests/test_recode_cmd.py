from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from bygge.cmd.recode_cmd import recode

_RESOURCE_DIR: Path = Path(__file__).parent / "resources"


# @pytest.mark.parametrize()
def test_recode_basics(tmp_path: Path) -> None:
    @dataclass(frozen=True, slots=True)
    class FileInfo:
        input_bytes: bytes
        output_bytes: bytes
        test_path: Path

    files: list[FileInfo] = []
    for i in range(3):
        input_file_name = f"example{i}-input.txt"
        input_path = _RESOURCE_DIR / input_file_name
        output_file_name = f"example{i}-output.txt"
        output_path = _RESOURCE_DIR / output_file_name

        test_path = tmp_path / input_file_name
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

    # Convert single file
    recode(file0.test_path)

    assert file0.test_path.read_bytes() == file0.output_bytes
    assert file1.test_path.read_bytes() == file1.input_bytes
    assert file2.test_path.read_bytes() == file2.input_bytes

    # Convert multiple files
    recode(tmp_path, suffix=".txt")

    assert file0.test_path.read_bytes() == file0.output_bytes
    assert file1.test_path.read_bytes() == file1.output_bytes
    assert file2.test_path.read_bytes() == file2.output_bytes
