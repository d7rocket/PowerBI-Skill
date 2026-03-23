# PBI Skill v2

## What This Is

A Claude Code skill for Power BI development that solves DAX requests immediately by default, escalates to structured questioning only after repeated failure signals, grounds generated measures in the user's actual model context, and provides a complete structured deep-mode workflow with model health review, hard phase gates, and context re-injection.

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
- ✓ pbi-edit writes `Measure:` (not `Entity:`) to `## Last Command` — v1.1 (DEBT-01)
- ✓ pbi-diff and pbi-commit write actual measure names to `Measure:` field — v1.1 (DEBT-02)
- ✓ pbi-optimise Command History rows match schema column order — v1.1 (DEBT-03)
- ✓ Deep mode model review phase fires before any DAX — v1.1 (PHASE-01)
- ✓ Deep mode phase boundaries are hard gates (no auto-advance) — v1.1 (VERF-01)
- ✓ Deep mode final gate checks output answers the stated business question — v1.1 (VERF-02)
- ✓ Context summary restated at start of each deep-mode phase — v1.1 (VERF-03)

### Active

- [ ] Installer reliably installs/updates all skill files with per-project vs user-level scope choice (INST-01–04)
- [ ] Large command files stay under token limits during skill execution (TOKEN-01–02)
- [ ] All file operations use Python with UTF-8 encoding — no grep/sed on model files (UTF8-01–03)
- [ ] `/pbi version` command shows full version history from bundled changelog (HIST-01)

## Current Milestone: v1.2 Quality & Distribution

**Goal:** Fix installer reliability, eliminate token overflow, enforce Python-first file ops, and add version history command.

**Target features:**
- Reworked installer with `-Scope project|user` parameter, all files included, version read from SKILL.md
- Token management for large command files
- Replace remaining grep/sed with Python for UTF-8 safety
- New `/pbi version` command with bundled CHANGELOG.md

### Out of Scope

- Automated Power BI API integration — conversational skill, not a service connector
- Generic DAX tutorials — context-driven assistance, not educational content
- Free-form Q&A mode without structure — destroys phase discipline in deep mode
- OAuth / Power BI Service integration — works from described context only

## Context

**Shipped v1.1** with 4 phases, 11 plans total, ~3,200 LOC across skill markdown files. Current version: v4.3.0.

**Tech stack:** Claude Code skill markdown, `.pbi-context.md` for session state, TMDL/TMSL file support, Python detection script (`detect.py`).

**v1.2 drivers:** install.ps1 is out of sync (v4.1.0 vs SKILL.md v4.3.0), missing `docs.md` and `detect.py` from download list. Several command files (audit 16KB, optimise 14KB, error 13KB) trigger 10K token errors. Four commands still use `grep -rlF` instead of `detect.py search` for measure lookups. French accented characters in model files require consistent Python/UTF-8 handling.

**Pending verification:** pbi-error file-mode live tests (ERR-03/INFRA-06) deferred until Power BI Desktop available. No implementation gap — same pattern as verified pbi-comment.

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
| Locked `- Field:` bullet syntax for Last Command writes | Prose notation caused Claude to infer wrong field names (Entity: vs Measure:) | ✓ Good — eliminates field-name ambiguity in all context writes |
| Hard gate three-branch logic (exact token / cancel / re-output) | Two-branch gates are soft gates — unmatched input must re-output the gate | ✓ Good — "ok" and "sounds good" now correctly re-output |
| Gate tokens: `continue`/`cancel` mid-session, `confirm`/`cancel` terminal | Differentiates mid-session phase advance from final session close | ✓ Good — clear semantic difference for users |
| Model review scope: described context only, no file reads | Phase B should be fast and conversational; file-level audit is `/pbi audit` | ✓ Good — non-blocking, routes users to right tool for deep analysis |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-23 after v1.2 milestone start*
