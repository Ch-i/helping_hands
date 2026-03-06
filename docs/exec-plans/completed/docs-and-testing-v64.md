# Execution Plan: Docs and Testing v64

**Status:** Completed
**Created:** 2026-03-06
**Goal:** Refactor goose hand tests to shared fixture; add conftest self-tests; update AGENTS.md; add error-handling design doc.

---

## Tasks

### Phase 1: Test improvements

- [x] Refactor test_cli_hand_goose.py to use shared `make_cli_hand` fixture from conftest.py
- [x] Add conftest fixture self-tests (repo_index, fake_config, make_cli_hand)

### Phase 2: Documentation improvements

- [x] Update AGENTS.md with Docker Sandbox agent type and scheduled task agents
- [x] Add `error-handling.md` design doc (standalone extraction from DESIGN.md patterns)
- [x] Update design-docs/index.md with new doc

### Phase 3: Finalize

- [x] All tests pass (1495 passed, 6 skipped)
- [x] Update PLANS.md
- [x] Move plan to completed

---

## Completion criteria

- test_cli_hand_goose.py uses shared `make_cli_hand` factory from conftest.py
- Conftest fixtures have dedicated test coverage (10 new tests)
- AGENTS.md reflects Docker Sandbox and scheduled agents
- Error handling design doc captures patterns from DESIGN.md
- All tests pass (1495 tests, 6 skipped)
- PLANS.md updated
