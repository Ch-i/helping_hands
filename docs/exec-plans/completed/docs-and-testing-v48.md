# Execution Plan: Docs and Testing v48

**Status:** Completed
**Created:** 2026-03-06
**Completed:** 2026-03-06
**Goal:** Close remaining CLI hand coverage gaps (claude.py, gemini.py, goose.py instance method delegation and edge cases).

---

## Tasks

### Phase 1: Claude CLI hand coverage gaps (97% -> 98%+)

- [x] Test `_should_dangerously_skip_permissions` geteuid exception path (lines 212-213)
- [x] Test `_StreamJsonEmitter.__call__` empty stripped line skip (line 32)
- [x] Test `_build_failure_message` instance delegation (line 243)

### Phase 2: Gemini CLI hand coverage gaps (98% -> 99%+)

- [x] Test `_build_failure_message` instance delegation (line 131)
- [x] Test `_invoke_gemini` async delegation (line 163)
- [x] Test `_invoke_backend` delegation to `_invoke_gemini`

### Phase 3: Goose CLI hand coverage gaps (98% -> 99%+)

- [x] Test `_resolve_goose_provider_model_from_config` bare model -> infer provider
- [x] Test `_resolve_goose_provider_model_from_config` provider/model split
- [x] Test `_resolve_goose_provider_model_from_config` default/empty model
- [x] Test `_resolve_goose_provider_model_from_config` gemini provider normalization
- [x] Test `_resolve_goose_provider_model_from_config` slash with empty model part
- [x] Test `_resolve_goose_provider_model_from_config` GPT model infers openai
- [x] Test `_invoke_backend` delegation to `_invoke_cli`

### Phase 4: Documentation updates

- [x] Update QUALITY_SCORE.md with new coverage entries
- [x] Update docs/PLANS.md with v48 entry
- [x] Move plan to completed

### Phase 5: Validation

- [x] All tests pass (1456 passed, 6 skipped)
- [x] Lint and format clean

---

## Completion criteria

- All Phase 1-5 tasks checked off
- `uv run pytest -v` passes (1456 tests)
- `uv run ruff check . && uv run ruff format --check .` passes
