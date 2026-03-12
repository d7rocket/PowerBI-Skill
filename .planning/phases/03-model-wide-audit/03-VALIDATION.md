---
phase: 3
slug: model-wide-audit
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-12
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — prompt/skill system with no compiled code |
| **Config file** | N/A |
| **Quick run command** | Manual: invoke `/pbi:audit` from `tests/fixtures/pbip-tmdl/` |
| **Full suite command** | Manual: run `/pbi:audit` against both TMDL and TMSL fixtures; verify expected findings appear |
| **Estimated runtime** | ~2 minutes (manual review) |

---

## Sampling Rate

- **After every task commit:** Bash smoke — `ls audit-report.md 2>/dev/null && echo "exists"` after running `/pbi:audit`
- **After every plan wave:** Full manual pass against both TMDL and TMSL fixtures; verify all expected findings appear
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~120 seconds (manual)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 3-W0-01 | 01 | 0 | AUD-04 | manual | Create `Date.tmdl` fixture; verify `dataCategory: Time` syntax | ❌ W0 | ⬜ pending |
| 3-W0-02 | 01 | 0 | AUD-03 | manual | Create `Products.tmdl` isolated table fixture | ❌ W0 | ⬜ pending |
| 3-01-01 | 01 | 1 | AUD-01, AUD-06 | structural | Review `SKILL.md` instruction steps — verify four domain steps exist | ❌ W0 | ⬜ pending |
| 3-01-02 | 01 | 1 | AUD-03 | manual | Run `/pbi:audit` from TMDL fixture; verify 🔴 CRITICAL [Relationships] Sales → Date appears | ✅ Fixture exists | ⬜ pending |
| 3-01-03 | 01 | 1 | AUD-04 | manual | Run `/pbi:audit` from fixture with no date table; verify 🟡 WARN [Date Table] appears | ✅ Fixture exists | ⬜ pending |
| 3-01-04 | 01 | 1 | AUD-05 | manual | Run `/pbi:audit` from TMDL fixture; verify 🔵 INFO [Measures] Revenue — no description appears | ✅ Fixture exists | ⬜ pending |
| 3-01-05 | 01 | 1 | AUD-02 | manual | Run `/pbi:audit`; verify naming findings appear | ✅ Fixture exists | ⬜ pending |
| 3-01-06 | 01 | 1 | AUD-07 | manual | Inspect report output; verify no JSON paths, all findings have subject + recommendation | ✅ Verified via spec | ⬜ pending |
| 3-01-07 | 01 | 1 | AUD-01 | manual | Run `/pbi:audit` from TMSL fixture; verify same report structure produced | ✅ Fixture exists | ⬜ pending |
| 3-01-08 | 01 | 1 | AUD-04 | manual | Run `/pbi:audit` with Date.tmdl fixture; verify positive date table detection | ❌ W0 | ⬜ pending |
| 3-01-09 | 01 | 1 | AUD-03 | manual | Run `/pbi:audit` with Products.tmdl isolated table; verify WARN missing-relationship appears | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/pbip-tmdl/.SemanticModel/definition/tables/Date.tmdl` — date table fixture with `dataCategory: Time` to test AUD-04 positive detection case
- [ ] `tests/fixtures/pbip-tmdl/.SemanticModel/definition/tables/Products.tmdl` — isolated table with no outbound relationships to test AUD-03 missing-relationship WARN
- [ ] Verify TMDL `dataCategory: Time` exact line placement empirically after creating Date.tmdl

*Wave 0 must complete before audit findings for AUD-03 (missing relationship) and AUD-04 (positive date table) can be verified.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `/pbi:audit` produces severity-graded report | AUD-01 | Claude skill output — no compiled test runner | Run `/pbi:audit` from TMDL fixture dir; verify CRITICAL/WARN/INFO sections present |
| Naming conventions checked across all scopes | AUD-02 | LLM inference output | Run `/pbi:audit`; verify naming findings reference actual names not JSON paths |
| Bidirectional relationship flagged as CRITICAL | AUD-03 | LLM pattern detection | Run `/pbi:audit` from TMDL fixture; verify `🔴 CRITICAL [Relationships] Sales → Date` appears |
| Missing relationship flagged as WARN | AUD-03 | Heuristic detection | Run `/pbi:audit` with Products.tmdl; verify WARN for isolated table appears |
| Date table absence flagged as WARN | AUD-04 | LLM metadata analysis | Run `/pbi:audit` from fixture with no `dataCategory: Time`; verify WARN appears |
| Date table presence detected correctly | AUD-04 | LLM metadata analysis | Run `/pbi:audit` with Date.tmdl; verify positive detection and INFO note |
| Missing description flagged as INFO | AUD-05 | LLM property check | Run `/pbi:audit`; verify `🔵 INFO [Measures] Revenue — no description` appears |
| Missing formatString flagged as WARN | AUD-05 | LLM property check | Add measure without formatString to fixture; verify WARN appears |
| No display folder flagged as WARN | AUD-05 | LLM property check | Add measure without displayFolder; verify WARN appears |
| Audit runs in four domain passes | AUD-06 | Structural review | Read SKILL.md; verify four numbered domain instruction steps |
| All findings include name + recommendation | AUD-07 | Output inspection | Review full report; confirm no JSON paths used anywhere |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
