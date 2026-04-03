from __future__ import annotations

from claude_code_py.commands.base import Command, CommandContext, CommandResult


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        self._commands[command.name] = command

    async def dispatch(self, raw: str, context: CommandContext) -> CommandResult:
        if not raw.startswith("/"):
            return CommandResult(handled=False, output="")
        name = raw.split()[0][1:]
        command = self._commands.get(name)
        if command is None:
            return CommandResult(handled=True, output=f"Unknown command: /{name}")
        return await command.run(raw, context)

    def help_lines(self) -> list[str]:
        return [f"/{name}: {command.help_text}" for name, command in sorted(self._commands.items())]
