from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import override

import click
from click import Command, Context, Parameter, ParamType, argument, option

from .unset import UNSET, Unset

type ClickDecorator = Callable[[Command | Callable[..., object]], Command | Callable[..., object]]


def _get_cwd(ctx: Context, param: Parameter, value: Path | None) -> Path:  # pyright: ignore[reportUnusedParameter]
    return Path.cwd() if value is None else value


CWD_OPT: ClickDecorator = option(
    "-C",
    "cwd",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True, path_type=Path),
    default=None,
    callback=_get_cwd,
    help="Working directory",
)

WORKSPACE_DIR_OPT: ClickDecorator = option(
    "-d",
    "workspace_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True, path_type=Path),
    default=None,
    help="Workspace directory",
)

YES_OPT: ClickDecorator = option(
    "--yes/--dry-run",
    "yes",
    type=bool,
    default=True,
    help="Perform the operation or perform a dry run",
)


ARGS_ARG: ClickDecorator = argument("args", nargs=-1, type=click.UNPROCESSED)


FIX_CHECK_OPT: ClickDecorator = option(
    "--fix/--check",
    type=bool,
    is_flag=True,
    default=True,
    help="Fix errors or check for errors only",
)

OUTPUT_DIR_OPT: ClickDecorator = option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, resolve_path=True, path_type=Path),
    default=None,
    help="Directory for script links (default: ~/.local/bin on POSIX, required on Windows)",
)


UNKNOWN_ARGS_CTX: dict[str, bool] = {"ignore_unknown_options": True, "allow_extra_args": True}


class NamedChoice[T](ParamType[T]):
    name: str = "namedchoice"

    def __init__(self, choices: Iterable[tuple[str, T]]) -> None:
        self._choices: dict[str, T] = dict(choices)
        self._labels: list[str] = list(self._choices.keys())

    @override
    def convert(self, value: str, param: Parameter | None, ctx: Context | None) -> T:
        converted_value = self._choices.get(value, UNSET)
        if not isinstance(converted_value, Unset):
            return converted_value
        self.fail(f"invalid choice: {value}. (choose from {', '.join(self._labels)})", param, ctx)

    @override
    def get_metavar(self, param: Parameter | None, ctx: Context | None) -> str:
        return f"[{'|'.join(self._labels)}]"

    @override
    def get_missing_message(self, param: Parameter | None, ctx: Context | None) -> str:
        return f"Choose from {', '.join(self._labels)}."
