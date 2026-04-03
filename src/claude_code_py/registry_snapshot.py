from __future__ import annotations

from dataclasses import asdict
from typing import Any


class RegistrySnapshot:
    @staticmethod
    def plugin_rows(loader: Any) -> list[dict[str, Any]]:
        return [
            {
                "name": item.name,
                "version": item.version,
                "entrypoint": item.entrypoint,
                "root": str(item.root),
                "metadata": item.metadata,
            }
            for item in loader.discover()
        ]

    @staticmethod
    def skill_rows(loader: Any) -> list[dict[str, Any]]:
        return [
            {
                "name": item.name,
                "description": item.description,
                "root": str(item.root),
                "enabled": item.enabled,
                "prompts": item.prompts,
                "references": [str(ref) for ref in item.references],
            }
            for item in loader.discover()
        ]

    @staticmethod
    def mcp_rows(registry: Any) -> list[dict[str, Any]]:
        return [
            {
                "name": item.name,
                "transport": item.transport,
                "command": item.command,
                "env": item.env,
                "metadata": item.metadata,
            }
            for item in registry.discover()
        ]

    @staticmethod
    def task_rows(orchestrator: Any) -> dict[str, Any]:
        return {
            "tasks": [asdict(item) for item in orchestrator.list_tasks()],
            "subagents": [asdict(item) for item in orchestrator.list_subagents()],
            "summary": orchestrator.summary(),
        }

    @staticmethod
    def remote_rows(registry: Any) -> list[dict[str, Any]]:
        return [asdict(item) for item in registry.list_sessions()]

    @staticmethod
    def bridge_rows(registry: Any) -> list[dict[str, Any]]:
        return [asdict(item) for item in registry.list_sessions()]
