# Execution Plan: Docs and Testing v27

**Status:** Completed
**Created:** 2026-03-05
**Completed:** 2026-03-05
**Goal:** Increase test coverage for DockerSandboxClaudeCodeHand (19% -> 91%) with pure/static/async method unit tests.

---

## Tasks

### Phase 1: DockerSandboxClaudeCodeHand unit tests

- [x] `_resolve_sandbox_name` — env var override
- [x] `_resolve_sandbox_name` — auto-generated from repo name
- [x] `_resolve_sandbox_name` — cached on second call
- [x] `_resolve_sandbox_name` — special characters sanitized
- [x] `_resolve_sandbox_name` — preexisting name returned
- [x] `_resolve_sandbox_name` — env var stripped
- [x] `_should_cleanup` — default (returns True)
- [x] `_should_cleanup` — set to "0" (returns False)
- [x] `_should_cleanup` — set to "1" (returns True)
- [x] `_should_cleanup` — set to "false" (returns False)
- [x] `_should_cleanup` — set to "true" (returns True)
- [x] `_wrap_sandbox_exec` — basic command wrapping
- [x] `_wrap_sandbox_exec` — env var forwarding
- [x] `_execution_mode` — returns "docker-sandbox"
- [x] `_build_failure_message` — auth detection ("not logged in")
- [x] `_build_failure_message` — auth detection ("authentication_failed")
- [x] `_build_failure_message` — generic failure with sandbox note appended
- [x] `_build_failure_message` — sandbox already in base message (no duplicate note)
- [x] `_command_not_found_message` — message format
- [x] `_fallback_command_when_not_found` — returns None
- [x] Class attributes (`_BACKEND_NAME`, `_CLI_LABEL`, `_CLI_DISPLAY_NAME`, container env vars)
- [x] `__init__` — initial state
- [x] `_docker_sandbox_available` — success (returncode 0)
- [x] `_docker_sandbox_available` — failure (returncode 1)
- [x] `_docker_sandbox_available` — FileNotFoundError
- [x] `_ensure_sandbox` — skips if already created
- [x] `_ensure_sandbox` — raises if docker not found
- [x] `_ensure_sandbox` — raises if sandbox plugin unavailable
- [x] `_ensure_sandbox` — creates sandbox successfully
- [x] `_ensure_sandbox` — raises on create failure
- [x] `_ensure_sandbox` — template env var applied
- [x] `_remove_sandbox` — skips if not created
- [x] `_remove_sandbox` — stops and removes sandbox

### Phase 2: Validation

- [x] All tests pass (1220 passed, 6 skipped)
- [x] Lint and format clean
- [x] Update `docs/QUALITY_SCORE.md` with new coverage notes
- [x] Update `docs/PLANS.md`
- [x] Move plan to completed

---

## Completion criteria

- All Phase 1-2 tasks checked off
- `uv run pytest -v` passes
- `uv run ruff check . && uv run ruff format --check .` passes
