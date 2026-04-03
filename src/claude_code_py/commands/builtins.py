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
    help_text = "Show current session id"

    async def run(self, raw: str, context: CommandContext) -> CommandResult:
        return CommandResult(handled=True, output=f"session_id={context.session_id}")
