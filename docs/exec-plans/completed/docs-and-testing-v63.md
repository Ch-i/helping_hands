# Execution Plan: Docs and Testing v63

**Status:** Completed
**Created:** 2026-03-06
**Goal:** Consolidate v32-v62 plans into 2026-03-06.md; add shared CLI hand factory fixture to conftest.py; refactor CLI hand tests to use it; update docs indexes.

---

## Tasks

### Phase 1: Plan consolidation

- [x] Consolidate v32-v62 plans into `completed/2026-03-06.md`
- [x] Remove individual v32-v62 plan files

### Phase 2: Shared test fixtures

- [x] Add `make_cli_hand` factory fixture to `tests/conftest.py`
- [x] Refactor test_cli_hand_claude.py to use shared fixture
- [x] Refactor test_cli_hand_codex.py to use shared fixture
- [x] Refactor test_cli_hand_gemini.py to use shared fixture
- [x] Refactor test_cli_hand_opencode.py to use shared fixture
- [x] Refactor test_docker_sandbox_claude.py to use shared fixture

### Phase 3: Documentation updates

- [x] Update PLANS.md with v63 and consolidated references
- [x] All tests pass

### Phase 4: Finalize

- [x] Move plan to completed

---

## Completion criteria

- v32-v62 plans consolidated into `completed/2026-03-06.md` (31 files -> 1)
- CLI hand test files use shared `make_cli_hand` factory from conftest.py
- All tests pass (1485 tests, 6 skipped)
- PLANS.md updated
