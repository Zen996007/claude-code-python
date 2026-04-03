# Architecture

## High-level flow

1. **CLI** initializes runtime config, provider selection, tools, commands, and approval hooks.
2. **QueryEngine** owns session state, transcript persistence, command dispatch, and prompt submission.
3. **AgentLoop** performs the provider ⇄ tool execution loop until the provider ends the turn or max-turns trips.
4. **Registry surfaces** expose plugins, skills, MCP specs, tasks, remote sessions, and bridge sessions into slash commands and top-level CLI inspection.
5. **ToolExecutor** validates tool calls, evaluates permissions, obtains approval when needed, and executes tools.

## Package map

- `providers/`
  - `base.py`: provider protocol and config
  - `mock.py`: deterministic development provider
  - `openai_compatible.py`: real HTTP provider scaffold
  - `factory.py`: runtime provider selection
- `commands/`
  - `builtins.py`: slash command implementations
  - `registry.py`: slash command dispatch and typo suggestions
- `builtins/`
  - `file_tools.py`: read/write/edit/list tools
  - `search_tools.py`: glob and grep-style project search
  - `bash_tool.py`: subprocess execution
- `storage/`
  - `transcript.py`: transcript and session state stores, latest-session lookup
- `plugins/`, `skills/`, `mcp/`, `tasks/`, `remote/`, `bridge/`
  - filesystem-backed specs surfaced through runtime introspection
- `registry_snapshot.py`
  - stable serialization helpers used by commands/CLI

## Session lifecycle

```text
CLI run
  -> build runtime config
  -> build provider from runtime.provider
  -> build tool registry + command registry
  -> QueryEngine.submit(prompt)
      -> slash command? dispatch immediately
      -> append user message to transcript
      -> Provider.generate(messages, tools)
      -> tool calls?
         -> ToolExecutor.execute(call)
            -> PermissionPolicy.evaluate(...)
            -> optional approval handler
            -> tool.run(parsed_input, context)
      -> append tool messages
      -> append assistant messages
      -> persist session counters + last prompt + lineage
```

## Design notes

- **provider-independent core** for easier testing
- **append-only transcripts** for replay and auditing
- **registry-driven tools/commands** for future auto-discovery
- **filesystem-backed registries** keep plugin/skill/MCP/task/remote/bridge state transparent
- **CLI and slash-command parity** lets the same state be inspected in or out of a live session
