# v100 - Docs and testing improvements

**Status:** in-progress
**Created:** 2026-03-07

## Tasks

- [x] Consolidate v99 into completed/2026-03-07.md
- [x] Add `_commit_message_from_prompt` edge case tests (punctuation variants, prefix stripping, single-char text)
- [x] Add `_parse_output` edge case tests (inline body marker, whitespace handling, late title, internal blank lines)
- [x] Add `_build_prompt`/`_build_commit_message_prompt` edge case tests (whitespace-only summary, guidance validation)
- [x] Add `default_prompts.py` structural validation tests (directive uniqueness, numbered steps, guard ordering, safety note, script references, python version, reasonable length)
- [x] Add doc structure validation tests (CLAUDE.md build commands, README.md sections/backends, AGENT.md ground rules/auto-update markers, active plan structure)
- [x] Update testing-methodology.md coverage count (2905 -> 2972 tests)
- [x] Update PLANS.md to reference active plan
- [x] Update QUALITY_SCORE.md pr_description and default_prompts coverage notes

## Completion criteria

- [x] All new tests pass (2972 passed, 0 failed)
- [x] `uv run ruff check .` and `uv run ruff format --check .` pass
- [x] Coverage count updated in testing-methodology.md
- [x] PLANS.md references this plan
