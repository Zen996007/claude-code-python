from __future__ import annotations

import asyncio

from pydantic import BaseModel

from claude_code_py.tools.base import Tool, ToolContext


class BashInput(BaseModel):
    command: str


class BashTool(Tool):
    name = "bash"
    description = "Run a shell command in the working directory"
    input_model = BashInput

    async def run(self, data: BashInput, context: ToolContext) -> str:
        process = await asyncio.create_subprocess_shell(
            data.command,
            cwd=str(context.cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        output = stdout.decode() + stderr.decode()
        return output.strip() or f"Exit code: {process.returncode}"
