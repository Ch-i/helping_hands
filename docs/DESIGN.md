# Design Philosophy

Core design patterns and principles for helping_hands.

## Guiding principles

1. **Plain data between layers** — Modules communicate through dicts and
   dataclasses. No tight coupling between config, repo, hands, and entry points.

2. **Streaming by default** — AI responses stream to the caller as they arrive.
   No buffering full responses unless explicitly needed.

3. **Explicit configuration** — No module-level singletons. `Config` is loaded
   once and threaded through function calls.

4. **Path safety** — All filesystem operations route through
   `meta/tools/filesystem.py` with `resolve_repo_target()` preventing
   path traversal outside the repo root.

5. **Minimal side effects** — Hands attempt commit/push/PR by default, but
   all side effects can be disabled (`--no-pr`). Execution and web tools
   are opt-in.

## Patterns

### Hand abstraction

The `Hand` base class defines the contract: `run()` for sync, `stream()` for
async iteration. Implementations are split into separate modules under
`hands/v1/hand/` to prevent monolithic growth.

### Provider resolution

Model strings like `gpt-5.2` or `anthropic/claude-sonnet-4-5` resolve through
the `ai_providers/` layer. Each provider wraps its SDK with a common interface
and lazy initialization.

### Two-phase CLI hands

CLI-backed hands (`codex`, `claude`, `goose`, `gemini`, `opencode`) run two
subprocess phases: (1) initialize/learn the repo, (2) execute the task.
This separation gives the external CLI tool repo context before acting.

Each backend customizes the shared `_TwoPhaseCLIHand` base through hook methods:

| Hook method | Purpose | Example backends |
|---|---|---|
| `_apply_backend_defaults()` | Inject CLI-specific flags before execution | All CLI hands |
| `_retry_command_after_failure()` | Return a modified command to retry on known errors | Claude (root permission), Gemini (model not found) |
| `_build_failure_message()` | Parse CLI output into actionable error messages | All CLI hands |
| `_fallback_command_when_not_found()` | Try alternate command when primary is missing | Claude (`npx` fallback) |
| `_resolve_cli_model()` | Filter or transform model names for the target CLI | Claude (rejects GPT models), OpenCode (preserves provider/model) |

#### Backend-specific behaviors

- **Claude Code** (`claude.py`): Injects `--dangerously-skip-permissions` (disabled
  for root), uses `--output-format stream-json` with `_StreamJsonEmitter` for
  structured progress parsing, falls back to `npx @anthropic-ai/claude-code` when
  `claude` binary is not found. Retries without skip-permissions on root-privilege
  errors. Detects write-permission prompt markers to surface non-interactive failures.

- **Codex** (`codex.py`): Injects `--sandbox` mode (defaults to `workspace-write`,
  switches to `danger-full-access` inside Docker containers) and
  `--skip-git-repo-check`. Normalizes bare `codex` command to `codex exec`.

- **Gemini** (`gemini.py`): Injects `--approval-mode auto_edit`. Requires
  `GEMINI_API_KEY` at subprocess env build time. Retries with `--model` stripped
  when the CLI reports model-not-found errors. Extracts model names from
  `models/<name>` patterns in error output.

- **Goose** (`goose.py`): Normalizes provider names (e.g. `gemini` to `google`),
  infers provider from model name prefixes, normalizes `OLLAMA_HOST` URLs.

- **OpenCode** (`opencode.py`): Preserves `provider/model` format for model
  resolution (no provider inference needed). Minimal hook surface.

- **Docker Sandbox Claude** (`docker_sandbox_claude.py`): Extends `ClaudeCodeHand`
  to run inside a Docker Desktop microVM sandbox (`docker sandbox create` /
  `docker sandbox exec`).  The workspace directory is synced at the same absolute
  path.  Sandbox names are auto-generated and cached per instance.  Cleanup is
  controlled by `HELPING_HANDS_DOCKER_SANDBOX_CLEANUP` (default: auto-remove).
  Requires Docker Desktop with the `docker sandbox` CLI plugin.

