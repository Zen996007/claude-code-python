from __future__ import annotations

import json

from claude_code_py.commands.base import Command, CommandContext, CommandResult
from claude_code_py.registry_snapshot import RegistrySnapshot


def _tail(raw: str) -> str:
    parts = raw.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else ""


class HelpCommand(Command):
    name = "help"
    help_text = "Show available slash commands"

    def __init__(self, lines: list[str] | None = None) -> None:
        self.lines = lines or []

    def set_lines(self, lines: list[str]) -> None:
        self.lines = lines

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        body = "\n".join(self.lines) if self.lines else "No commands registered"
        return CommandResult(handled=True, output=body)


class SessionCommand(Command):
    name = "session"
    help_text = "Show current session id, counters, and resume lineage"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        state = context.metadata.get("state")
        if state is None:
            return CommandResult(handled=True, output=f"session_id={context.session_id}")
        details = [
            f"session_id={state.session_id}",
            f"turns={state.turn_count}",
            f"messages={state.total_messages}",
            f"tools={state.total_tool_calls}",
            f"transcript_entries={state.transcript_entries}",
        ]
        if state.resumed_from:
            details.append(f"resumed_from={state.resumed_from}")
        if state.last_user_prompt:
            details.append(f"last_user_prompt={state.last_user_prompt}")
        return CommandResult(handled=True, output=" ".join(details))


class ToolsCommand(Command):
    name = "tools"
    help_text = "List registered tools or inspect one tool: /tools [name]"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        registry = context.metadata["tool_registry"]
        name = _tail(raw)
        if not name:
            return CommandResult(handled=True, output="\n".join(registry.names()))
        tool = registry.get(name)
        if tool is None:
            return CommandResult(handled=True, output=f"Unknown tool: {name}")
        description = registry.describe(name)
        return CommandResult(
            handled=True,
            output=(
                f"name={description['name']}\n"
                f"description={description['description']}\n"
                f"tags={','.join(description.get('tags', [])) or '-'}\n"
                f"parameters={json.dumps(description['parameters'], ensure_ascii=False)}"
            ),
        )


class ProviderCommand(Command):
    name = "provider"
    help_text = "Show active provider configuration"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        provider = context.metadata["provider"]
        config = provider.config
        runtime = context.metadata.get("runtime")
        return CommandResult(
            handled=True,
            output=(
                f"provider={provider.__class__.__name__}\n"
                f"provider_id={getattr(runtime, 'provider', 'unknown')}\n"
                f"model={config.model}\n"
                f"temperature={config.temperature}\n"
                f"max_tokens={config.max_tokens}\n"
                f"api_base={config.api_base or '-'}\n"
                f"api_key_env={config.api_key_env or '-'}"
            ),
        )


class PluginsCommand(Command):
    name = "plugins"
    help_text = "List discovered plugins or inspect one: /plugins [name]"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        loader = context.metadata.get("plugin_loader")
        items = RegistrySnapshot.plugin_rows(loader) if loader else []
        if not items:
            return CommandResult(handled=True, output="No plugins discovered")
        name = _tail(raw)
        if not name:
            return CommandResult(
                handled=True,
                output="\n".join(f"{item['name']}@{item['version']} [{item['root']}]" for item in items),
            )
        for item in items:
            if item["name"] == name:
                return CommandResult(handled=True, output=json.dumps(item, indent=2, ensure_ascii=False))
        return CommandResult(handled=True, output=f"Unknown plugin: {name}")


class SkillsCommand(Command):
    name = "skills"
    help_text = "List discovered skills or inspect one: /skills [name]"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        loader = context.metadata.get("skill_loader")
        items = RegistrySnapshot.skill_rows(loader) if loader else []
        if not items:
            return CommandResult(handled=True, output="No skills discovered")
        name = _tail(raw)
        if not name:
            return CommandResult(
                handled=True,
                output="\n".join(f"{item['name']}: {item['description']}" for item in items),
            )
        for item in items:
            if item["name"] == name:
                return CommandResult(handled=True, output=json.dumps(item, indent=2, ensure_ascii=False))
        return CommandResult(handled=True, output=f"Unknown skill: {name}")


