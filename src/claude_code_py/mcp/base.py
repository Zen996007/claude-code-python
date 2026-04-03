from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class MCPServerSpec:
    name: str
    transport: str = "stdio"
    command: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class MCPServer(Protocol):
    spec: MCPServerSpec

    async def start(self) -> None: ...

    async def stop(self) -> None: ...

    async def invoke(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]: ...
