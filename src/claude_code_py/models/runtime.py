from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class RuntimeConfig(BaseModel):
    cwd: Path
    session_dir: Path
    model_name: str = "mock-provider"
    max_turns: int = 12
    verbose: bool = False
    allow_commands: bool = True
    plugin_dir: Path | None = None
    skill_dir: Path | None = None
    mcp_dir: Path | None = None


class SessionState(BaseModel):
    session_id: str
    turn_count: int = 0
    total_tool_calls: int = 0
    total_messages: int = 0
    notes: list[str] = Field(default_factory=list)
    command_history: list[str] = Field(default_factory=list)
    resumed_from: str | None = None
    transcript_entries: int = 0
