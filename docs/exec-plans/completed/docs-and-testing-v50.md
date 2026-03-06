# Execution Plan: Docs and Testing v50

**Status:** Completed
**Created:** 2026-03-06
**Completed:** 2026-03-06
**Goal:** Improve frontend test coverage by exporting and testing pure utility functions, adding component-level render tests with @testing-library/react.

---

## Tasks

### Phase 1: Export and test frontend utility functions

- [x] Export `providerFromBackend`, `formatProviderName`, `repoName`, `cronFrequency` from App.tsx
- [x] Export `buildDeskSlots`, `checkDeskCollision` from App.tsx
- [x] Export `backendDisplayName`, `asRecord`, `readStringValue`, `readBoolishValue`, `readSkillsValue` from App.tsx
- [x] Write tests for all newly exported functions in App.utils.test.ts (55 new tests)

### Phase 2: Component-level render tests

- [x] Add App.test.tsx with render smoke test using @testing-library/react
- [x] Install @testing-library/dom peer dependency
- [x] Test initial form state renders correctly (repo path, prompt defaults)
- [x] Test UI structure (service health bar, dashboard toggles, task list, navigation buttons)

### Phase 3: Documentation updates

- [x] Update QUALITY_SCORE.md with new frontend coverage entries
- [x] Update docs/PLANS.md with v50 entry
- [x] Update docs/FRONTEND.md with new test file

### Phase 4: Validation

- [x] All frontend tests pass (83 passed across 2 files)
- [x] Frontend lint and typecheck pass
- [x] Backend tests still pass (1461 passed, 6 skipped)
- [x] Move plan to completed

---

## Completion criteria

- All Phase 1-4 tasks checked off
- `npm --prefix frontend run test` passes (83 tests)
- `npm --prefix frontend run lint && npm --prefix frontend run typecheck` passes
- `uv run pytest -v` passes (1461 tests)
