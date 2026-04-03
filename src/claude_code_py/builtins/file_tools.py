from __future__ import annotations

from pathlib import Path

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


class FileReadTool(Tool):
    name = "file_read"
    description = "Read a UTF-8 text file"
    input_model = FileReadInput

    def is_concurrency_safe(self, data: BaseModel) -> bool:
        return True

    async def run(self, data: FileReadInput, context: ToolContext) -> str:
        return (context.cwd / data.path).read_text()


class FileWriteTool(Tool):
    name = "file_write"
    description = "Write a UTF-8 text file"
    input_model = FileWriteInput

    async def run(self, data: FileWriteInput, context: ToolContext) -> str:
        target = context.cwd / data.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(data.content)
        return f"Wrote {target}"


class FileEditTool(Tool):
    name = "file_edit"
    description = "Exact string replacement in a file"
    input_model = FileEditInput

    async def run(self, data: FileEditInput, context: ToolContext) -> str:
        target = context.cwd / data.path
        content = target.read_text()
        if data.old not in content:
            raise ValueError("old text not found")
        target.write_text(content.replace(data.old, data.new, 1))
        return f"Edited {target}"