### Two-phase lifecycle and IO loop

The `_run_two_phase` method orchestrates the full CLI hand execution lifecycle:

1. **Skill catalog staging** — `_stage_skill_catalog()` copies selected skill
   Markdown files to a temp directory; `_cleanup_skill_catalog()` removes them
   in a `finally` block (guaranteed even on exception).
2. **`_run_two_phase_inner`** — runs the init and task subprocess phases.
3. **`_invoke_backend`** — the default delegates to `_invoke_cli`, which calls
   `_invoke_cli_with_cmd`.  Backends override this to inject custom behavior
   (e.g. Claude wraps with `_StreamJsonEmitter`, Docker Sandbox wraps with
   `_wrap_sandbox_exec`).

The subprocess IO loop (`_invoke_cli_with_cmd`) manages:

- **Idle timeout** — if no output arrives for `_idle_timeout_seconds()`, the
  process is terminated and a `RuntimeError` is raised.
- **Heartbeat messages** — emitted every `_heartbeat_seconds()` during idle
  periods so callers know the process is still alive.
- **Interrupt handling** — if `_is_interrupted()` returns `True` during the
  read loop, the active process is terminated and the loop exits.
- **Fallback/retry** — on `FileNotFoundError`, `_fallback_command_when_not_found()`
  provides an alternate command; on non-zero exit, `_retry_command_after_failure()`
  can return a modified command for one retry.

Docker Sandbox (`DockerSandboxClaudeCodeHand`) extends this lifecycle by
wrapping `_run_two_phase` with sandbox creation/cleanup:

```
_ensure_sandbox(emit)  →  super()._run_two_phase(...)  →  _remove_sandbox(emit)
```

The sandbox is only removed when `_should_cleanup()` returns `True` (controlled
by `HELPING_HANDS_DOCKER_SANDBOX_CLEANUP`).

### PR description and commit message generation

The `pr_description` module (`hands/v1/hand/pr_description.py`) generates rich
PR titles/bodies and commit messages by invoking a CLI tool (e.g. `claude -p`)
against the git diff.  Key design choices:

- **Opt-in with graceful fallback** — when no CLI is available or generation
  fails, the system falls back to heuristic message derivation from the task
  prompt/summary.
- **Diff truncation** — diffs are capped at configurable limits (12k chars for
  PR descriptions, 8k for commit messages) to stay within model context.
- **Structured output parsing** — CLI output must contain `PR_TITLE:` /
  `PR_BODY:` or `COMMIT_MSG:` markers; unparseable output is silently skipped.
- **Environment-controlled** — timeout, diff limit, and disable toggle are all
  configurable via `HELPING_HANDS_*` env vars.

### Scheduled task management

The `schedules` module (`server/schedules.py`) provides cron-based recurring
task execution using RedBeat for Redis-backed persistence.  Key design choices:

- **Dataclass-driven** — `ScheduledTask` is a plain dataclass serialized to/from
  JSON in Redis.  No ORM or database schema required.
- **Dual storage** — schedule metadata lives in Redis keys
  (`helping_hands:schedule:meta:{id}`); the actual cron trigger lives in RedBeat's
  scheduler entries.  The two are kept in sync by `ScheduleManager` CRUD methods.
- **Lazy dependency checks** — `redbeat` and `croniter` are optional imports
  guarded by `_check_redbeat()` / `_check_croniter()`.  The rest of the server
  works without them; only schedule endpoints require the extras.
- **Cron presets** — common patterns (`daily`, `hourly`, `weekdays`, etc.) are
  resolved from `CRON_PRESETS` before validation, so users can pass human-readable
  names instead of raw cron strings.
- **Trigger-now** — `trigger_now()` dispatches an immediate Celery task using the
  schedule's saved parameters, recording the run in metadata.

### Health checks and server config

The FastAPI server exposes `/health` (basic liveness) and `/health/services`
(per-service connectivity) endpoints.  Each backing service has a dedicated
probe function:

