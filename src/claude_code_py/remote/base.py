from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RemoteSessionSpec:
    session_id: str
    endpoint: str
    protocol: str = "http"
    metadata: dict[str, Any] = field(default_factory=dict)
