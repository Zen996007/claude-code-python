from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import orjson

from claude_code_py.remote.base import RemoteSessionSpec


class RemoteSessionRegistry:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def register(self, spec: RemoteSessionSpec) -> None:
        (self.root / f"{spec.session_id}.json").write_bytes(
            orjson.dumps(asdict(spec), option=orjson.OPT_INDENT_2)
        )

    def get(self, session_id: str) -> RemoteSessionSpec | None:
        path = self.root / f"{session_id}.json"
        if not path.exists():
            return None
        return RemoteSessionSpec(**orjson.loads(path.read_bytes()))

    def list_sessions(self) -> list[RemoteSessionSpec]:
        return [RemoteSessionSpec(**orjson.loads(path.read_bytes())) for path in sorted(self.root.glob("*.json"))]
