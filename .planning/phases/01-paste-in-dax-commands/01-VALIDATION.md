---
phase: 1
slug: paste-in-dax-commands
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-12
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — prompt/skill system, not compiled code |
| **Config file** | none — Wave 0 creates fixture files |
| **Quick run command** | Manual: invoke `/pbi:explain` with a known DAX measure in Claude Code |
| **Full suite command** | Manual: run all five commands with test measures from `tests/fixtures/` |
| **Estimated runtime** | ~10 minutes (manual pass) |

---

## Sampling Rate

- **After every task commit:** Manual smoke test — invoke each new skill once with a simple measure to confirm it appears in menu and responds
- **After every plan wave:** Full manual pass with test fixture measures for all five commands
- **Before `/gsd:verify-work`:** Full suite must pass
- **Max feedback latency:** One wave (no automated timer)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-W0-01 | W0 | 0 | CTX-01, DAX-01 | smoke | `ls tests/fixtures/simple-measure.dax` | ❌ W0 | ⬜ pending |
| 1-W0-02 | W0 | 0 | DAX-02, DAX-03 | smoke | `ls tests/fixtures/intermediate-measure.dax` | ❌ W0 | ⬜ pending |
| 1-W0-03 | W0 | 0 | DAX-08, DAX-09 | smoke | `ls tests/fixtures/slow-filter-measure.dax` | ❌ W0 | ⬜ pending |
| 1-W0-04 | W0 | 0 | DAX-09 | smoke | `ls tests/fixtures/complex-measure.dax` | ❌ W0 | ⬜ pending |
| 1-W0-05 | W0 | 0 | ERR-01 | smoke | `ls tests/fixtures/error-log.txt` | ❌ W0 | ⬜ pending |
| 1-01-01 | 01 | 1 | INFRA-01 | smoke | Manual: type `/pbi` in Claude Code, verify `/pbi:explain` in menu | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 1 | CTX-01 | smoke | `ls .pbi-context.md` after invoking any skill | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 1 | CTX-03 | smoke | `cat .pbi-context.md` after run; verify Last Command section updated | ❌ W0 | ⬜ pending |
| 1-01-04 | 01 | 1 | CTX-02, CTX-04 | manual | Run command, report failure, re-run, verify prior failure flag appears | ❌ W0 | ⬜ pending |
| 1-02-01 | 02 | 1 | DAX-01 | manual | Paste `Revenue = SUM(Sales[Amount])`; verify output has plain-English summary | ❌ W0 | ⬜ pending |
| 1-02-02 | 02 | 1 | DAX-02 | manual | Paste `Total = CALCULATE(SUM(Sales[Amt]), FILTER(Sales, Sales[Year]=2024))`; verify filter/row context and transition sections | ❌ W0 | ⬜ pending |
| 1-02-03 | 02 | 1 | DAX-03 | manual | Test Simple measure → verify Simple tag; test nested SUMX → verify Advanced tag | ❌ W0 | ⬜ pending |
| 1-03-01 | 03 | 1 | DAX-04, DAX-05 | manual | Paste unformatted multi-line measure; verify SQLBI-style indented output in ` ```dax ` block | ❌ W0 | ⬜ pending |
| 1-03-02 | 03 | 1 | DAX-06 | manual | Break API URL in skill; run format; verify one-line fallback note and Claude inline format appears | ❌ W0 | ⬜ pending |
| 1-04-01 | 04 | 1 | DAX-07, DAX-08 | manual | Paste `Slow = SUMX(Sales, Sales[Amount])`; verify rewrite to `SUM` with rationale | ❌ W0 | ⬜ pending |
| 1-04-02 | 04 | 1 | DAX-09 | manual | Paste `Risk = SUMX(Customers, [CustomerRevenue])`; verify flag present, no rewrite | ❌ W0 | ⬜ pending |
| 1-04-03 | 04 | 1 | DAX-10 | manual | Paste measure with two valid rewrites; verify trade-off alternatives shown | ❌ W0 | ⬜ pending |
| 1-05-01 | 05 | 1 | DAX-11, DAX-12 | manual | Paste complex measure; verify `//` inline comments on meaningful lines AND Description field block | ❌ W0 | ⬜ pending |
| 1-06-01 | 06 | 1 | ERR-01 | manual | Paste known PBI error log; verify diagnosis and root cause explanation | ❌ W0 | ⬜ pending |
| 1-06-02 | 06 | 1 | ERR-02 | manual | Run a command, then paste related error; verify correlation to last change shown | ❌ W0 | ⬜ pending |
| 1-06-03 | 06 | 1 | ERR-04 | manual | Log error in `.pbi-context.md`; paste same error again; verify lead-with-correct-method output | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/simple-measure.dax` — `Revenue = SUM(Sales[Amount])` — covers DAX-01, DAX-03 (Simple)
- [ ] `tests/fixtures/intermediate-measure.dax` — `Sales YTD = CALCULATE([Revenue], DATESYTD('Date'[Date]))` — covers DAX-02, DAX-03 (Intermediate)
- [ ] `tests/fixtures/complex-measure.dax` — `Risky = SUMX(Customers, [Revenue])` — covers DAX-09 (iterator over measure ref)
- [ ] `tests/fixtures/slow-filter-measure.dax` — `Slow = CALCULATE(SUM(Sales[Amt]), FILTER(Sales, Sales[Year]=2024))` — covers DAX-08 (Rule 1)
- [ ] `tests/fixtures/error-log.txt` — sample Power BI error message — covers ERR-01
- [ ] `.pbi-context.md` initial stub — created by Wave 0 setup task

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Skill appears in `/` command menu | INFRA-01 | Claude Code menu is UI-only | Type `/pbi` in Claude Code; verify `/pbi:explain`, `/pbi:format`, `/pbi:optimise`, `/pbi:comment`, `/pbi:error` all appear |
| Plain-English explanation with context sections | DAX-01, DAX-02 | Natural language output; no structured assertion | Paste test measure; read output; verify filter context, row context, transitions identified |
| Complexity level tag adapts | DAX-03 | Model judgment call | Paste Simple → verify `[Simple]` tag; paste nested SUMX → verify `[Advanced]` tag |
| SQLBI format + code block | DAX-04, DAX-05 | Visual/format check | Paste unformatted measure; verify indentation style matches SQLBI convention |
| API fallback note visible | DAX-06 | Requires breaking the API URL | Break URL in skill; run format; verify graceful fallback with one-line note |
| Iterator-over-measure flagged, not rewritten | DAX-09 | Requires Claude to correctly identify pattern | Paste `SUMX(Customers, [CustomerRevenue])`; verify only a flag is returned, not a rewrite |
| Context file captures prior failures | CTX-02, CTX-04 | Interactive session state | Manually cause a failure; check `.pbi-context.md`; re-run; verify alternative approach led |
| Error correlation to last change | ERR-02 | Requires prior context in session file | Run a command, record it; then paste a related error and verify the output cross-references the prior command |
| Skip failed approach on repeat error | ERR-04 | Requires prior failure in context | Log a failed approach; paste same error; verify output skips the failed method |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency documented (manual cadence accepted for skill-only phase)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
