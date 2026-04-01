# Retrospective: PBI Skill v2

---

## Milestone: v1.0 — Core

**Shipped:** 2026-03-14
**Phases:** 2 (Phase 1: Skill Core + Escalation, Phase 2: Context-Aware DAX) | **Plans:** 7

### What Was Built

- SKILL.md v4.0 with progressive friction (solve-first, escalate on failure signals only)
- `/pbi deep` entry point for explicit deep mode invocation
- Model context intake (Step 0.5) added to all 6 DAX subcommands
- Always-on duplication check in `new.md`
- Filter-sensitive pattern gate with visual context write-back in `new.md`
- Measures Gate in `deep.md` — session-end review tied to business question

### What Worked

- **Inversion of the core model** (interrogation-first → solve-first) was validated in Phase 1 acceptance tests. The progressive friction pattern is clearly the right model for daily-use tooling.
- **Step 0.5 as a universal pattern** worked across all 6 subcommands with minimal friction — the skip-if-present logic prevents re-asking in multi-command sessions.
- **Phase 2 execution velocity**: 5 plans in ~30 min total (6 min/plan avg). Research-then-implement with tight scope is the right execution model for skill file changes.
- **Acceptance scenarios before implementation** (Plan 02-01 first): having 14 pass criteria written before touching code made the implementation targets unambiguous.

### What Was Inefficient

- **ROADMAP.md plan checkboxes not updated after execution**: the gsd-tools and VERIFICATION.md had the right state, but the human-readable plan checkboxes stayed stale. Created noise in the milestone audit.
- **REQUIREMENTS.md Phase 1 checkboxes**: 7 Phase 1 requirements stayed unchecked even after Phase 1 was verified complete. Caused a false "5/11 checked" reading at milestone completion.
- **STATE.md fragmentation**: two frontmatter blocks from different projects stacked in one file. Messy but functional.

### Patterns Established

- **Step 0.5 placement**: always after `## Instructions` header, before Step 1; always skip if `## Model Context` section present
- **Duplication check placement**: after Step 1 (intent recognition), before DAX generation
- **Filter-sensitive gate**: keyword-triggered, blocks generation until visual placement confirmed
- **Measures gate**: fires only on explicit user completion signal (not per-measure); restates business question

### Key Lessons

1. **Write acceptance tests before implementation plans** — had to do this explicitly (Plan 02-01 first in Phase 2). Should be a default step in every phase plan.
2. **Update requirement checkboxes at phase completion** — don't let them go stale. The verification step should include a REQUIREMENTS.md update.
3. **The solve-first pattern is contagious** — once implemented in the skill, it became the obvious model for everything. Don't overthink the design; ship and iterate.
4. **Tech debt is predictable at phase boundary**: all 3 v1.0 known issues (field name mismatches in `.pbi-context.md`) were identified by the integration audit. Future audits at phase boundaries prevent milestone-level surprises.

### Cost Observations

- Model mix: balanced profile (Sonnet default, Haiku for file ops)
- Sessions: ~4 sessions across 2 days
- Notable: Phase 2 executed in a single session at high velocity — tight scope + existing patterns from Phase 1 = fast execution

---

## Milestone: v1.1 — Complete

**Shipped:** 2026-03-14
**Phases:** 2 (Phase 3: Context Field Fixes, Phase 4: Deep Mode Complete) | **Plans:** 4

### What Was Built

- Locked four-line `## Last Command` block with `- Field:` bullet syntax across edit, optimise, diff, commit — closed all three context-schema bugs from v1.0 audit
- Four-phase deep mode workflow: Phase A (context intake), Gate A→B, Phase B (model review), Gate B→C, Phase C (DAX development), Phase D (final verification)
- Hard gate three-branch logic (exact token / cancel / re-output) — prevents soft-gate bypass
- Context re-injection blocks at Phase B, C, D starts to prevent context drift
- 8 acceptance scenarios (S5-01 to S5-08) covering PHASE-01, VERF-01, VERF-02, VERF-03

