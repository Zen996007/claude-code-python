from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(slots=True)
class IntegrationSpec:
    name: str
    enabled: bool = True
    config: dict[str, Any] = field(default_factory=dict)


class Integration(Protocol):
    spec: IntegrationSpec

    async def start(self) -> None: ...

    async def stop(self) -> None: ...
