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
- Real discovery/loaders for plugins, skills, MCP manifests, tasks, remote sessions, and bridge sessions
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

Each session has both a state file and append-only JSONL transcript. The runtime can now replay transcript entries, rebuild in-memory conversation state, and resume a prior session id. Transcript files also capture provider events and tool-call records for later audit/debug work.

## Roadmap

### Milestone 2 delivered

1. provider streaming/event model with transcripted provider events
2. resumable sessions and transcript replay
3. richer slash-command introspection for tools/provider/runtime counters
4. plugin + skill discovery/loaders
5. MCP registry/loader scaffolding with runnable command resolution
6. task orchestration primitives and sub-agent descriptors
7. bridge + remote session registries
8. expanded CLI commands for running, resuming, listing sessions, and listing tools

### Near-term

1. richer shell execution events and structured tool outputs
2. built-in diff/search/glob tools
3. MCP client runtime transports beyond manifest loading
4. remote bridge protocol forwarding and sync
5. task worker execution backends
6. TUI layer

### Longer-term

- true Claude Code-style conversation compaction
- worktree-aware task execution
- multi-provider routing
- approval UIs and audit logs
- robust prompt/system policy management

## Repo hygiene

Generated artifacts are ignored via `.gitignore` and removed from tracked workspace output.
