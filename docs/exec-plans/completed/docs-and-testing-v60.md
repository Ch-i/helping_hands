# Execution Plan: Docs and Testing v60

**Status:** Completed
**Created:** 2026-03-06
**Completed:** 2026-03-06
**Goal:** Close remaining branch coverage gaps in model_provider.py, docker_sandbox_claude.py, skills/__init__.py, and registry.py; document untestable gaps; update QUALITY_SCORE.md.

---

## Tasks

### Phase 1: Backend test coverage

- [x] Close model_provider.py branch 51->55: unrecognized provider in `provider/model` format falls through to `_infer_provider_name`
- [x] Close docker_sandbox_claude.py branch 127->130: `config.verbose` is False during `_ensure_sandbox`
- [x] Close docker_sandbox_claude.py branch 268->273: `_build_failure_message` when base already contains "sandbox"
- [x] Close skills/__init__.py branches 42->47, 44->42: skill file with no `# ` heading line
- [x] Close registry.py branch 247->245: empty token after normalize in inner comma-split loop

### Phase 2: Documentation improvements

- [x] Document cli/main.py line 367 (`if __name__`) as untestable in tech-debt-tracker
- [x] Document cli/base.py branch 552->559 (heartbeat without idle timeout) in tech-debt-tracker
- [x] Update QUALITY_SCORE.md with coverage notes

### Phase 3: Validation and bookkeeping

- [x] All tests pass (1485 tests)
- [x] Update docs/PLANS.md with v60 entry
- [x] Move plan to completed

---

## Completion criteria

- model_provider.py 99% -> 100% (branch 51->55 closed)
- docker_sandbox_claude.py 99% -> 100% (branches 127->130, 268->273 closed)
- skills/__init__.py 98% -> 100% (branches 42->47, 44->42 closed)
- registry.py 99% -> 100% (branch 247->245 closed)
- cli/main.py and cli/base.py gaps documented in tech-debt-tracker
- All existing tests continue to pass
