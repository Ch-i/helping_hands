# ARCHITECTURE.md

High-level architecture of helping_hands. For detailed design notes see
`obsidian/docs/Architecture.md`. For coding conventions see `AGENT.md`.

---

## System overview

```
                    ┌─────────────┐
                    │   User /    │
                    │   Client    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼────┐ ┌────▼─────┐ ┌───▼────┐
        │   CLI    │ │ FastAPI  │ │  MCP   │
        │  main.py │ │  app.py  │ │ server │
        └─────┬────┘ └────┬─────┘ └───┬────┘
              │            │           │
              └────────────┼───────────┘
                           │
                    ┌──────▼──────┐
                    │    lib/     │
                    │  (core)     │
                    └──────┬──────┘
                           │
         ┌─────────┬───────┼───────┬──────────┐
         │         │       │       │          │
    ┌────▼───┐ ┌───▼──┐ ┌──▼──┐ ┌──▼───┐ ┌───▼────┐
    │ config │ │ repo │ │hands│ │github│ │  meta  │
    │        │ │      │ │ v1  │ │      │ │ tools  │
    └────────┘ └──────┘ └──┬──┘ └──────┘ └────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼────┐ ┌────▼─────┐ ┌───▼────────┐
        │ iterative│ │   e2e    │ │ cli hands  │
        │ hands    │ │   hand   │ │ (codex,    │
        │ (lg, at) │ │          │ │ claude...) │
        └──────────┘ └──────────┘ └────────────┘
```

## Layers

### 1. Entry points

Three runtime surfaces share the same core library:

- **CLI** (`cli/main.py`) — Interactive terminal usage
- **Server** (`server/app.py`) — FastAPI + Celery for async/scheduled runs
- **MCP** (`server/mcp_server.py`) — Tool server for IDE integrations

### 2. Core library (`lib/`)

- **config** — `Config.from_env()` loads `.env`, env vars, CLI overrides
- **repo** — `RepoIndex` builds file maps from local repos
- **github** — `GitHubClient` for clone/branch/commit/push/PR operations
- **ai_providers/** — Provider wrappers (OpenAI, Anthropic, Google, LiteLLM, Ollama) with common interface
- **hands/v1/hand/** — Execution backends (see below)
- **meta/tools/** — Filesystem, command, web, and registry tools
- **meta/skills/** — Skill catalog for agent capabilities

### 3. Hand backends

All hands extend `Hand` base class (`base.py`) and implement `run()`/`stream()`:

| Hand | Module | Type | Description |
|---|---|---|---|
| `E2EHand` | `e2e.py` | Integration | Clone/edit/commit/push/PR flow |
| `BasicLangGraphHand` | `langgraph.py` | Iterative | LangGraph agent loop |
| `BasicAtomicHand` | `atomic.py` | Iterative | Atomic Agents loop |
| `CodexCLIHand` | `cli/codex.py` | CLI subprocess | Wraps `codex exec` |
| `ClaudeCodeHand` | `cli/claude.py` | CLI subprocess | Wraps `claude -p` |
| `GooseCLIHand` | `cli/goose.py` | CLI subprocess | Wraps `goose run` |
| `GeminiCLIHand` | `cli/gemini.py` | CLI subprocess | Wraps `gemini -p` |
| `OpenCodeCLIHand` | `cli/opencode.py` | CLI subprocess | Wraps `opencode run` |

### 4. Model resolution

Model strings (e.g., `gpt-5.2`, `anthropic/claude-sonnet-4-5`) are resolved
through `ai_providers/` wrappers and `model_provider.py` adapters before
reaching backend-specific clients.

### 5. Finalization

All hands share a finalization flow (in `base.py`):
1. Detect git changes
2. Optional pre-commit run (when `enable_execution` is on)
3. Create branch, commit, push via token-authenticated remote
4. Open/update PR

Disable with `--no-pr`.

## Data flows

### CLI task execution

```
User runs CLI command
        │
        ▼
  cli/main.py parses args
        │
        ▼
  Config.from_env() merges .env + env vars + CLI overrides
        │
        ▼
  RepoIndex.from_path(target) builds file map
        │
        ▼
  Hand subclass instantiated (based on --backend)
        │
        ▼
  hand.stream(prompt) called
        │
        ├── Iteration 1: bootstrap context (README, AGENT.md, tree)
        │       │
        │       ▼
        │   AI provider generates response
        │       │
        │       ▼
        │   Parse @@FILE / @@READ / @@TOOL blocks
        │       │
        │       ▼
        │   Apply file edits, resolve reads, run tools
        │       │
        │       ▼
        │   Check SATISFIED: yes/no
        │
        ├── Iteration 2..N: prior summary as context (no bootstrap)
        │       │
        │       ▼
        │   (same parse → apply → check loop)
        │
        └── Exit: satisfied | max_iterations | interrupted
                │
                ▼
          Finalization: branch → commit → push → PR
```

### Server task execution

```
Client POST /build with {repo_path, prompt, backend, ...}
        │
        ▼
  FastAPI validates request, generates task_id
        │
        ▼
  Celery task queued → worker picks up
        │
        ▼
  Worker: Config + RepoIndex + Hand (same as CLI path)
        │
        ▼
  hand.run(prompt) called (non-streaming)
        │
        ▼
  TaskResult stored (Redis/in-memory)
        │
        ▼
  Client polls GET /tasks/{task_id} until status=complete
```

### MCP server flow

```
IDE sends MCP tool call (e.g., "build_repo")
        │
        ▼
  mcp_server.py routes to handler
        │
        ▼
  Handler creates Config + RepoIndex + Hand
        │
        ▼
  hand.run(prompt) → result returned as MCP response
```

## External integrations

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   GitHub     │     │  AI Provider │     │    Redis     │
│   API        │     │  APIs        │     │              │
│              │     │              │     │              │
│ - Clone repo │     │ - OpenAI     │     │ - Task state │
│ - Push branch│     │ - Anthropic  │     │ - Celery     │
│ - Create PR  │     │ - Google     │     │   broker     │
│ - PR comments│     │ - LiteLLM    │     │ - RedBeat    │
│              │     │ - Ollama     │     │   schedules  │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                     ┌──────▼──────┐
                     │    lib/     │
                     │  (core)     │
                     └─────────────┘
```

## Design principles

- **Plain data between layers** — Dicts/dataclasses, not tight coupling
- **Streaming by default** — AI output streams as it arrives
- **Explicit config** — No singletons; config passed explicitly
- **Path-safe operations** — All file ops go through `meta/tools/filesystem.py`
- **Idempotent updates** — PR resume updates existing branch/body/comments

## Key file paths

| Purpose | Path |
|---|---|
| Hand base class | `src/helping_hands/lib/hands/v1/hand/base.py` |
| Iterative hands | `src/helping_hands/lib/hands/v1/hand/iterative.py` |
| CLI hand base | `src/helping_hands/lib/hands/v1/hand/cli/base.py` |
| Config | `src/helping_hands/lib/config.py` |
| GitHub integration | `src/helping_hands/lib/github.py` |
| Filesystem tools | `src/helping_hands/lib/meta/tools/filesystem.py` |
| Tool registry | `src/helping_hands/lib/meta/tools/registry.py` |
| CLI entry | `src/helping_hands/cli/main.py` |
| Server entry | `src/helping_hands/server/app.py` |
| MCP server | `src/helping_hands/server/mcp_server.py` |

---

*Last updated: 2026-03-04*
