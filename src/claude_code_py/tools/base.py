from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel


@dataclass(slots=True)
class ToolContext:
    cwd: Path
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def resolve_path(self, raw_path: str) -> Path:
        candidate = (self.cwd / raw_path).resolve()
        root = self.cwd.resolve()
        if candidate != root and root not in candidate.parents:
            raise ValueError(f"Path escapes working directory: {raw_path}")
        return candidate


class ToolInput(BaseModel):
    pass


class Tool(ABC):
    name: str
    description: str
    input_model: type[BaseModel]
    tags: tuple[str, ...] = ()

    def is_concurrency_safe(self, data: BaseModel) -> bool:
        return False

    @abstractmethod
    async def run(self, data: BaseModel, context: ToolContext) -> str:
        raise NotImplementedError

    def parse(self, arguments: dict[str, Any]) -> BaseModel:
        return self.input_model.model_validate(arguments)

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.input_model.model_json_schema(),
        }
