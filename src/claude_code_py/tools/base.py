from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel


@dataclass(slots=True)
class ToolContext:
    cwd: Path


class ToolInput(BaseModel):
    pass


class Tool(ABC):
    name: str
    description: str
    input_model: type[BaseModel]

    def is_concurrency_safe(self, data: BaseModel) -> bool:
        return False

    @abstractmethod
    async def run(self, data: BaseModel, context: ToolContext) -> str:
        raise NotImplementedError

    def parse(self, arguments: dict[str, Any]) -> BaseModel:
        return self.input_model.model_validate(arguments)
