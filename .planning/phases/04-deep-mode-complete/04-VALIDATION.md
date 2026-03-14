---
phase: 4
slug: deep-mode-complete
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-14
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual acceptance scenarios (markdown) |
| **Config file** | none — manual execution |
| **Quick run command** | Open `tests/acceptance-scenarios.md` and run the Phase 4 group |
| **Full suite command** | Run all groups in `tests/acceptance-scenarios.md` and `tests/phase2-acceptance-scenarios.md` |
| **Estimated runtime** | ~10 minutes (manual) |

---

## Sampling Rate

- **After every task commit:** Smoke test — run S4-01 (model review fires before DAX) and S4-03 (gate holds on "ok" input) from the Phase 4 scenario group
- **After every plan wave:** Full Phase 4 scenario group (estimated 6–8 scenarios)
- **Before `/gsd:verify-work`:** All acceptance scenario groups must be green
- **Max feedback latency:** Manual — run after each task

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 4-01-01 | 01 | 0 | PHASE-01, VERF-01, VERF-02, VERF-03 | manual | n/a — scenario file creation | ❌ Wave 0 | ⬜ pending |
| 4-01-02 | 01 | 1 | PHASE-01 | manual | Run S4-01 from acceptance-scenarios.md | ❌ Wave 0 | ⬜ pending |
| 4-01-03 | 01 | 1 | VERF-01 | manual | Run S4-03 from acceptance-scenarios.md | ❌ Wave 0 | ⬜ pending |
| 4-01-04 | 01 | 1 | VERF-02 | manual | Run S4-05 from acceptance-scenarios.md | ❌ Wave 0 | ⬜ pending |
| 4-01-05 | 01 | 1 | VERF-03 | manual | Run S4-07 from acceptance-scenarios.md | ❌ Wave 0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Phase 4 group appended to `tests/acceptance-scenarios.md` — covers PHASE-01, VERF-01, VERF-02, VERF-03

*All test types are manual-only. Justification: behaviors are Claude conversational responses — no automated runner can execute `/pbi deep` and evaluate response quality. Manual acceptance scenarios are the established pattern for this project (see `tests/acceptance-scenarios.md` and `tests/phase2-acceptance-scenarios.md`).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Model review phase surfaces M:M, missing date table, bidirectional filter issues | PHASE-01 | Conversational Claude response — no automated runner | Run S4-01: start `/pbi deep`, describe model with issues, confirm model review fires before any DAX |
| Hard gate holds until "continue" — does not advance on vague input ("ok", "yes") | VERF-01 | Conversational gate evaluation | Run S4-03: reach a phase gate, type "ok" — confirm gate re-outputs, does not advance |
| Final gate blocks session close until business question confirmed | VERF-02 | Conversational gate evaluation | Run S4-05: reach end of session, give non-answer — confirm gate holds |
| Context summary output at start of each phase | VERF-03 | Conversational output evaluation | Run S4-07: advance through phases — confirm context block appears at each phase start |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < manual (per task)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
