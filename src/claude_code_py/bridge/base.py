from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BridgeMessage:
    source: str
    target: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BridgeSession:
    bridge_id: str
    local_session_id: str
    remote_session_id: str
    transport: str = "memory"
    metadata: dict[str, Any] = field(default_factory=dict)
