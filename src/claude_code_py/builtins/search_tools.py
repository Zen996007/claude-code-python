from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path

from pydantic import BaseModel, Field

from claude_code_py.tools.base import Tool, ToolContext


def _matches(pattern: str, local_name: str, relative_name: str, basename: str) -> bool:
    patterns = [pattern]
    if pattern.startswith("**/"):
        patterns.append(pattern[3:])
    return any(
        fnmatch(local_name, item) or fnmatch(relative_name, item) or fnmatch(basename, item)
        for item in patterns
    )


class FileGlobInput(BaseModel):
    pattern: str = "**/*"
    base_path: str = "."
    include_hidden: bool = False
    directories: bool = False
    limit: int = Field(default=200, ge=1, le=2000)


class GrepSearchInput(BaseModel):
    pattern: str
    base_path: str = "."
    glob: str = "**/*"
    case_sensitive: bool = False
    limit: int = Field(default=100, ge=1, le=2000)


class FileGlobTool(Tool):
    name = "file_glob"
    description = "Find files or directories matching a glob pattern"
    input_model = FileGlobInput
    tags = ("read", "filesystem", "search")

    async def run(self, data: FileGlobInput, context: ToolContext) -> str:
        base = context.resolve_path(data.base_path)
        if not base.exists():
            raise ValueError(f"Path does not exist: {data.base_path}")
        items: list[str] = []
        for path in sorted(base.rglob("*")):
            relative = path.relative_to(context.cwd.resolve())
            if not data.include_hidden and any(part.startswith(".") for part in relative.parts):
                continue
            if path.is_dir() and not data.directories:
                continue
            local_name = path.relative_to(base).as_posix()
            if _matches(data.pattern, local_name, relative.as_posix(), path.name):
                prefix = "dir" if path.is_dir() else "file"
                items.append(f"{prefix}\t{relative}")
            if len(items) >= data.limit:
                break
        return "\n".join(items) if items else "No matches"


class GrepSearchTool(Tool):
    name = "grep_search"
    description = "Search text inside files under the working directory"
    input_model = GrepSearchInput
    tags = ("read", "filesystem", "search")

    async def run(self, data: GrepSearchInput, context: ToolContext) -> str:
        base = context.resolve_path(data.base_path)
        if not base.exists():
            raise ValueError(f"Path does not exist: {data.base_path}")
        needle = data.pattern if data.case_sensitive else data.pattern.lower()
        matches: list[str] = []
        for path in sorted(base.rglob("*")):
            if path.is_dir():
                continue
            relative = path.relative_to(context.cwd.resolve())
            local_name = path.relative_to(base).as_posix()
            if not _matches(data.glob, local_name, relative.as_posix(), path.name):
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for line_no, line in enumerate(content.splitlines(), start=1):
                haystack = line if data.case_sensitive else line.lower()
                if needle in haystack:
                    matches.append(f"{relative}:{line_no}: {line}")
                if len(matches) >= data.limit:
                    return "\n".join(matches)
        return "\n".join(matches) if matches else "No matches"
