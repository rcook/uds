from __future__ import annotations

from logging import Formatter, LogRecord
from typing import override

import click


class ColourFormatter(Formatter):
    @override
    def format(self, record: LogRecord) -> str:
        message = super().format(record)
        match record.levelname:
            case "INFO":
                return click.style(message, fg="green")
            case "WARNING":
                return click.style(message, fg="yellow")
            case "ERROR":
                return click.style(message, fg="red")
            case "DEBUG":
                return click.style(message, fg="cyan")
            case _:
                return message
