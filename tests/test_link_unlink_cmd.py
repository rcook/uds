from __future__ import annotations

import os
from pathlib import Path

from pytest import CaptureFixture, MonkeyPatch, raises

from bygge import ByggeError
from bygge.cmd.link_cmd import link
from bygge.cmd.link_util import discover_scripts, resolve_output_dir
from bygge.cmd.unlink_cmd import unlink
from bygge.constants import IS_WINDOWS
from bygge.workspace import Workspace


def test_resolve_output_dir_explicit(tmp_path: Path) -> None:
    """Test explicit output directory resolution."""
    result = resolve_output_dir(tmp_path / "custom")
    assert result == (tmp_path / "custom").resolve()


def test_resolve_output_dir_default_posix() -> None:
    """Test default output directory resolution on POSIX."""
    if IS_WINDOWS:
        return  # Skip on Windows

    result = resolve_output_dir(None)
    assert result == (Path.home() / ".local" / "bin").resolve()


def test_resolve_output_dir_default_windows() -> None:
    """Test that default output directory is required on Windows."""
    if not IS_WINDOWS:
        return  # Skip on non-Windows

    with raises(ByggeError, match="--output-dir option is required on Windows"):
        _ = resolve_output_dir(None)


def test_resolve_output_dir_windows_error_mocked(monkeypatch: MonkeyPatch) -> None:
    """Test that default output directory raises error on Windows (via mock)."""
    import bygge.cmd.link_util

    monkeypatch.setattr(bygge.cmd.link_util, "IS_WINDOWS", True)

    with raises(ByggeError, match="--output-dir option is required on Windows"):
        _ = resolve_output_dir(None)


def test_discover_scripts_empty(tmp_workspace: Workspace) -> None:
    """Test that discover_scripts returns empty when no scripts defined."""
    scripts = discover_scripts(tmp_workspace)
    assert scripts == {}


def test_discover_scripts_finds_project_scripts(
    tmp_workspace: Workspace, tmp_workspace_dir: Path
) -> None:
    """Test that discover_scripts finds [project.scripts] entries."""
    pkg_dir = tmp_workspace_dir / "packages" / "my_pkg"
    pkg_dir.mkdir(parents=True)
    pyproject = pkg_dir / "pyproject.toml"
    _ = pyproject.write_text(
        "[project]\n"
        + 'name = "my_pkg"\n'
        + 'version = "0.1.0"\n'
        + "\n"
        + "[project.scripts]\n"
        + 'my-tool = "my_pkg:main"\n'
        + 'another-tool = "my_pkg:other"\n'
    )

    scripts = discover_scripts(tmp_workspace)
    assert "my-tool" in scripts
    assert "another-tool" in scripts

    ext = ".exe" if IS_WINDOWS else ""
    bin_dir = (
        tmp_workspace_dir / ".venv" / "Scripts"
        if IS_WINDOWS
        else tmp_workspace_dir / ".venv" / "bin"
    )
    assert scripts["my-tool"] == bin_dir / f"my-tool{ext}"
    assert scripts["another-tool"] == bin_dir / f"another-tool{ext}"


def test_discover_scripts_multiple_pyproject_files(
    tmp_workspace: Workspace, tmp_workspace_dir: Path
) -> None:
    """Test that discover_scripts finds scripts from multiple pyproject.toml files."""
    pkg1 = tmp_workspace_dir / "packages" / "pkg1"
    pkg1.mkdir(parents=True)
    _ = (pkg1 / "pyproject.toml").write_text(
        '[project]\nname = "pkg1"\n\n[project.scripts]\ntool1 = "pkg1:main"\n'
    )

    pkg2 = tmp_workspace_dir / "packages" / "pkg2"
    pkg2.mkdir(parents=True)
    _ = (pkg2 / "pyproject.toml").write_text(
        '[project]\nname = "pkg2"\n\n[project.scripts]\ntool2 = "pkg2:main"\n'
    )

    scripts = discover_scripts(tmp_workspace)
    assert "tool1" in scripts
    assert "tool2" in scripts


