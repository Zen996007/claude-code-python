from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TaskSpec:
    id: str
    title: str
    status: str = "pending"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SubAgentTask:
    id: str
    task_id: str
    label: str
    runtime: str = "local"
    status: str = "pending"
    metadata: dict[str, Any] = field(default_factory=dict)
