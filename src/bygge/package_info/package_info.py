from __future__ import annotations

from dataclasses import dataclass
from logging import debug
from pathlib import Path
from typing import Self

from bygge.contracts import (
    CoveragePlugin,
    DeadCodePlugin,
    FormatPlugin,
    Input,
    LintPlugin,
    Payload,
    TestPlugin,
    TypeCheckPlugin,
)
from bygge.plugins import Plugins
from bygge.util import TomlValue, query_toml, try_dict, try_str

from .context import Context
from .plugin_info import PluginInfo


@dataclass(frozen=True, slots=True)
class SkinnyContext:
    plugins: Plugins
    input: Input
    blob: TomlValue

    def get_name(self) -> str | None:
        return try_str(query_toml(self.blob, "project.name"))

    def get_source_dirs(self) -> list[Path] | None:
        source_dirs = None
        for f in self.plugins.source_dir_plugins:
            temp = f.fetch_source_dirs(input=self.input, blob=self.blob)
            count = 0 if temp is None else len(temp)
            debug(f"Plugin {type(f).__name__}: found {count} source directories")
            if temp is not None and source_dirs is None:
                source_dirs = temp
        return source_dirs

    def get_test_dirs(self) -> list[Path] | None:
        test_dirs = None
        for f in self.plugins.test_dir_plugins:
            temp = f.fetch_test_dirs(input=self.input, blob=self.blob)
            count = 0 if temp is None else len(temp)
            debug(f"Plugin {type(f).__name__}: found {count} test directories")
            if temp is not None and test_dirs is None:
                test_dirs = temp
        return test_dirs


@dataclass(frozen=True, slots=True)
class PackageInfo:
    name: str
    test: PluginInfo[TestPlugin] | None
    coverage: PluginInfo[CoveragePlugin] | None
    type_check: PluginInfo[TypeCheckPlugin] | None
    format: PluginInfo[FormatPlugin] | None
    lint: PluginInfo[LintPlugin] | None
    dead_code: PluginInfo[DeadCodePlugin] | None

    @classmethod
    def make(cls: type[Self], plugins: Plugins, input: Input) -> Self | None:
        obj = try_dict(input.blob)
        if obj is None:  # pragma: no cover - TOML root is always a dict
            return None

        skinny_ctx = SkinnyContext(plugins=plugins, input=input, blob=obj)

        name = skinny_ctx.get_name()
        if name is None:
            return None

        source_dirs = skinny_ctx.get_source_dirs()
        if source_dirs is None:
            return None

        test_dirs = skinny_ctx.get_test_dirs() or []

        payload = Payload(source_dirs=source_dirs, test_dirs=test_dirs)

        ctx = Context(
            plugins=skinny_ctx.plugins,
            input=skinny_ctx.input,
            blob=skinny_ctx.blob,
            payload=payload,
        )

        return cls(
            name=name,
            test=PluginInfo[TestPlugin].find(ctx=ctx, plugins=ctx.plugins.test_plugins),
            coverage=PluginInfo[CoveragePlugin].find(ctx=ctx, plugins=ctx.plugins.coverage_plugins),
            type_check=PluginInfo[TypeCheckPlugin].find(
                ctx=ctx, plugins=ctx.plugins.type_check_plugins
            ),
            format=PluginInfo[FormatPlugin].find(ctx=ctx, plugins=ctx.plugins.format_plugins),
            lint=PluginInfo[LintPlugin].find(ctx=ctx, plugins=ctx.plugins.lint_plugins),
            dead_code=PluginInfo[DeadCodePlugin].find(
                ctx=ctx, plugins=ctx.plugins.dead_code_plugins
            ),
        )