def test_discover_scripts_skips_venv(tmp_workspace: Workspace, tmp_workspace_dir: Path) -> None:
    """Test that discover_scripts skips pyproject.toml inside .venv."""
    # Create a pyproject.toml inside .venv (should be ignored)
    venv_pyproject = tmp_workspace_dir / ".venv" / "lib" / "site-packages" / "some_pkg"
    venv_pyproject.mkdir(parents=True)
    _ = (venv_pyproject / "pyproject.toml").write_text(
        '[project]\nname = "venv-pkg"\n\n[project.scripts]\nvenv-tool = "venv_pkg:main"\n'
    )

    # Create a valid pyproject.toml outside .venv
    pkg_dir = tmp_workspace_dir / "packages" / "real_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "real_pkg"\n\n[project.scripts]\nreal-tool = "real_pkg:main"\n'
    )

    scripts = discover_scripts(tmp_workspace)
    assert "real-tool" in scripts
    assert "venv-tool" not in scripts


def test_discover_scripts_skips_pyproject_without_scripts(
    tmp_workspace: Workspace, tmp_workspace_dir: Path
) -> None:
    """Test that discover_scripts skips pyproject.toml without [project.scripts]."""
    # Create a pyproject.toml without [project.scripts]
    pkg1 = tmp_workspace_dir / "packages" / "no_scripts"
    pkg1.mkdir(parents=True)
    _ = (pkg1 / "pyproject.toml").write_text('[project]\nname = "no_scripts"\nversion = "0.1.0"\n')

    # Create a pyproject.toml with scripts
    pkg2 = tmp_workspace_dir / "packages" / "with_scripts"
    pkg2.mkdir(parents=True)
    _ = (pkg2 / "pyproject.toml").write_text(
        '[project]\nname = "with_scripts"\n\n[project.scripts]\ntool = "pkg:main"\n'
    )

    scripts = discover_scripts(tmp_workspace)
    assert "tool" in scripts
    assert len(scripts) == 1


def test_link_creates_symlink(
    tmp_workspace: Workspace, tmp_workspace_dir: Path, tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Test that link creates symlinks in the output directory."""
    if IS_WINDOWS:
        return  # Skip on Windows (separate test for .cmd wrappers)

    output_dir = tmp_path / "output"
    pkg_dir = tmp_workspace_dir / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_pkg"\n\n[project.scripts]\nmy-script = "test_pkg:main"\n'
    )

    # Create dummy binary in venv
    venv_bin = tmp_workspace_dir / ".venv" / "bin"
    binary_path = venv_bin / "my-script"
    binary_path.touch()

    link(workspace=tmp_workspace, output_dir=output_dir, force=False)

    captured = capsys.readouterr()
    assert "creating symlink" in captured.out
    assert "my-script" in captured.out

    link_path = output_dir / "my-script"
    assert link_path.is_symlink()
    assert Path(os.readlink(link_path)) == binary_path


def test_link_unchanged_when_matching(
    tmp_workspace: Workspace, tmp_workspace_dir: Path, tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Test unchanged detection when symlink already correct."""
    if IS_WINDOWS:
        return  # Skip on Windows

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    pkg_dir = tmp_workspace_dir / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_pkg"\n\n[project.scripts]\nmy-script = "test_pkg:main"\n'
    )

    venv_bin = tmp_workspace_dir / ".venv" / "bin"
    binary_path = venv_bin / "my-script"
    binary_path.touch()

    # Create the correct symlink manually
    link_path = output_dir / "my-script"
    link_path.symlink_to(binary_path)

    link(workspace=tmp_workspace, output_dir=output_dir, force=False)

    captured = capsys.readouterr()
    assert "unchanged" in captured.out


def test_link_warns_on_conflict(
    tmp_workspace: Workspace, tmp_workspace_dir: Path, tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Test warning when existing link differs without --force."""
    if IS_WINDOWS:
        return  # Skip on Windows

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    pkg_dir = tmp_workspace_dir / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_pkg"\n\n[project.scripts]\nmy-script = "test_pkg:main"\n'
    )

    venv_bin = tmp_workspace_dir / ".venv" / "bin"
    binary_path = venv_bin / "my-script"
    binary_path.touch()

    # Create a different symlink
    link_path = output_dir / "my-script"
    different_target = tmp_path / "different"
    different_target.touch()
    link_path.symlink_to(different_target)

    link(workspace=tmp_workspace, output_dir=output_dir, force=False)

    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "already exists and differs" in captured.out

    # Should not have changed the symlink
    assert Path(os.readlink(link_path)) == different_target


def test_link_force_overrides(
    tmp_workspace: Workspace, tmp_workspace_dir: Path, tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Test that --force replaces differing links."""
    if IS_WINDOWS:
        return  # Skip on Windows

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    pkg_dir = tmp_workspace_dir / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_pkg"\n\n[project.scripts]\nmy-script = "test_pkg:main"\n'
    )

    venv_bin = tmp_workspace_dir / ".venv" / "bin"
    binary_path = venv_bin / "my-script"
    binary_path.touch()

    # Create a different symlink
    link_path = output_dir / "my-script"
    different_target = tmp_path / "different"
    different_target.touch()
    link_path.symlink_to(different_target)

    link(workspace=tmp_workspace, output_dir=output_dir, force=True)

    captured = capsys.readouterr()
    assert "creating symlink" in captured.out

    # Should have replaced the symlink
    assert Path(os.readlink(link_path)) == binary_path


