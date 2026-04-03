from __future__ import annotations

from pathlib import Path
from typing import Any

import orjson

from claude_code_py.plugins.base import PluginSpec


class PluginLoader:
    def __init__(self, root: Path) -> None:
        self.root = root

    def discover(self) -> list[PluginSpec]:
        if not self.root.exists():
            return []
        found: list[PluginSpec] = []
        for manifest in sorted(self.root.glob("*/plugin.json")):
            payload = orjson.loads(manifest.read_bytes())
            found.append(
                PluginSpec(
                    name=payload["name"],
                    root=manifest.parent,
                    version=payload.get("version", "0.1.0"),
                    entrypoint=payload.get("entrypoint"),
                    metadata=self._metadata(payload),
                )
            )
        return found

    def _metadata(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in payload.items() if key not in {"name", "version", "entrypoint"}}
