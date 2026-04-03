# claude-code-python

Python rewrite scaffold for a Claude Code–style agent runtime.

## Goals

- Python 3.11+
- Typer CLI
- Pydantic models and schemas
- Async-first runtime with asyncio/anyio
- Modular architecture:
  - CLI
  - Query Engine
  - Agent Loop
  - Tool registry / executor
  - Permissions
  - Transcript storage
  - Commands
  - MCP / plugins / skills
  - Tasks / multi-agent
  - TUI adapters

## Status

This is the first scaffold version. It defines the package layout and the initial runtime skeleton for a full-stack Python rewrite.
