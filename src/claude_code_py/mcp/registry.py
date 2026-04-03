from __future__ import annotations

from pathlib import Path
from typing import Any

import orjson

from claude_code_py.mcp.base import MCPServerSpec


class MCPRegistry:
    def __init__(self, root: Path) -> None:
        self.root = root
        self._specs: dict[str, MCPServerSpec] = {}

    def discover(self) -> list[MCPServerSpec]:
        if not self.root.exists():
            return []
        specs: list[MCPServerSpec] = []
        for manifest in sorted(self.root.glob("*.json")):
            payload = orjson.loads(manifest.read_bytes())
            spec = MCPServerSpec(
                name=payload["name"],
                transport=payload.get("transport", "stdio"),
                command=payload.get("command", []),
                env=payload.get("env", {}),
                metadata=self._metadata(payload),
            )
            specs.append(spec)
            self._specs[spec.name] = spec
        return specs

    def get(self, name: str) -> MCPServerSpec | None:
        if name not in self._specs:
            self.discover()
        return self._specs.get(name)

    def runnable_command(self, name: str) -> list[str]:
        spec = self.get(name)
        if spec is None:
            raise KeyError(name)
        if not spec.command:
            raise ValueError(f"MCP server {name} has no runnable command")
        return spec.command

    def _metadata(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in payload.items() if key not in {"name", "transport", "command", "env"}}