| Probe | Mechanism | Returns |
|---|---|---|
| `_check_redis_health` | `redis.Redis.from_url(...).ping()` with 2 s timeout | `"ok"` / `"error"` |
| `_check_db_health` | `psycopg2.connect(DATABASE_URL)` with 3 s timeout | `"ok"` / `"error"` / `"na"` (no `DATABASE_URL`) |
| `_check_workers_health` | `celery_app.control.inspect(timeout=2).ping()` | `"ok"` / `"error"` |

All probes catch broad `Exception` so a single failing service never crashes the
health endpoint.  Dependencies (`redis`, `psycopg2`) are imported locally inside
the probe functions to keep them soft-optional.

`_is_running_in_docker()` detects container environments via `/.dockerenv` file
presence or the `HELPING_HANDS_IN_DOCKER` env var.  The `/config` endpoint
exposes this to the frontend so it can default `use_native_cli_auth` accordingly.

Flower integration (`_fetch_flower_current_tasks`) is also soft-optional:
when `HELPING_HANDS_FLOWER_API_URL` is unset the helper returns an empty list.
When configured, it merges Flower task data with Celery inspect results via
`_upsert_current_task`, preferring the highest-priority status and merging
source labels.

### GitHub client abstraction

`GitHubClient` (`lib/github.py`) wraps PyGithub behind a convenience layer
that encapsulates authentication, git operations, and PR management.  Key
design choices:

- **Context manager** — `GitHubClient` implements `__enter__/__exit__` so
  callers can release resources deterministically.
- **Static git helpers** — operations that only shell out to `git` (clone,
  branch, pull, fetch, add/commit, set identity) are `@staticmethod` so they
  don't require a token.
- **Token resolution** — constructor looks up `GITHUB_TOKEN`, then `GH_TOKEN`,
  then an explicit kwarg.  Missing token raises immediately.
- **Check run aggregation** — `get_check_runs()` distills individual run
  results into an overall conclusion: `no_checks`, `pending`, `success`,
  `failure`, or `mixed` (all completed but not all success/failure).
- **Marker-based PR comments** — `upsert_pr_comment()` creates or edits a
  single comment identified by an HTML-comment marker.  The marker is appended
  only when not already present in the body, preventing duplication.

### Finalization

Commit/push/PR logic is centralized in the `Hand` base class so all backends
share the same branch naming, token auth, and PR body generation.

Key resilience patterns:

- **whoami fallback** — when `gh.whoami()` fails (network error, bad token),
  `token_user` defaults to `""` and the PR description update is skipped
  rather than failing the entire push.
- **precommit cleanup** — if pre-commit reformats code and the result matches
  HEAD (no net changes), the finalization returns `no_changes` instead of
  attempting an empty commit.
- **default_branch fallback** — if `get_repo()` raises when fetching the
  remote's default branch, the system falls back to `_default_base_branch()`
  (usually `"main"`) rather than crashing.

### Meta tools layer

The `meta/tools/` package provides a unified, path-safe tool layer shared by
iterative hands and the MCP server.  It is organized into four submodules with
a single `__init__.py` re-exporting the full public surface (21 symbols):

| Submodule | Responsibility | Key types |
|---|---|---|
| `filesystem.py` | Path-confined file I/O | `resolve_repo_target`, `read_text_file`, `write_text_file`, `mkdir_path`, `path_exists` |
| `command.py` | Subprocess execution (Python/Bash) | `CommandResult`, `run_python_code`, `run_python_script`, `run_bash_script` |
| `registry.py` | Tool category definitions and routing | `ToolCategory`, `ToolSpec`, `build_tool_runner_map`, `format_tool_instructions` |
| `web.py` | Web search and browsing | `WebSearchResult`, `WebBrowseResult`, `search_web`, `browse_url` |

Design choices:

- **Path confinement** — `resolve_repo_target()` resolves user-supplied paths
  against a repo root and rejects traversal attempts (`../`).  All file
  operations in hands and MCP call this before touching the filesystem.
