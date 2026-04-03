# Architecture

## Runtime stack

1. **CLI** initializes runtime config, tools, commands, provider, and approval hooks.
2. **QueryEngine** owns session state, transcript persistence, command dispatch, and prompt submission.
3. **AgentLoop** performs the provider ⇄ tool execution loop until the provider ends the turn or max-turns trips.
4. **Provider** converts conversation state into model responses.
5. **ToolExecutor** validates tool calls, evaluates permissions, obtains approval when needed, and executes tools.
6. **SessionStore / TranscriptStore** persist state and append-only execution history.

## Main modules

- `providers/`
  - `base.py`: provider protocol and config
  - `mock.py`: deterministic development provider
  - `openai_compatible.py`: real HTTP provider scaffold
- `commands/`
  - `base.py`: command interfaces
  - `registry.py`: slash command dispatch
  - `builtins.py`: starter commands
- `permissions/`
  - `policy.py`: request/result model with allow/ask/deny decisions
- `storage/`
  - `transcript.py`: transcript and session state stores
- `integrations/`, `plugins/`, `skills/`, `mcp/`, `tasks/`, `remote/`, `bridge/`
  - intentionally thin interfaces to make later feature work additive instead of invasive

## Turn flow

```text
user prompt
  -> QueryEngine
    -> CommandRegistry? (if /command)
    -> AgentLoop
      -> Provider.generate(messages, tools)
      -> tool calls?
         -> ToolExecutor.execute(call)
         -> PermissionPolicy.evaluate(request)
         -> approval hook? (optional)
         -> tool.run(parsed_input, context)
      -> append tool messages
      -> repeat until end_turn
    -> persist transcript + state
```

## Why this structure

This keeps the rewrite practical:

- **provider-independent core** for easier testing
- **append-only transcript** for observability and replay
- **approval hook** so policy and UI stay decoupled
- **registry-driven tools/commands** for future auto-discovery
- **scaffolded extension packages** so MCP/plugins/skills can land without another rewrite