def test_link_no_scripts_message(
    tmp_workspace: Workspace, capsys: CaptureFixture[str], tmp_path: Path
) -> None:
    """Test message when no scripts found."""
    link(workspace=tmp_workspace, output_dir=tmp_path / "output", force=False)

    captured = capsys.readouterr()
    assert "No scripts found" in captured.out


def test_unlink_removes_matching_symlink(
    tmp_workspace: Workspace, tmp_workspace_dir: Path, tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Test that unlink removes matching symlinks."""
    if IS_WINDOWS:
        return  # Skip on Windows

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    pkg_dir = tmp_workspace_dir / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_pkg"\n\n[project.scripts]\nmy-script = "test_pkg:main"\n'
    )

    venv_bin = tmp_workspace_dir / ".venv" / "bin"
    binary_path = venv_bin / "my-script"
    binary_path.touch()

    # Create the symlink
    link_path = output_dir / "my-script"
    link_path.symlink_to(binary_path)
    assert link_path.is_symlink()

    unlink(workspace=tmp_workspace, output_dir=output_dir)

    captured = capsys.readouterr()
    assert "removed" in captured.out
    assert not link_path.exists()


def test_unlink_not_found(
    tmp_workspace: Workspace, tmp_workspace_dir: Path, tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Test unlink message when symlink not present."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    pkg_dir = tmp_workspace_dir / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_pkg"\n\n[project.scripts]\nmy-script = "test_pkg:main"\n'
    )

    unlink(workspace=tmp_workspace, output_dir=output_dir)

    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_unlink_skips_non_bygge_symlink(
    tmp_workspace: Workspace, tmp_workspace_dir: Path, tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Test that unlink skips symlinks not created by bygge."""
    if IS_WINDOWS:
        return  # Skip on Windows

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    pkg_dir = tmp_workspace_dir / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_pkg"\n\n[project.scripts]\nmy-script = "test_pkg:main"\n'
    )

    # Create a symlink pointing to a different target
    link_path = output_dir / "my-script"
    different_target = tmp_path / "different"
    different_target.touch()
    link_path.symlink_to(different_target)

    unlink(workspace=tmp_workspace, output_dir=output_dir)

    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "not installed by bygge" in captured.out

    # Should not have removed the symlink
    assert link_path.is_symlink()
    assert Path(os.readlink(link_path)) == different_target


def test_unlink_output_dir_does_not_exist(tmp_workspace: Workspace, tmp_path: Path) -> None:
    """Test that unlink raises error when output dir doesn't exist."""
    non_existent = tmp_path / "does_not_exist"

    with raises(ByggeError, match="does not exist"):
        unlink(workspace=tmp_workspace, output_dir=non_existent)