### What Worked

- **Tight scope execution**: 4 plans, ~7 min total (Phase 3: ~2 min, Phase 4: ~4 min). Clear bug descriptions + locked solution patterns = near-zero planning overhead.
- **Three-branch gate pattern**: Articulating the third branch (re-output on unmatched input) as the distinguishing feature of a *hard* gate resolved the design immediately. The insight "two-branch gates are soft gates" is a reusable heuristic.
- **Acceptance scenarios as completion signal**: Writing S5-01 to S5-08 in Plan 02 made Phase 4 completion unambiguous without requiring live PBI Desktop tests.
- **Locked `- Field:` bullet syntax**: Single change to instruction format eliminated an entire class of field-name ambiguity bugs. Generalizes to any context-write instruction.

### What Was Inefficient

- **v1.1-MILESTONE-AUDIT.md not created before close**: The v1.0 audit was available but no v1.1 audit was run before milestone completion. Low risk given the small scope, but the audit step provides value even for 2-phase milestones.
- **ROADMAP.md plan checkboxes stayed `[ ]` through phase execution**: Same pattern from v1.0 — the phase summary and VERIFICATION.md had the right state but the roadmap plan checkboxes were never updated. Minor noise.

### Patterns Established

- **Locked context-write format**: All future subcommands that update `## Last Command` should use the locked four-line `- Field:` bullet format — never prose, never `Field = value`
- **Hard gate structure**: Three branches always: (1) exact affirmative token → proceed, (2) cancel → stop, (3) anything else → re-output the full gate prompt. Never two-branch.
- **Acceptance scenarios before plan close**: Last plan of each phase should include or reference the acceptance scenario group for that phase. Serves as verifiable completion criteria without live tool access.

### Key Lessons

1. **"Two-branch gates are soft gates"** — the third branch (re-output on unmatched input) is what makes a gate hard. This is the key design insight from Phase 4.
2. **Field-name ambiguity is a class of bug** — any instruction that says "write Field = value" is a soft instruction. Lock it with `- Field: [value]` and the class disappears.
3. **Small milestones ship fast** — 2 phases, 4 plans, 7 minutes execution. Tight scope + clear bugs + existing patterns = very low friction. The overhead is in planning and closure, not execution.

### Cost Observations

- Model mix: balanced profile (Sonnet default)
- Sessions: ~2 sessions on 2026-03-14
- Notable: Both phases executed in a single day with minimal context; Phase 3 in ~2 min, Phase 4 in ~4 min — fastest v1.x milestone by far

---

## Milestone: v1.2 — Quality & Distribution

**Shipped:** 2026-03-31
**Phases:** 4 (Phase 5: Installer Overhaul, Phase 6: Token Safety + UTF-8 Hardening, Phase 7: Version History Command, Phase 8: Audit & Settings Sub-skill) | **Plans:** 11

### What Was Built

- Reworked `install.ps1` with `-Scope project|user` parameter, full 21-file manifest, dynamic version read from SKILL.md
- Python `detect.py` expanded to 15 subcommands: `html-parse`, `version-check`, `gitignore-check`, `search`, `session-check`, `settings-set`, `ensure-dir`, `migrate`, and more — replacing all grep/sed pipelines
- TMSL chunked-read guards in `load.md`, `edit.md`, `comment.md` (1000-line blocks, prevents 10K token overflow on large model.bim files)
- Bundled `CHANGELOG.md` in `shared/` with offline `/pbi:version` command — full version history without network call
- `/pbi:settings` extracted from inline handler → dedicated `settings/SKILL.md` sub-skill with `disable-model-invocation: true`
- All 20 `.claude/commands/pbi/*.md` files synced to v6.1: `.pbi/context.md` path, `ensure-dir`/`migrate`/`settings` detection, `session-check` auto-resume
- Session-start format standardised across all 21 sub-skills: `**Session-Start:** [ISO]` (the exact format `detect.py session_check()` parses)

