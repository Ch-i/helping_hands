# Execution Plan: Docs and Testing v55

**Status:** Completed
**Created:** 2026-03-06
**Completed:** 2026-03-06
**Goal:** Reach 80%+ frontend statement coverage by adding tests for schedule CRUD, task polling/selection, notification/toast rendering, and worker capacity fetching.

---

## Tasks

### Phase 1: Schedule CRUD operation tests

- [x] Test edit schedule form (openEditScheduleForm with mocked GET)
- [x] Test delete schedule (confirm dialog + DELETE call, cancel confirms no DELETE)
- [x] Test trigger schedule (confirm dialog + POST trigger)
- [x] Test toggle schedule enable/disable
- [x] Test schedule items render with name and action buttons

### Phase 2: Task selection and polling tests

- [x] Test selectTask transitions to monitor view with correct state
- [x] Test task polling discovers background tasks and updates history
- [x] Test terminal task status triggers toast
- [x] Test poll error handling (non-ok response)

### Phase 3: Notification and toast tests

- [x] Test notification banner renders when permission is "default"
- [x] Test notification banner dismissal
- [x] Test toast rendering for completed tasks
- [x] Test toast close button removes toast
- [x] Test requestNotifPermission callback

### Phase 4: Fetch helpers and misc coverage

- [x] Test task discovery from /tasks/current endpoint
- [x] Test /tasks/current API failure handled gracefully
- [x] Test monitor output scroll handler
- [x] Test monitor resize handle
- [x] Test New submission button resets state from monitor view

### Phase 5: Documentation and validation

- [x] Update docs/PLANS.md with v55 entry
- [x] Update QUALITY_SCORE.md with new frontend coverage
- [x] Move plan to completed
- [x] All frontend tests pass (153 tests)

---

## Completion criteria

- Frontend test count: 134 -> 153 (19 new component tests)
- Frontend coverage: 71.5% -> 82.3% statements, 80.2% branches
- All existing tests continue to pass