def test_unlink_no_scripts_message(
    tmp_workspace: Workspace, capsys: CaptureFixture[str], tmp_path: Path
) -> None:
    """Test message when no scripts found during unlink."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    unlink(workspace=tmp_workspace, output_dir=output_dir)

    captured = capsys.readouterr()
    assert "No scripts found" in captured.out


def test_link_creates_windows_wrapper(
    tmp_workspace: Workspace,
    tmp_workspace_dir: Path,
    tmp_path: Path,
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    """Test that link creates .cmd wrappers on Windows."""
    # Mock IS_WINDOWS in all modules
    import bygge.cmd.link_cmd
    import bygge.cmd.link_util

    monkeypatch.setattr(bygge.cmd.link_util, "IS_WINDOWS", True)
    monkeypatch.setattr(bygge.cmd.link_cmd, "IS_WINDOWS", True)

    output_dir = tmp_path / "output"
    pkg_dir = tmp_workspace_dir / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_pkg"\n\n[project.scripts]\nmy-script = "test_pkg:main"\n'
    )

    # Create dummy binary in venv Scripts directory
    venv_scripts = tmp_workspace_dir / ".venv" / "Scripts"
    venv_scripts.mkdir(exist_ok=True)
    binary_path = venv_scripts / "my-script.exe"
    binary_path.touch()

    # Mock discover_scripts to return Windows-style path

    def mock_discover(_workspace: Workspace) -> dict[str, Path]:
        return {"my-script": binary_path}

    monkeypatch.setattr(bygge.cmd.link_util, "discover_scripts", mock_discover)

    link(workspace=tmp_workspace, output_dir=output_dir, force=False)

    captured = capsys.readouterr()
    assert "creating wrapper script" in captured.out

    wrapper_path = output_dir / "my-script.cmd"
    assert wrapper_path.exists()
    content = wrapper_path.read_text()
    assert f"@echo off\n{binary_path} %*\nexit /b %errorlevel%\n" == content


def test_link_windows_wrapper_unchanged(
    tmp_workspace: Workspace,
    tmp_workspace_dir: Path,
    tmp_path: Path,
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    """Test unchanged detection for Windows .cmd wrappers."""
    import bygge.cmd.link_cmd
    import bygge.cmd.link_util

    monkeypatch.setattr(bygge.cmd.link_util, "IS_WINDOWS", True)
    monkeypatch.setattr(bygge.cmd.link_cmd, "IS_WINDOWS", True)

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    pkg_dir = tmp_workspace_dir / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_pkg"\n\n[project.scripts]\nmy-script = "test_pkg:main"\n'
    )

    venv_scripts = tmp_workspace_dir / ".venv" / "Scripts"
    venv_scripts.mkdir(exist_ok=True)
    binary_path = venv_scripts / "my-script.exe"
    binary_path.touch()

    def mock_discover(_workspace: Workspace) -> dict[str, Path]:
        return {"my-script": binary_path}

    monkeypatch.setattr(bygge.cmd.link_util, "discover_scripts", mock_discover)

    # Create the correct wrapper manually
    wrapper_path = output_dir / "my-script.cmd"
    _ = wrapper_path.write_text(f"@echo off\n{binary_path} %*\nexit /b %errorlevel%\n")

    link(workspace=tmp_workspace, output_dir=output_dir, force=False)

    captured = capsys.readouterr()
    assert "unchanged" in captured.out


def test_link_windows_wrapper_conflict(
    tmp_workspace: Workspace,
    tmp_workspace_dir: Path,
    tmp_path: Path,
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    """Test conflict detection for Windows .cmd wrappers."""
    import bygge.cmd.link_cmd
    import bygge.cmd.link_util

    monkeypatch.setattr(bygge.cmd.link_util, "IS_WINDOWS", True)
    monkeypatch.setattr(bygge.cmd.link_cmd, "IS_WINDOWS", True)

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    pkg_dir = tmp_workspace_dir / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_pkg"\n\n[project.scripts]\nmy-script = "test_pkg:main"\n'
    )

    venv_scripts = tmp_workspace_dir / ".venv" / "Scripts"
    venv_scripts.mkdir(exist_ok=True)
    binary_path = venv_scripts / "my-script.exe"
    binary_path.touch()

    def mock_discover(_workspace: Workspace) -> dict[str, Path]:
        return {"my-script": binary_path}

    monkeypatch.setattr(bygge.cmd.link_util, "discover_scripts", mock_discover)

    # Create a different wrapper
    wrapper_path = output_dir / "my-script.cmd"
    _ = wrapper_path.write_text("@echo off\necho different\n")

    link(workspace=tmp_workspace, output_dir=output_dir, force=False)

    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "already exists and differs" in captured.out

    # Should not have changed
    assert "echo different" in wrapper_path.read_text()


def test_unlink_removes_windows_wrapper(
    tmp_workspace: Workspace,
    tmp_workspace_dir: Path,
    tmp_path: Path,
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    """Test that unlink removes Windows .cmd wrappers."""
    import bygge.cmd.link_util
    import bygge.cmd.unlink_cmd

    monkeypatch.setattr(bygge.cmd.link_util, "IS_WINDOWS", True)
    monkeypatch.setattr(bygge.cmd.unlink_cmd, "IS_WINDOWS", True)

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    pkg_dir = tmp_workspace_dir / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_pkg"\n\n[project.scripts]\nmy-script = "test_pkg:main"\n'
    )

    venv_scripts = tmp_workspace_dir / ".venv" / "Scripts"
    venv_scripts.mkdir(exist_ok=True)
    binary_path = venv_scripts / "my-script.exe"
    binary_path.touch()

    def mock_discover(_workspace: Workspace) -> dict[str, Path]:
        return {"my-script": binary_path}

    monkeypatch.setattr(bygge.cmd.link_util, "discover_scripts", mock_discover)
    # discover_scripts is already patched in link_util above

    # Create the wrapper
    wrapper_path = output_dir / "my-script.cmd"
    _ = wrapper_path.write_text(f"@echo off\n{binary_path} %*\nexit /b %errorlevel%\n")
    assert wrapper_path.exists()

    unlink(workspace=tmp_workspace, output_dir=output_dir)

    captured = capsys.readouterr()
    assert "removed" in captured.out
    assert not wrapper_path.exists()


def test_unlink_skips_different_windows_wrapper(
    tmp_workspace: Workspace,
    tmp_workspace_dir: Path,
    tmp_path: Path,
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    """Test that unlink skips .cmd wrappers not created by bygge."""
    import bygge.cmd.link_util
    import bygge.cmd.unlink_cmd

    monkeypatch.setattr(bygge.cmd.link_util, "IS_WINDOWS", True)
    monkeypatch.setattr(bygge.cmd.unlink_cmd, "IS_WINDOWS", True)

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    pkg_dir = tmp_workspace_dir / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_pkg"\n\n[project.scripts]\nmy-script = "test_pkg:main"\n'
    )

    venv_scripts = tmp_workspace_dir / ".venv" / "Scripts"
    venv_scripts.mkdir(exist_ok=True)
    binary_path = venv_scripts / "my-script.exe"
    binary_path.touch()

    def mock_discover(_workspace: Workspace) -> dict[str, Path]:
        return {"my-script": binary_path}

    monkeypatch.setattr(bygge.cmd.link_util, "discover_scripts", mock_discover)
    # discover_scripts is already patched in link_util above

    # Create a different wrapper
    wrapper_path = output_dir / "my-script.cmd"
    _ = wrapper_path.write_text("@echo off\necho different\n")

    unlink(workspace=tmp_workspace, output_dir=output_dir)

    captured = capsys.readouterr()
    assert "WARNING" in captured.out
    assert "not installed by bygge" in captured.out

    # Should not have removed
    assert wrapper_path.exists()


def test_unlink_windows_wrapper_not_found(
    tmp_workspace: Workspace,
    tmp_workspace_dir: Path,
    tmp_path: Path,
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    """Test unlink message when Windows wrapper not present."""
    import bygge.cmd.link_util
    import bygge.cmd.unlink_cmd

    monkeypatch.setattr(bygge.cmd.link_util, "IS_WINDOWS", True)
    monkeypatch.setattr(bygge.cmd.unlink_cmd, "IS_WINDOWS", True)

    output_dir = tmp_path / "output"
    output_dir.mkdir()

    pkg_dir = tmp_workspace_dir / "packages" / "test_pkg"
    pkg_dir.mkdir(parents=True)
    _ = (pkg_dir / "pyproject.toml").write_text(
        '[project]\nname = "test_pkg"\n\n[project.scripts]\nmy-script = "test_pkg:main"\n'
    )

    venv_scripts = tmp_workspace_dir / ".venv" / "Scripts"
    venv_scripts.mkdir(exist_ok=True)
    binary_path = venv_scripts / "my-script.exe"
    binary_path.touch()

    def mock_discover(_workspace: Workspace) -> dict[str, Path]:
        return {"my-script": binary_path}

    monkeypatch.setattr(bygge.cmd.link_util, "discover_scripts", mock_discover)
    # discover_scripts is already patched in link_util above

    unlink(workspace=tmp_workspace, output_dir=output_dir)

    captured = capsys.readouterr()
    assert "not found" in captured.out
