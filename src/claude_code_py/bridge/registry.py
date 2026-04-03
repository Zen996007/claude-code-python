from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import orjson

from claude_code_py.bridge.base import BridgeSession


class BridgeRegistry:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def register(self, session: BridgeSession) -> None:
        (self.root / f"{session.bridge_id}.json").write_bytes(
            orjson.dumps(asdict(session), option=orjson.OPT_INDENT_2)
        )

    def list_sessions(self) -> list[BridgeSession]:
        return [BridgeSession(**orjson.loads(path.read_bytes())) for path in sorted(self.root.glob("*.json"))]
