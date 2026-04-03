from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RemoteSessionSpec:
    session_id: str
    endpoint: str
    protocol: str = "http"
