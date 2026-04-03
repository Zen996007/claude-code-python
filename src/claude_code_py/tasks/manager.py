from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import orjson

from claude_code_py.tasks.base import SubAgentTask, TaskSpec


class TaskOrchestrator:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def add_task(self, task: TaskSpec) -> None:
        self._write_json(self.root / f"{task.id}.task.json", asdict(task))

    def add_subagent(self, subagent: SubAgentTask) -> None:
        self._write_json(self.root / f"{subagent.id}.subagent.json", asdict(subagent))

    def get_task(self, task_id: str) -> TaskSpec | None:
        path = self.root / f"{task_id}.task.json"
        if not path.exists():
            return None
        return TaskSpec(**orjson.loads(path.read_bytes()))

    def get_subagent(self, subagent_id: str) -> SubAgentTask | None:
        path = self.root / f"{subagent_id}.subagent.json"
        if not path.exists():
            return None
        return SubAgentTask(**orjson.loads(path.read_bytes()))

    def list_tasks(self) -> list[TaskSpec]:
        return [TaskSpec(**orjson.loads(path.read_bytes())) for path in sorted(self.root.glob("*.task.json"))]

    def list_subagents(self) -> list[SubAgentTask]:
        return [SubAgentTask(**orjson.loads(path.read_bytes())) for path in sorted(self.root.glob("*.subagent.json"))]

    def summary(self) -> dict[str, int]:
        tasks = self.list_tasks()
        subagents = self.list_subagents()
        return {
            "tasks": len(tasks),
            "subagents": len(subagents),
            "running_tasks": sum(1 for item in tasks if item.status == "running"),
            "running_subagents": sum(1 for item in subagents if item.status == "running"),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.write_bytes(orjson.dumps(payload, option=orjson.OPT_INDENT_2))
