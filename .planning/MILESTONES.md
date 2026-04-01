# Milestones

## v1.2 Quality & Distribution (Shipped: 2026-04-01)

**Phases completed:** 6 phases, 13 plans, 23 tasks

**Key accomplishments:**

- Bare /pbi router skill using category menu (A/B/C/D) and inline keyword intent mapping across all 10 pbi subcommands
- General-purpose PBIP model editor with 7-step workflow: entity resolution with fuzzy-match, pre-write checklist (Desktop + unappliedChanges.json + indentation), Before/After preview with capital-N default, and auto-commit with conventional prefixes
- Status:
- Three UTF-8-safe Python subcommands added to detect.py (html-parse, version-check, gitignore-check) replacing grep/sed shell pipelines in format.md, help.md, and diff.md
- grep -rlF eliminated from edit.md and comment.md (replaced with detect.py search), plus TMSL offset/limit chunked-read guards added to both files for token overflow prevention
- grep -rlF eliminated from error.md and new.md; both TMSL branches now guard against reading large model.bim files without chunking
- Eliminated all grep/sed shell commands from format.md, help.md, and diff.md by routing through detect.py Python subcommands (html-parse, version-check, gitignore-check) completing the UTF8-02 and UTF8-03 requirements
- TMSL chunked-read guard added to load.md Step 2, ensuring large model.bim files are read in 1000-line chunks to prevent token overflow
- Bundled CHANGELOG.md (v1.0.0-v4.3.0) with offline /pbi version command using detect.py version-check and Read tool
- Task 1 — SKILL.md routing table:
- Extracted inline Settings Handler into dedicated /pbi:settings sub-skill with disable-model-invocation, commands stub, and installer coverage
- Session-start format standardised to `

---

## v1.1 Complete (Shipped: 2026-03-14)

**Phases completed:** 2 phases (Phase 3: Context Field Fixes, Phase 4: Deep Mode Complete)
**Plans:** 4 | **Requirements shipped:** 7/7 v1.1 | **Files changed:** 21 | 3,039 insertions

**Key accomplishments:**

- Fixed pbi-edit Step 7: `Measure:` field (locked four-line format) replaces `Entity:` — closes DEBT-01 ERR-02 cross-phase degradation
- Fixed pbi-diff and pbi-commit Step 5: actual measure names written to `Measure:` field, replacing `(git operation)` placeholder — closes DEBT-02
- Fixed pbi-optimise Step 9: Command History rows reordered to `timestamp | command | measure | outcome` schema — closes DEBT-03
- Rewrote deep.md as four-phase structured workflow (Phase A intake → Gate A→B → Phase B model review → Gate B→C → Phase C DAX → Phase D verification) — closes PHASE-01
- Hard phase gates with three-branch logic (continue/cancel/re-output) — "ok" and "sounds good" now re-output the gate prompt, preventing soft-gate bypass — closes VERF-01/VERF-02/VERF-03
- Added Group 5 acceptance scenarios (S5-01 to S5-08) covering all Phase 4 requirements

**Archives:**

- `.planning/milestones/v1.1-ROADMAP.md`
- `.planning/milestones/v1.1-REQUIREMENTS.md`

---

## v1.0 Core (Shipped: 2026-03-14)

**Phases completed:** 2 phases (Phase 1: Skill Core + Escalation, Phase 2: Context-Aware DAX)
**Plans:** 7 | **Requirements shipped:** 12/16 v1 (Phase 3 requirements deferred to v1.1)

**Key accomplishments:**

- SKILL.md v4.0 rewrite: solve-first catch-all default, 2-step escalation on failure signals, `/pbi deep` entry point
- 19 manual acceptance scenarios covering solve-first, escalation paths, deep mode intake (Phase 1 test suite)
- `new.md` upgraded: universal model context intake (Step 0.5), always-on duplication check, filter-sensitive pattern gate with Visual Context write-back
- Step 0.5 model context check added to `explain`, `format`, `optimise` — grounding DAX in table context, non-blocking variant in `format`
- Step 0.5 context intake added to `comment` and `error` — skips when context already recorded
- Measures Gate (`deep.md` Step 4) — terminal session review that restates business question, requires confirmation before closing

**Tech debt deferred:**

- pbi-edit writes `Entity:` not `Measure:` to session context (cross-phase ERR-02 degradation)
- pbi-diff / pbi-commit omit `Measure:` field (stale pbi-error correlation)
- pbi-optimise Command History row format misaligned with schema

**Archives:**

- `.planning/milestones/v1.0-ROADMAP.md`
- `.planning/milestones/v1.0-REQUIREMENTS.md`
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md`

---
