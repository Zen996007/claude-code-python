from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BridgeMessage:
    source: str
    target: str
    payload: dict[str, Any] = field(default_factory=dict)
