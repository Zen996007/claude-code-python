# Architecture

## Rewrite target

This project aims to re-express the main Claude Code architectural layers in Python:

1. CLI bootstrap
2. Runtime initialization
3. Session-oriented QueryEngine
4. Agent loop with tool_use / tool_result cycle
5. Tool abstraction, registry, and executor
6. Permission system
7. Command system
8. Transcript persistence and compaction hooks
9. MCP / plugin / skill integration points
10. Task / multi-agent / worktree-ready orchestration
11. TUI-friendly presentation layer

## Planned package map

- `cli/` – Typer CLI entrypoints
- `core/` – Query engine, agent loop, runtime state
- `tools/` – Tool abstractions and registry
- `builtins/` – Built-in file, shell, web tools
- `permissions/` – Permission policy and decisions
- `storage/` – session transcripts and persistence
- `commands/` – slash-command analogs
- `integrations/`, `mcp/`, `plugins/`, `skills/` – extension layers
- `tasks/` – task system and multi-agent orchestration
- `ui/` – terminal presentation adapters
- `bridge/`, `remote/` – remote session support
- `models/` – shared Pydantic models

## Development phases

### Phase 1
- Core models
- CLI bootstrap
- QueryEngine skeleton
- Tool abstraction and registry
- Built-in file/shell tools
- Minimal permission gate
- Local transcript storage

### Phase 2
- Streaming agent loop
- command routing
- richer shell/file tooling
- summary/compact hooks
- test suite expansion

### Phase 3
- MCP integration
- plugin and skill loaders
- tasks, sub-agents, worktree support
- TUI layer
- remote bridge/session features
