# Plans

Index of execution plans for helping_hands development.

## Active plans

_No active plans._

## Completed plans

### Week 10 (Mar 3–9, 2026) — Docs, testing, and automation

- [v103 - Playwright integration tests](exec-plans/completed/v103-playwright-integration-tests.md) --
  25 Playwright e2e tests (smoke, submission, schedule, monitor, world view); CI job added; TODO.md completed
- [2026-03-07 consolidated](exec-plans/completed/2026-03-07.md) --
  v80-v102: 28 design docs, massive docs validation test suite, provider tests, Config edge cases, plan consolidation; 1740 -> 3031 tests
- [2026-03-06 consolidated](exec-plans/completed/2026-03-06.md) --
  v32-v79: PR description, schedule, E2E, server health, Docker sandbox, celery usage, frontend 82.3%, shared conftest fixtures, 21 design docs; 1263 -> 1717 tests
- [2026-03-05 consolidated](exec-plans/completed/2026-03-05.md) --
  v5-v31: CLI hand, AI provider, iterative hand, Docker sandbox, celery, MCP, web tool, PR description test suites; provider abstraction design doc; 470 -> 1256 tests
- [2026-03-04 consolidated](exec-plans/completed/2026-03-04.md) --
  v1-v4: Established docs structure, product specs, hand abstraction design doc, iterative hand tests, SECURITY.md sandboxing; 50 -> 470 tests
- [2026-03-03](exec-plans/completed/2026-03-03.md) --
  OpenCode hand, prompt in task inputs, merged schedule/skills/usage/concurrency branch

### Earlier weeks

- [Week 9 (Feb 24 – Mar 2)](exec-plans/completed/2026/Week-9.md) --
  Multi-backend expansion (Goose, Gemini, Ollama), React frontend launch, animated office world view, cron scheduling, usage tracking, skills/tools refactor
- [Week 8 (Feb 21–23)](exec-plans/completed/2026/Week-8.md) --
  Project inception: Hand abstraction, AI providers, Celery, MCP server, GitHub integration, Claude Code CLI, E2E flow

## How plans work

1. Plans are created in `docs/exec-plans/active/` with a descriptive filename
2. Each plan has a status, creation date, tasks, and completion criteria
3. When all tasks are done, the plan moves to `docs/exec-plans/completed/`
4. The tech debt tracker (`docs/exec-plans/tech-debt-tracker.md`) captures
   ongoing technical debt items that don't warrant a full plan
