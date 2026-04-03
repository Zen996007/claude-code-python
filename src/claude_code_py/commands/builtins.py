from __future__ import annotations

from claude_code_py.commands.base import Command, CommandContext, CommandResult


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
    help_text = "Show current session id and counters"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        state = context.metadata.get("state")
        if state is None:
            return CommandResult(handled=True, output=f"session_id={context.session_id}")
        return CommandResult(
            handled=True,
            output=(
                f"session_id={state.session_id} turns={state.turn_count} "
                f"messages={state.total_messages} tools={state.total_tool_calls}"
            ),
        )


class ToolsCommand(Command):
    name = "tools"
    help_text = "List registered tools or inspect one tool: /tools [name]"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        registry = context.metadata["tool_registry"]
        parts = raw.split(maxsplit=1)
        if len(parts) == 1:
            return CommandResult(handled=True, output="\n".join(registry.names()))
        name = parts[1].strip()
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
                f"parameters={description['parameters']}"
            ),
        )


class ProviderCommand(Command):
    name = "provider"
    help_text = "Show active provider configuration"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        provider = context.metadata["provider"]
        config = provider.config
        return CommandResult(
            handled=True,
            output=(
                f"provider={provider.__class__.__name__}\n"
                f"model={config.model}\n"
                f"temperature={config.temperature}\n"
                f"max_tokens={config.max_tokens}"
            ),
        )


class PluginsCommand(Command):
    name = "plugins"
    help_text = "List discovered plugins"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        loader = context.metadata.get("plugin_loader")
        plugins = loader.discover() if loader else []
        if not plugins:
            return CommandResult(handled=True, output="No plugins discovered")
        return CommandResult(
            handled=True,
            output="\n".join(f"{item.name}@{item.version} [{item.root}]" for item in plugins),
        )


class SkillsCommand(Command):
    name = "skills"
    help_text = "List discovered skills"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        loader = context.metadata.get("skill_loader")
        skills = loader.discover() if loader else []
        if not skills:
            return CommandResult(handled=True, output="No skills discovered")
        return CommandResult(
            handled=True,
            output="\n".join(f"{item.name}: {item.description}" for item in skills),
        )


class MCPCommand(Command):
    name = "mcp"
    help_text = "List discovered MCP servers"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        registry = context.metadata.get("mcp_registry")
        servers = registry.discover() if registry else []
        if not servers:
            return CommandResult(handled=True, output="No MCP servers discovered")
        return CommandResult(
            handled=True,
            output="\n".join(f"{item.name}: {item.transport} -> {' '.join(item.command)}" for item in servers),
        )


class TasksCommand(Command):
    name = "tasks"
    help_text = "Show task orchestrator summary"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        orchestrator = context.metadata.get("task_orchestrator")
        if orchestrator is None:
            return CommandResult(handled=True, output="No task orchestrator configured")
        summary = orchestrator.summary()
        return CommandResult(
            handled=True,
            output=" ".join(f"{key}={value}" for key, value in summary.items()),
        )
