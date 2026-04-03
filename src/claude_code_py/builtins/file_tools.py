from __future__ import annotations

from pydantic import BaseModel

from claude_code_py.tools.base import Tool, ToolContext


class FileReadInput(BaseModel):
    path: str


class FileWriteInput(BaseModel):
    path: str
    content: str


class FileEditInput(BaseModel):
    path: str
    old: str
    new: str


class ListDirectoryInput(BaseModel):
    path: str = "."


class FileReadTool(Tool):
    name = "file_read"
    description = "Read a UTF-8 text file"
    input_model = FileReadInput
    tags = ("read", "filesystem")

    def is_concurrency_safe(self, data: BaseModel) -> bool:
        return True

    async def run(self, data: FileReadInput, context: ToolContext) -> str:
        return context.resolve_path(data.path).read_text(encoding="utf-8")


class FileWriteTool(Tool):
    name = "file_write"
    description = "Write a UTF-8 text file"
    input_model = FileWriteInput
    tags = ("write", "filesystem")

    async def run(self, data: FileWriteInput, context: ToolContext) -> str:
        target = context.resolve_path(data.path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data.content, encoding="utf-8")
        return f"Wrote {target}"


class FileEditTool(Tool):
    name = "file_edit"
    description = "Exact string replacement in a file"
    input_model = FileEditInput
    tags = ("write", "filesystem")

    async def run(self, data: FileEditInput, context: ToolContext) -> str:
        target = context.resolve_path(data.path)
        content = target.read_text(encoding="utf-8")
        if data.old not in content:
            raise ValueError("old text not found")
        target.write_text(content.replace(data.old, data.new, 1), encoding="utf-8")
        return f"Edited {target}"


class ListDirectoryTool(Tool):
    name = "file_list"
    description = "List files in a directory"
    input_model = ListDirectoryInput
    tags = ("read", "filesystem")

    def is_concurrency_safe(self, data: BaseModel) -> bool:
        return True

    async def run(self, data: ListDirectoryInput, context: ToolContext) -> str:
        target = context.resolve_path(data.path)
        if not target.is_dir():
            raise ValueError(f"Not a directory: {data.path}")
        entries = sorted(
            f"{'dir' if entry.is_dir() else 'file'}\t{entry.relative_to(context.cwd.resolve())}"
            for entry in target.iterdir()
        )
        return "\n".join(entries)
