from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class RuntimeConfig(BaseModel):
    cwd: Path
    session_dir: Path
    model_name: str = "mock-provider"
    provider: str = "mock"
    max_turns: int = 12
    verbose: bool = False
    allow_commands: bool = True
    plugin_dir: Path | None = None
    skill_dir: Path | None = None
    mcp_dir: Path | None = None
    temperature: float = 0.0
    max_tokens: int = 2048
    api_base: str | None = None
    api_key_env: str | None = None
    system_prompt: str | None = None


class SessionState(BaseModel):
    session_id: str
    turn_count: int = 0
    total_tool_calls: int = 0
    total_messages: int = 0
    notes: list[str] = Field(default_factory=list)
    command_history: list[str] = Field(default_factory=list)
    resumed_from: str | None = None
    transcript_entries: int = 0
    last_user_prompt: str | None = None
    last_assistant_message: str | None = None
