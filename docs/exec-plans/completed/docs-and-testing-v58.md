# Execution Plan: Docs and Testing v58

**Status:** Completed
**Created:** 2026-03-06
**Completed:** 2026-03-06
**Goal:** Close claude.py _StreamJsonEmitter and _skip_permissions_enabled branch gaps, add skills normalize whitespace-only token test, fix stale server docstring, add error recovery patterns to DESIGN.md.

---

## Tasks

### Phase 1: Backend test coverage

- [x] Add claude.py _StreamJsonEmitter tests for unknown content block type and whitespace-only text preview (lines 62->55, 69->55)
- [x] Add claude.py _skip_permissions_enabled test for geteuid not callable (line 208->214)
- [x] Add skills normalize_skill_selection whitespace-only token test (line 79->77)

### Phase 2: Documentation improvements

- [x] Fix stale server/__init__.py docstring ("not yet implemented" -> actual description)
- [x] Add error recovery patterns section to docs/DESIGN.md

### Phase 3: Validation and bookkeeping

- [x] Update QUALITY_SCORE.md with coverage notes
- [x] Update docs/PLANS.md with v58 entry
- [x] All tests pass (1477 tests)
- [x] Move plan to completed

---

## Completion criteria

- claude.py coverage: 99% -> 99%+ (3 branch gaps closed: unknown block type, whitespace-only preview, geteuid not callable)
- skills/__init__.py coverage: 98% -> 98%+ (1 branch gap closed: whitespace-only token)
- DESIGN.md includes error recovery patterns section
- server/__init__.py docstring updated from stale "not yet implemented" to accurate description
- All existing tests continue to pass
