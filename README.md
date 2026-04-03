# claude-code-python

A realistic Python rewrite of a Claude Code-style local agent runtime.

## What exists now

- Async `QueryEngine` with session state and transcript persistence
- Multi-turn `AgentLoop` driven by a provider abstraction
- Provider layer with:
  - `MockProvider` for local development/tests
  - `OpenAICompatibleProvider` scaffold for real HTTP chat-completions backends
- Built-in tools:
  - `file_read`
  - `file_write`
  - `file_edit`
  - `file_list`
  - `bash`
- Tool registry with JSON-schema descriptions for model tool wiring
- Permission policy with allow / ask / deny decisions and approval handler hook
- Slash command skeleton with `/session` and `/help`
- Session artifacts:
  - `.sessions/<id>.jsonl` transcript
  - `.sessions/<id>.state.json` session state
- Clear extension scaffolding for plugins, skills, MCP, tasks, remote, and bridge layers
- Pytest coverage for registry, permissions, providers, and query flow

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
claude-code-py "read README.md"
```

## Architecture overview

```text
CLI
 └─ QueryEngine
    ├─ CommandRegistry
    ├─ SessionStore / TranscriptStore
    └─ AgentLoop
       ├─ Provider
       ├─ ToolRegistry
       └─ ToolExecutor
          └─ PermissionPolicy (+ approval hook)
```

## Current design choices

### Providers

`Provider` is the model-facing interface. The project now separates local orchestration from vendor specifics.

- `MockProvider` is deterministic and useful for tests.
- `OpenAICompatibleProvider` targets `/chat/completions`-style APIs and converts model tool calls into internal `ToolCall` objects.

### Permissions

Permission handling is intentionally explicit:

- read-only tools are auto-allowed
- dangerous shell patterns are denied
- writes and unknown operations go through `ASK`
- runtime can inject an approval callback for interactive or policy-based approval

### Sessions and transcripts

Each session has both a state file and append-only JSONL transcript. That gives a durable trail for replay, compaction, summaries, and future resumability.

## Roadmap

### Near-term

1. streaming provider responses
2. resumable sessions and transcript replay
3. richer shell execution events and structured tool outputs
4. command implementations for config/model/tool inspection
5. built-in diff/search/glob tools
6. plugin + skill discovery/loaders
7. MCP client runtime and transport adapters
8. remote bridge protocol and session forwarding
9. task orchestration / sub-agent workers
10. TUI layer

### Longer-term

- true Claude Code-style conversation compaction
- worktree-aware task execution
- multi-provider routing
- approval UIs and audit logs
- robust prompt/system policy management

## Repo hygiene

Generated artifacts are ignored via `.gitignore` and removed from tracked workspace output.
