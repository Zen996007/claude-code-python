from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CommandContext:
    session_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CommandResult:
    handled: bool
    output: str
    should_continue: bool = False


class Command(ABC):
    name: str
    help_text: str

    @abstractmethod
    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        raise NotImplementedError
