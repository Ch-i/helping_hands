# Week 9 (Feb 24 – Mar 2, 2026)

Multi-backend expansion and frontend launch week.

---

## Feb 25 — Goose hand

- Goose CLI hand added
- Goose automated hand update (PR #18)

## Feb 26 — Provider explosion + frontend

- Goose app mode fixes, model selection fix
- Ollama provider added
- Refactoring pass
- Local CLI auth (leverage underlying terminal CLI for hands)
- Gemini initial implementation (demand spike testing issues)
- Codex local test
- Documentation updates
- React frontend added (`frontend/`)
- Better UI
- Skills system exploration
- Git issues fixed (cli git pull)
- **World view**: animated agent office scene added

**Key commits:** `6f1bcf1` add goose → `011e844` hand world agent office view

## Feb 27 — Stability

- Back to working state after integration churn
- Timeout updates
- Automated hand update (PR #47)
- Test fixes

## Feb 28 — Scheduling + frontend polish

- Better PR generation
- WASD input field fix (PR #49)
- Neuromancer-style helmet for character sprite (PR #50)
- Desk collision fix — sprite walks behind desk (PR #51)
- Cron-scheduled submission tasks (PR #52)
- Skills and tools big refactor (separated concerns)
- Safari push notifications fix
- Verbose parameter and better PR scheduling
- Ruff E501 rule removed

**Key commits:** `dc26877` better PRs → `aac58ea` big refactor separating skills and tools

## Mar 1 — Usage + concurrency

- Usage tracking/monitoring added
- Concurrency issue fixed

## Mar 2 — Frontend polish

- Frontend image assets

---

**Week summary:** Expanded from 1 backend (Claude) to 5 (Claude, Codex, Goose, Gemini, Ollama). Launched React frontend with animated office world view. Added cron scheduling, usage tracking, and skills/tools separation. 6 PRs merged via automated hand updates.
