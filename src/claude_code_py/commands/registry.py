from __future__ import annotations

from difflib import get_close_matches

from claude_code_py.commands.base import Command, CommandContext, CommandResult


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        self._commands[command.name] = command

    def names(self) -> list[str]:
        return sorted(self._commands)

    async def dispatch(self, raw: str, context: CommandContext) -> CommandResult:
        if not raw.startswith("/"):
            return CommandResult(handled=False, output="")
        body = raw[1:].strip()
        if not body:
            return CommandResult(handled=True, output="Empty command. Try /help")
        name, *_ = body.split(maxsplit=1)
        name = name.lower()
        command = self._commands.get(name)
        if command is None:
            suggestions = get_close_matches(name, self.names(), n=3, cutoff=0.5)
            suffix = f" Did you mean: {' '.join('/' + item for item in suggestions)}" if suggestions else ""
            return CommandResult(handled=True, output=f"Unknown command: /{name}.{suffix}")
        return await command.run(f"/{body}", context)

    def help_lines(self) -> list[str]:
        return [f"/{name}: {command.help_text}" for name, command in sorted(self._commands.items())]