class MCPCommand(Command):
    name = "mcp"
    help_text = "List discovered MCP servers or inspect one: /mcp [name]"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        registry = context.metadata.get("mcp_registry")
        items = RegistrySnapshot.mcp_rows(registry) if registry else []
        if not items:
            return CommandResult(handled=True, output="No MCP servers discovered")
        name = _tail(raw)
        if not name:
            return CommandResult(
                handled=True,
                output="\n".join(f"{item['name']}: {item['transport']} -> {' '.join(item['command'])}" for item in items),
            )
        for item in items:
            if item["name"] == name:
                return CommandResult(handled=True, output=json.dumps(item, indent=2, ensure_ascii=False))
        return CommandResult(handled=True, output=f"Unknown MCP server: {name}")


class TasksCommand(Command):
    name = "tasks"
    help_text = "Show task summary or inspect details: /tasks detail"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        orchestrator = context.metadata.get("task_orchestrator")
        if orchestrator is None:
            return CommandResult(handled=True, output="No task orchestrator configured")
        detail = _tail(raw)
        payload = RegistrySnapshot.task_rows(orchestrator)
        if detail == "detail":
            return CommandResult(handled=True, output=json.dumps(payload, indent=2, ensure_ascii=False))
        return CommandResult(
            handled=True,
            output=" ".join(f"{key}={value}" for key, value in payload["summary"].items()),
        )


class RemoteCommand(Command):
    name = "remote"
    help_text = "List remote sessions or inspect one: /remote [session_id]"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        registry = context.metadata.get("remote_registry")
        items = RegistrySnapshot.remote_rows(registry) if registry else []
        if not items:
            return CommandResult(handled=True, output="No remote sessions registered")
        session_id = _tail(raw)
        if not session_id:
            return CommandResult(
                handled=True,
                output="\n".join(f"{item['session_id']}: {item['protocol']} {item['endpoint']}" for item in items),
            )
        for item in items:
            if item["session_id"] == session_id:
                return CommandResult(handled=True, output=json.dumps(item, indent=2, ensure_ascii=False))
        return CommandResult(handled=True, output=f"Unknown remote session: {session_id}")


class BridgesCommand(Command):
    name = "bridges"
    help_text = "List bridge sessions or inspect one: /bridges [bridge_id]"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        registry = context.metadata.get("bridge_registry")
        items = RegistrySnapshot.bridge_rows(registry) if registry else []
        if not items:
            return CommandResult(handled=True, output="No bridge sessions registered")
        bridge_id = _tail(raw)
        if not bridge_id:
            return CommandResult(
                handled=True,
                output="\n".join(
                    f"{item['bridge_id']}: {item['local_session_id']} -> {item['remote_session_id']} ({item['transport']})"
                    for item in items
                ),
            )
        for item in items:
            if item["bridge_id"] == bridge_id:
                return CommandResult(handled=True, output=json.dumps(item, indent=2, ensure_ascii=False))
        return CommandResult(handled=True, output=f"Unknown bridge session: {bridge_id}")


class RuntimeCommand(Command):
    name = "runtime"
    help_text = "Show runtime directories and provider selection"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        runtime = context.metadata["runtime"]
        return CommandResult(
            handled=True,
            output=(
                f"cwd={runtime.cwd}\n"
                f"session_dir={runtime.session_dir}\n"
                f"plugin_dir={runtime.plugin_dir}\n"
                f"skill_dir={runtime.skill_dir}\n"
                f"mcp_dir={runtime.mcp_dir}\n"
                f"provider={runtime.provider}\n"
                f"model={runtime.model_name}"
            ),
        )


class CommandsCommand(Command):
    name = "commands"
    help_text = "List registered slash commands"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        registry = context.metadata.get("commands")
        lines = registry.help_lines() if registry else []
        return CommandResult(handled=True, output="\n".join(lines) if lines else "No commands registered")
