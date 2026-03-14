# PBI Skill v2

## What This Is

A Claude Code skill for Power BI development that solves DAX requests immediately by default, escalates to structured questioning only after repeated failure signals, and grounds generated measures in the user's actual model context (table names, existing measures, filter exposure).

## Core Value

Never block a data analyst — solve immediately, interrogate only when stuck or asked.

## Requirements

### Validated

- ✓ Skill defaults to solving immediately, no upfront interrogation — v1.0 (PROG-01)
- ✓ Escalation fires after 2-3 failure signals, not upfront — v1.0 (PROG-02)
- ✓ Escalation asks exactly one targeted question per gap identified — v1.0 (PROG-03)
- ✓ Deep workflow only activates when explicitly requested (`/pbi deep`) — v1.0 (PROG-04)
- ✓ Escalation extracts business question when invoked — v1.0 (INTR-01)
- ✓ Escalation gathers data model state (tables, relationships) — v1.0 (INTR-02)
- ✓ Escalation audits existing measures for duplication — v1.0 (INTR-03)
- ✓ Filter-sensitive DAX asks visual placement context before writing — v1.0 (INTR-04)
- ✓ Generated measures reference actual user-described tables/columns — v1.0 (DAX-01)
- ✓ Duplication check always fires before writing any new measure — v1.0 (DAX-02)
- ✓ Filter context warning surfaced for CALCULATE-heavy patterns without visual placement — v1.0 (DAX-03)
- ✓ Measures phase has explicit gate: confirm before session closes in deep mode — v1.0 (PHASE-02)

### Active

**v1.1 Complete:**

- [ ] **DEBT-01**: pbi-edit writes `Entity:` not `Measure:` to `## Last Command` — fix field name
- [ ] **DEBT-02**: pbi-diff and pbi-commit omit `Measure:` field — add consistent field writes
- [ ] **DEBT-03**: pbi-optimise Command History row format wrong column order — align with schema
- [ ] **PHASE-01**: Model review phase — analyze described model, flag health issues (M:M, missing date table, bidirectional filters), outputs findings before any DAX
- [ ] **VERF-01**: Phase gates — hard checkpoints between phases in deep mode, user must confirm before advancing
- [ ] **VERF-02**: Business question gate — final check that output answers the question stated at the start
- [ ] **VERF-03**: Context re-injection — explicit context summary restated at start of each phase to prevent drift

### Out of Scope

- Automated Power BI API integration — conversational skill, not a service connector
- Generic DAX tutorials — context-driven assistance, not educational content
- Free-form Q&A mode without structure — destroys phase discipline in deep mode
- OAuth / Power BI Service integration — works from described context only

## Context

**Shipped v1.0** with 2 phases, 7 plans, 2,635 LOC across skill markdown files.

The core design decision that emerged from Phase 1: the original brief asked for "interrogation first", but the skill was rebuilt with the inverse — **progressive friction** (solve-first, escalate only on failure). This is the right model for a daily-use co-pilot. The interrogation path exists but is gated behind failure signals, not upfront.

Phase 2 grounded all DAX commands in model context. Every subcommand now checks for `## Model Context` in `.pbi-context.md` and asks once if absent. The filter-sensitive gate and duplication check are always-on behaviors in `/pbi new`.

**Tech debt from v1.0:** Three cross-phase `.pbi-context.md` field consistency issues (pbi-edit writes `Entity:` not `Measure:`, pbi-diff/commit omit `Measure:`, pbi-optimise Command History row format misaligned). Priority 1 fixes for v1.1.

**Tech stack:** Claude Code skill markdown, `.pbi-context.md` for session state, TMDL/TMSL file support.

## Constraints

- **Scope**: Claude Code skill file — a `.md` prompt file that Claude reads and executes
- **Interaction**: Conversational only — no file system access to .pbix files, works from user-described context
- **Audience**: Devesh (Power BI / DAX developer using Claude Code daily)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Solve-first (progressive friction) over interrogation-first | Daily-use co-pilot should never block; interrogation only fires when stuck | ✓ Good — Phase 1 verification confirmed this is the right UX model |
| Targeted escalation (one question per gap) | Full checklist interrogation reproduces the exact failure mode being fixed | ✓ Good — acceptance tests confirm gap-targeted questioning works |
| `*` wildcard catch-all in routing table | Ensures any DAX request is handled without an empty-args bounce | ✓ Good — no edge cases found in testing |
| Step 0.5 placement: after `## Instructions`, before Step 1 | Context intake must happen before any action but after router | ✓ Good — consistent across all 5 subcommands |
| Skip Step 0.5 when `## Model Context` already present | Prevents redundant re-asking across commands in same session | ✓ Good — smooths multi-command sessions |
| Duplication check always-on (not optional) | Opt-in check would be skipped; always-on prevents silent duplication | ✓ Good — fires reliably without user action |
| Filter-sensitive keyword list includes natural language phrases | DAX function names alone miss user-phrased requests like "over time" | ✓ Good — catches more patterns |
| Measures gate fires only on analyst completion signal | Per-measure gating would be disruptive; end-of-session review is less friction | ✓ Good — confirmed in Phase 2 smoke tests |
| Model after GSD structure | User explicitly identified GSD as the reference for quality | — Pending (Phase 3 will complete this) |

## Current Milestone: v1.1 Complete

**Goal:** Ship a clean, debt-free final version — fix all context-field bugs and deliver Deep Mode with model review, phase gates, and context re-injection.

**Target features:**
- Fix 3 cross-phase `.pbi-context.md` field consistency bugs (pbi-edit, pbi-diff/commit, pbi-optimise)
- Model review phase in deep mode (health flag analysis before any DAX)
- Hard phase gates between all deep-mode phases
- Business question gate at session end
- Context re-injection at each phase start

---
*Last updated: 2026-03-14 after v1.1 milestone start*
