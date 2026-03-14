# Roadmap: PBI Skill v2

## Milestones

- ✅ **v1.0 Core** — Phases 1-2 (shipped 2026-03-14)
- 🚧 **v1.1 Complete** — Phases 3-4 (in progress)

## Phases

<details>
<summary>✅ v1.0 Core (Phases 1-2) — SHIPPED 2026-03-14</summary>

- [x] Phase 1: Skill Core + Escalation (2/2 plans) — completed 2026-03-13
- [x] Phase 2: Context-Aware DAX (5/5 plans) — completed 2026-03-14

Full phase details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

### 🚧 v1.1 Complete (In Progress)

**Milestone Goal:** Ship a clean, debt-free final version — fix all context-field bugs and deliver Deep Mode with model review, phase gates, and context re-injection.

- [ ] **Phase 3: Context Field Fixes** - Fix all .pbi-context.md schema inconsistencies across pbi-edit, pbi-diff, pbi-commit, and pbi-optimise
- [ ] **Phase 4: Deep Mode Complete** - Deliver model review phase, hard phase gates, context re-injection, and business question gate in deep mode

## Phase Details

### Phase 3: Context Field Fixes
**Goal**: All `.pbi-context.md` field writes are schema-consistent across every subcommand, so pbi-error can correctly correlate context after any workflow
**Depends on**: Phase 2
**Requirements**: DEBT-01, DEBT-02, DEBT-03
**Success Criteria** (what must be TRUE):
  1. User running pbi-edit sees `Measure:` (not `Entity:`) written to `## Last Command` in `.pbi-context.md`
  2. User running pbi-diff or pbi-commit sees `Measure:` field written to `## Last Command`
  3. User running pbi-optimise sees Command History rows written as `timestamp | command | measure | outcome`, matching the schema
  4. pbi-error correctly correlates the last-edited measure after an edit, diff, commit, or optimise session
**Plans**: 2 plans

Plans:
- [ ] 03-01-PLAN.md — Fix edit.md (DEBT-01) and optimise.md (DEBT-03) context write instructions
- [ ] 03-02-PLAN.md — Fix diff.md and commit.md (DEBT-02) Measure field writes

### Phase 4: Deep Mode Complete
**Goal**: Deep mode delivers a complete structured workflow — model review before any DAX, hard gates between phases, context restated at each phase start, and a final check that output answers the stated business question
**Depends on**: Phase 3
**Requirements**: PHASE-01, VERF-01, VERF-02, VERF-03
**Success Criteria** (what must be TRUE):
  1. User entering `/pbi deep` sees a model review phase that analyzes their described model and surfaces health issues (M:M relationships, missing date table, bidirectional filters) before any DAX is written
  2. Each deep-mode phase boundary is a hard gate — the session does not advance to the next phase until the user explicitly confirms
  3. Context (tables, relationships, existing measures, business question) is restated at the start of each deep-mode phase
  4. At session end, a final gate checks that the output answers the business question stated at the start of the session
  5. A user who skips confirmation at any gate cannot proceed — the gate holds until confirmed
**Plans**: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Skill Core + Escalation | v1.0 | 2/2 | Complete | 2026-03-13 |
| 2. Context-Aware DAX | v1.0 | 5/5 | Complete | 2026-03-14 |
| 3. Context Field Fixes | 1/2 | In Progress|  | - |
| 4. Deep Mode Complete | v1.1 | 0/TBD | Not started | - |