### What Worked

- **Parallel wave execution for independent plans** (Phase 8 Wave 1: 08-01 + 08-02 in parallel) shaved significant time. For plans with no data dependency, parallel is always the right call.
- **detect.py as the extension point**: All Python-first requirements in Phase 6 fell neatly into adding new detect.py subcommands. The script as a single extension surface worked extremely well — no scattered Python inline strings in skill files.
- **Mechanical replacement tasks as sub-agent work**: The 20-file commands sync (Phase 8, Plan 02) was entirely mechanical. Delegating it to a sub-agent with a precise task spec was more reliable than doing it inline — zero missed files.
- **Session-check pattern supersedes Model Context presence check**: The v6.1 session-check pattern (detect.py session_check) is cleaner than checking for `## Model Context` in the context file. The 2-hour window logic prevents stale context reuse.

### What Was Inefficient

- **Phase 5 had only 1 plan** (05-01) vs the original scope of 2 — the installer plan was merged, which was the right call but resulted in an oddly sized phase. Minor.
- **ROADMAP.md milestone entry didn't include Phase 8** at milestone start — added late. Phase 8 was an add-on to the roadmap mid-milestone. Normal evolution, but adds noise to milestone archival.
- **commands/ files were 4 versions behind** (v4-era): The scope of Plan 08-02 (20 files, 3 changes each) was larger than anticipated because no one had been maintaining the commands/ files in sync with the skills/. Need a sync-check in the phase planning workflow.

### Patterns Established

- **detect.py as the single Python entry point**: All file operations, searches, settings reads/writes, and session management go through detect.py subcommands. Never add ad-hoc Python inline in skill files.
- **`disable-model-invocation: true` for utility sub-skills**: Any sub-skill that runs scripts only (no LLM reasoning) should use this flag to prevent accidental model invocations and save tokens.
- **Parallel agents for independent large-scale mechanical tasks**: 20+ file updates without dependencies = perfect sub-agent candidate. Use worktree isolation for parallelism.
- **Session-start format**: `**Session-Start:** [ISO 8601 UTC]` immediately after `## Model Context` heading — single line, detect.py parses line.strip().startswith('**Session-Start:**').

### Key Lessons

1. **Keep commands/ in sync with skills/ at each milestone** — a cross-check step should be part of every milestone start to catch drift before it compounds.
2. **A dedicated sub-skill per command is the right architecture** — extracting the settings handler from base SKILL.md into settings/SKILL.md resolved routing clarity and made `/pbi:settings` directly invocable. All future commands should follow the sub-skill pattern.
3. **Chunking is a must for TMSL models** — model.bim files in large PBIP projects easily exceed 10K tokens. Chunk-read at 1000 lines is the correct default for any Read tool call on model files.
4. **The 2-hour session window is the right heuristic for auto-load** — saves a model load (fast) on every command in a session while ensuring fresh context after idle gaps.

### Cost Observations

- Model mix: Sonnet primary, Haiku for file-heavy tasks (load, diff, commit)
- Sessions: ~5 sessions across 8 days (2026-03-23 → 2026-03-31)
- Notable: Phase 8 used parallel sub-agents for Wave 1 (2 agents simultaneously) — first use of worktree isolation in this project, worked cleanly

---

## Cross-Milestone Trends

| Milestone | Phases | Plans | Avg/Plan | Tech Debt Items |
|-----------|--------|-------|----------|-----------------|
| v1.0 Core | 2 | 7 | ~10 min | 3 (field schema mismatches) |
| v1.1 Complete | 2 | 4 | ~2 min | 0 (debt-clearing milestone) |
| v1.2 Quality & Distribution | 4 | 11 | ~7 min | 1 (pbi-error live test pending PBI Desktop) |

