from __future__ import annotations

from pathlib import Path

import orjson

from claude_code_py.models.messages import Message, ToolResult


class TranscriptStore:
    def __init__(self, session_file: Path) -> None:
        self.session_file = session_file
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

    def append_message(self, message: Message) -> None:
        self._append({"type": "message", **message.model_dump()})

    def append_tool_result(self, result: ToolResult) -> None:
        self._append({"type": "tool_result", **result.model_dump()})

    def _append(self, payload: dict) -> None:
        with self.session_file.open("ab") as fh:
            fh.write(orjson.dumps(payload))
            fh.write(b"\n")
