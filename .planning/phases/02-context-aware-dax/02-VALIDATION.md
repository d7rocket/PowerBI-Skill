---
phase: 2
slug: context-aware-dax
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-14
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual acceptance testing (no automated test runner — skill is markdown instructions for an LLM) |
| **Config file** | None — test scenarios are human-readable `.md` files |
| **Quick run command** | Open project in Claude Code, run specified `/pbi` command, compare output to pass criteria |
| **Full suite command** | Run all scenarios in `tests/phase2-acceptance-scenarios.md` sequentially |
| **Estimated runtime** | ~15 minutes (manual) |

---

## Sampling Rate

- **After every task commit:** Smoke test — run the single changed command with a representative request, verify no regression
- **After every plan wave:** Run all Phase 2 scenarios plus Phase 1 Group 4 (existing behavior preservation)
- **Before `/gsd:verify-work`:** Full Phase 2 suite must be green

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 2-01 | 01 | 0 | DAX-01,02,03,INTR-04,PHASE-02 | manual | Run all scenarios in `tests/phase2-acceptance-scenarios.md` | ❌ Wave 0 | ⬜ pending |
| 2-02 | 02 | 1 | DAX-01 | manual | Run `/pbi new` with empty `.pbi-context.md`, verify table/column question asked | ❌ Wave 0 | ⬜ pending |
| 2-03 | 02 | 1 | DAX-01 | manual | Run `/pbi new` twice, verify second run skips question | ❌ Wave 0 | ⬜ pending |
| 2-04 | 02 | 1 | DAX-01 | manual | Run each DAX command with empty context, verify question asked | ❌ Wave 0 | ⬜ pending |
| 2-05 | 02 | 1 | DAX-02 | manual | Run `/pbi new`, verify "Does a similar measure already exist?" appears | ❌ Wave 0 | ⬜ pending |
| 2-06 | 02 | 1 | DAX-02 | manual | Answer yes with existing measure name, verify CALCULATE wrapper | ❌ Wave 0 | ⬜ pending |
| 2-07 | 02 | 1 | DAX-03,INTR-04 | manual | Request DATESYTD measure, verify visual context ask fires before DAX | ❌ Wave 0 | ⬜ pending |
| 2-08 | 02 | 1 | DAX-03 | manual | Generate two time-intel measures, verify second skips visual context question | ❌ Wave 0 | ⬜ pending |
| 2-09 | 02 | 1 | INTR-04 | manual | Request `SUM(Sales[Amount])`, verify no visual context question | ❌ Wave 0 | ⬜ pending |
| 2-10 | 03 | 2 | PHASE-02 | manual | Complete deep mode session, say "done", verify measure list displayed | ❌ Wave 0 | ⬜ pending |
| 2-11 | 03 | 2 | PHASE-02 | manual | Verify business question from `.pbi-context.md` appears in gate output | ❌ Wave 0 | ⬜ pending |
| 2-12 | 03 | 2 | PHASE-02 | manual | Answer "confirm", verify session closed message | ❌ Wave 0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/phase2-acceptance-scenarios.md` — 14-scenario acceptance script covering all requirement IDs (DAX-01, DAX-02, DAX-03, INTR-04, PHASE-02)

*Note: No test framework install needed — all testing is manual execution by a human following the scenario script. The acceptance scenario file is the only Wave 0 gap.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Context intake ask on `/pbi new` with empty context | DAX-01 | Skill is markdown instructions for LLM — no automated runner | Run `/pbi new`, confirm "Which table and which columns are relevant?" is asked |
| Context reuse — no re-ask on second run | DAX-01 | Requires stateful session observation | Run `/pbi new` twice in same session, verify second skips question |
| Duplication check fires every `/pbi new` | DAX-02 | LLM instruction — no assert hook | Run `/pbi new`, verify "Does a similar measure already exist?" appears before generation |
| Wrapping measure on "yes" to duplication check | DAX-02 | Output quality judgment required | Answer yes, paste existing measure, verify output uses `CALCULATE([existing], ...)` pattern |
| Filter-sensitive ask fires before DAX output | DAX-03, INTR-04 | Ordering requires human observation | Request DATESYTD measure, confirm visual context question precedes any DAX |
| Deep mode measures gate on "done" | PHASE-02 | Interactive session flow | Complete deep mode, say "done", verify gate shows measure summary + business question |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 900s (manual — 15 min max per wave)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
