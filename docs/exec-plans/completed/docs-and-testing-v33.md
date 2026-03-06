# Execution Plan: Docs and Testing v33

**Status:** Completed
**Created:** 2026-03-06
**Completed:** 2026-03-06
**Goal:** Add schedule module edge case tests; update DESIGN.md with scheduling pattern.

---

## Tasks

### Phase 1: Schedule module edge case tests

- [x] `trigger_now` happy path (mocked celery task)
- [x] `trigger_now` with missing schedule returns None
- [x] `trigger_now` dispatches with correct task parameters
- [x] `get_schedule_manager` function returns ScheduleManager instance
- [x] `create_schedule` with `enabled=True` calls `_create_redbeat_entry`
- [x] `create_schedule` with `enabled=False` skips `_create_redbeat_entry`
- [x] `update_schedule` with `enabled=True` calls `_create_redbeat_entry`
- [x] `update_schedule` with `enabled=False` skips `_create_redbeat_entry`
- [x] `_create_redbeat_entry` raises ValueError for non-5-part cron
- [x] `_create_redbeat_entry` raises ValueError for >5 cron parts
- [x] `_delete_redbeat_entry` handles KeyError gracefully
- [x] `_delete_redbeat_entry` calls entry.delete() on success
- [x] `list_schedules` filters out None entries
- [x] `list_schedules` returns empty for no keys
- [x] `from_dict` roundtrip preserves `fix_ci` and `ci_check_wait_minutes`
- [x] `from_dict` defaults `fix_ci` to False
- [x] `from_dict` roundtrip preserves `use_native_cli_auth`
- [x] All tests verified (existing + new edge cases pass)

### Phase 2: Documentation updates

- [x] DESIGN.md -- add scheduling pattern section

### Phase 3: Validation

- [x] All tests pass (1473 passed)
- [x] Lint and format clean
- [x] Update docs/QUALITY_SCORE.md
- [x] Update docs/PLANS.md
- [x] Move plan to completed

---

## Completion criteria

- All Phase 1-3 tasks checked off
- `uv run pytest -v` passes
- `uv run ruff check . && uv run ruff format --check .` passes
