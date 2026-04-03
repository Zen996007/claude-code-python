from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class PluginSpec:
    name: str
    version: str = "0.1.0"
    entrypoint: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Plugin(Protocol):
    spec: PluginSpec

    async def load(self) -> None: ...
