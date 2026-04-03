from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class RuntimeConfig(BaseModel):
    cwd: Path
    session_dir: Path
    model_name: str = "stub-model"
    max_turns: int = 12
    verbose: bool = False


class SessionState(BaseModel):
    session_id: str
    turn_count: int = 0
    total_tool_calls: int = 0
    total_messages: int = 0
    notes: list[str] = Field(default_factory=list)
