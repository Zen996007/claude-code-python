from __future__ import annotations

import asyncio

from pydantic import BaseModel, Field

from claude_code_py.tools.base import Tool, ToolContext


class BashInput(BaseModel):
    command: str
    timeout_seconds: float = Field(default=30.0, gt=0)


class BashTool(Tool):
    name = "bash"
    description = "Run a shell command in the working directory"
    input_model = BashInput
    tags = ("shell", "process")

    async def run(self, data: BashInput, context: ToolContext) -> str:
        process = await asyncio.create_subprocess_shell(
            data.command,
            cwd=str(context.cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=data.timeout_seconds)
        except TimeoutError:
            process.kill()
            await process.communicate()
            raise TimeoutError(f"Command timed out after {data.timeout_seconds}s")
        output = (stdout.decode() + stderr.decode()).strip()
        if output:
            return output
        return f"Exit code: {process.returncode}"
