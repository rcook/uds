from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import override

import click
from click import Command, Context, Parameter, ParamType, argument, option

from .unset import UNSET, Unset

type ClickDecorator = Callable[[Command | Callable[..., object]], Command | Callable[..., object]]


CWD_OPT: ClickDecorator = option(
    "-C",
    "cwd",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True, path_type=Path),
    default=Path.cwd(),
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
