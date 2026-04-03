from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class SkillSpec:
    name: str
    root: Path
    description: str = ""
    enabled: bool = True
    prompts: list[str] = field(default_factory=list)
    references: list[Path] = field(default_factory=list)
