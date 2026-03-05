# Execution Plan: Docs and Testing v31

**Status:** Completed
**Created:** 2026-03-05
**Completed:** 2026-03-05
**Goal:** Fix ARCHITECTURE.md table formatting; add Claude CLI hand edge-case tests for _StreamJsonEmitter and _invoke_claude/_invoke_backend async methods.

---

## Tasks

### Phase 1: Documentation fixes

- [x] ARCHITECTURE.md — merge dangling Docker sandbox entry into the Key file paths table

### Phase 2: _StreamJsonEmitter edge case tests

- [x] Empty text block in assistant event (skipped, not emitted)
- [x] Result event without cost/duration (no api summary emitted)
- [x] Result event with only cost (partial api summary)
- [x] User tool_result with empty string content (skipped)
- [x] User event with non-tool_result block (skipped)
- [x] Content list with non-dict items in tool_result (skipped)
- [x] Flush on already-empty buffer (no-op)
- [x] Multiple newlines in single chunk (processes all lines)
- [x] Unknown event type produces no output

### Phase 3: _invoke_claude / _invoke_backend async tests

- [x] _invoke_claude wires up _StreamJsonEmitter and returns result_text
- [x] _invoke_claude falls back to raw output when no result event parsed
- [x] _invoke_backend delegates to _invoke_claude

### Phase 4: Validation

- [x] All tests pass (1256 passed, 6 skipped)
- [x] Lint and format clean
- [x] Update docs/QUALITY_SCORE.md
- [x] Update docs/PLANS.md
- [x] Move plan to completed

---

## Completion criteria

- All Phase 1-4 tasks checked off
- `uv run pytest -v` passes
- `uv run ruff check . && uv run ruff format --check .` passes