- **Opt-in activation** — execution tools and web tools are disabled by default.
  Hands check `_execution_tools_enabled()` / `_web_tools_enabled()` before
  dispatching `@@TOOL` requests.
- **Runner dispatch** — `build_tool_runner_map()` returns a dict mapping
  `"category.action"` strings to runner callables.  The iterative hand loop
  routes `@@TOOL` requests through this map.
- **Format helpers** — `format_tool_instructions()` generates the `@@TOOL`
  reference text injected into the system prompt.
  `format_tool_instructions_for_cli()` produces a condensed variant for CLI
  hands that pass tool docs via `--init-prompt`.

### Skill catalog

Skills (`meta/skills/`) are composable knowledge bundles — Markdown files
injected into hand prompts via `--skills`.  Unlike tools (callable capabilities),
skills carry no executable code.  Key design choices:

- **Pure knowledge artifacts** — skills are `.md` files discovered from
  `catalog/*.md` at import time via `_discover_catalog()`.  No code execution,
  no side effects.
- **Opt-in selection** — `normalize_skill_selection()` resolves user-provided
  skill names (strings or tuples) against the discovered catalog.  Unknown
  skills are silently ignored rather than raising errors.
- **Temporary staging** — CLI hands call `stage_skill_catalog()` to copy
  selected skill files into a temp directory before subprocess execution, then
  `_cleanup_skill_catalog()` removes them in a `finally` block.  This avoids
  leaking skill content into the repo working tree.
- **Graceful degradation** — if the catalog directory is missing or empty,
  `_discover_catalog()` returns an empty dict.  Skill-related prompts are
  simply omitted when no skills are selected.

### Error recovery patterns

The codebase applies a consistent set of error recovery strategies across
modules.  These are not ad-hoc — each pattern addresses a specific class of
failure and keeps the user-facing flow moving.

| Pattern | Where used | Behavior |
|---|---|---|
| **Exception suppression with fallback** | `_update_pr_description`, `_skip_permissions_enabled` | Wrap optional enhancement in `try/except`; on failure, silently fall back to a simpler path instead of crashing the overall operation |
| **Retry with modified command** | `_retry_command_after_failure` (Claude root error, Gemini model-not-found) | On specific CLI errors, re-invoke with a modified command (e.g. strip `--dangerously-skip-permissions`, drop `--model`) rather than failing immediately |
| **Fallback command** | `_fallback_command_when_not_found` (Claude `npx` fallback) | When the primary CLI binary is missing (`FileNotFoundError`), try an alternative command before giving up |
| **Graceful degradation** | `_discover_catalog` (empty dir), `_check_*_health` probes, `_has_*_auth` checks | Return a safe default (empty dict, `"error"`, `False`) when optional dependencies or resources are unavailable, rather than raising |
| **Default branch fallback** | `_finalize_repo_pr` | When the remote API fails to provide the default branch, fall back to `_default_base_branch()` (`"main"`) |
| **Platform capability detection** | `_skip_permissions_enabled` (`os.geteuid`) | Use `getattr` + `callable` checks before invoking platform-specific APIs; gracefully degrade on platforms where the API is absent |
| **Idle timeout with heartbeat** | CLI IO loop (`_invoke_cli_with_cmd`) | Emit periodic heartbeat messages during long-running subprocesses; terminate only after a configurable idle threshold, not on first silence |
| **Async fallback chains** | `BasicAtomicHand.stream()` | Try `async for`, then `await`, then sync `run()` — three progressively simpler execution paths for agent output that may or may not be async |

Guiding principle: **fail narrowly, not broadly**.  A failure in PR description
generation should not prevent the commit.  A missing health check dependency
should not crash the server.  Each recovery boundary is placed at the narrowest
scope where the failure can be contained.

## Anti-patterns to avoid

- **Global state** — No module-level caches or singletons
- **Cross-layer imports** — CLI/server should not import each other's internals
- **Monolithic files** — Keep hand implementations in separate modules
- **Implicit auth** — Always use explicit token-based push, never OS credential prompts
