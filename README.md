# claude-code-python

A realistic Python rewrite of a Claude Code-style local agent runtime.

## What exists now

- Async `QueryEngine` with session state, transcript persistence, and resume support
- Multi-turn `AgentLoop` driven by a provider abstraction
- Provider layer with:
  - `MockProvider` for local development/tests
  - `OpenAICompatibleProvider` scaffold for real HTTP chat-completions backends
  - runtime provider selection via CLI flags or env vars
- Built-in tools:
  - `file_read`
  - `file_write`
  - `file_edit`
  - `file_list`
  - `file_glob`
  - `grep_search`
  - `bash`
- Tool registry with JSON-schema descriptions for model tool wiring and CLI introspection
- Permission policy with allow / ask / deny decisions and approval handler hook
- Slash command layer with runtime/provider/tool/registry introspection
- Session artifacts:
  - `.sessions/<id>.jsonl` transcript
  - `.sessions/<id>.state.json` session state
- Real discovery/loaders for plugins, skills, MCP manifests, tasks, remote sessions, and bridge sessions
- Richer CLI inspection paths for plugins/skills/MCP/tasks/remote/bridges/providers/runtime
- Pytest coverage for registry, permissions, providers, search tools, command dispatch, and query flow

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q
claude-code-py run "read README.md"
```

## CLI usage

### Basic run

```bash
claude-code-py run "read README.md"
claude-code-py run --stream "list src"
claude-code-py run --resume "continue from the last session"
claude-code-py sessions
claude-code-py tools
```

### Provider selection

```bash
claude-code-py run --provider mock "hello"
claude-code-py run \
  --provider openai-compatible \
  --model gpt-4.1-mini \
  --api-base https://api.openai.com/v1 \
  --api-key-env OPENAI_API_KEY \
  "summarize the repo"
```

You can also drive provider config with env vars:

```bash
export CLAUDE_CODE_PY_PROVIDER=openai-compatible
export CLAUDE_CODE_PY_MODEL=gpt-4.1-mini
export CLAUDE_CODE_PY_API_BASE=https://api.openai.com/v1
export CLAUDE_CODE_PY_API_KEY_ENV=OPENAI_API_KEY
```

### Registry inspection

```bash
claude-code-py inspect plugins
claude-code-py inspect skills --name writer
claude-code-py inspect mcp --name fetch
claude-code-py inspect tasks
claude-code-py inspect remote --name remote-1
claude-code-py inspect bridges --name bridge-1
claude-code-py inspect runtime
claude-code-py inspect commands
```

### Slash commands inside a session

```text
/help
/session
/provider
/runtime
/tools
/tools grep_search
/plugins
/skills
/mcp
/tasks
/tasks detail
/remote
/bridges
/commands
```

## Architecture overview

```text
CLI
 └─ QueryEngine
    ├─ CommandRegistry
    ├─ SessionStore / TranscriptStore
    ├─ Registry snapshots (plugins / skills / mcp / tasks / remote / bridges)
    └─ AgentLoop
       ├─ Provider
       ├─ ToolRegistry
       └─ ToolExecutor
          └─ PermissionPolicy (+ approval hook)
```

## Current design choices

### Providers

`Provider` is the model-facing interface. The project separates local orchestration from vendor specifics.

- `MockProvider` is deterministic and useful for tests.
- `OpenAICompatibleProvider` targets `/chat/completions`-style APIs and converts model tool calls into internal `ToolCall` objects.
- `providers.factory.build_provider()` centralizes provider selection.

### Permissions

Permission handling is intentionally explicit:

- read-only tools are auto-allowed
- dangerous shell patterns are denied
- writes and unknown operations go through `ASK`
- runtime can inject an approval callback for interactive or policy-based approval

### Sessions and transcripts

Each session has both a state file and append-only JSONL transcript.

The runtime can now:

- replay transcript entries
- rebuild in-memory conversation state
- resume the latest or a specific prior session id
- persist `last_user_prompt` and `last_assistant_message`
- render richer `sessions` output for resume/debug workflows

### Registry-backed runtime surfaces

Plugins, skills, MCP specs, tasks, remote sessions, and bridge sessions are no longer just loose file loaders. They are exposed through both:

- slash commands for in-session inspection
- top-level CLI `inspect` commands for out-of-band debugging and scripting

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

### Milestone 3 delivered

1. provider selection/config plumbing in CLI and runtime
2. concrete registry inspection for plugins/skills/MCP/tasks/remote/bridges
3. richer session listing/resume UX with last prompt and lineage
4. command dispatch suggestions for mistyped slash commands
5. new search/introspection tools: `file_glob` and `grep_search`
6. expanded tests covering CLI, registry detail views, command suggestions, and search tools

### Near-term

1. richer shell execution events and structured tool outputs
2. MCP client runtime transports beyond manifest loading
3. remote bridge protocol forwarding and sync
4. task worker execution backends
5. TUI layer

### Longer-term

- true Claude Code-style conversation compaction
- worktree-aware task execution
- multi-provider routing
- approval UIs and audit logs
- robust prompt/system policy management

## Repo hygiene

Generated artifacts are ignored via `.gitignore` and removed from tracked workspace output.
