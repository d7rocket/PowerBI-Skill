---
phase: 4
slug: git-workflow
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-12
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual / bash fixture-based (no automated test runner) |
| **Config file** | none — existing `tests/fixtures/` directories used |
| **Quick run command** | `cd tests/fixtures/pbip-tmdl && git diff HEAD -- '.SemanticModel/' 2>/dev/null` |
| **Full suite command** | Manual walkthrough of all 8 GIT scenarios against both fixture types |
| **Estimated runtime** | ~15 minutes (manual inspection) |

---

## Sampling Rate

- **After every task commit:** Manual inspection of bash block output and `git log` for git-touching tasks
- **After every plan wave:** Run all manual scenarios against both TMDL and TMSL fixtures
- **Before `/gsd:verify-work`:** All 8 GIT requirements manually verified and passing
- **Max feedback latency:** One wave (all tasks in a wave verified before next wave starts)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 4-W0-01 | W0 | 0 | GIT-03 | manual | `ls tests/fixtures/pbip-tmdl-no-gitignore/` | ❌ W0 | ⬜ pending |
| 4-W0-02 | W0 | 0 | GIT-08 | manual | `ls tests/fixtures/pbip-no-repo/` | ❌ W0 | ⬜ pending |
| 4-W0-03 | W0 | 0 | GIT-01,GIT-04 | manual | `cd tests/fixtures/pbip-tmdl && git log --oneline 2>/dev/null` | ✅ | ⬜ pending |
| 4-01-01 | 01 | 1 | GIT-01,GIT-02 | manual | Run `/pbi:diff` in pbip-tmdl fixture; inspect output | ✅ | ⬜ pending |
| 4-01-02 | 01 | 1 | GIT-03 | manual | Run `/pbi:diff` in pbip-tmdl-no-gitignore fixture; verify silent auto-fix | ❌ W0 | ⬜ pending |
| 4-02-01 | 02 | 1 | GIT-04,GIT-05 | manual | Run `/pbi:commit` in pbip-tmdl fixture; inspect `git log` message | ✅ | ⬜ pending |
| 4-02-02 | 02 | 1 | GIT-08 | manual | Run `/pbi:commit` in pbip-no-repo fixture; verify repo init + gitignore + initial commit | ❌ W0 | ⬜ pending |
| 4-03-01 | 03 | 2 | GIT-06 | manual | Run `/pbi:comment` in PBIP file mode; verify auto-commit line in output and `git log` | ✅ | ⬜ pending |
| 4-03-02 | 03 | 2 | GIT-06 | manual | Run `/pbi:error` confirm `y`; verify auto-commit line in output | ✅ | ⬜ pending |
| 4-03-03 | 03 | 2 | GIT-06 | manual | Run `/pbi:comment` in directory with no git repo; verify no-repo hint appears | ❌ W0 | ⬜ pending |
| 4-04-01 | 04 | 2 | GIT-07 | manual | `grep -r "git push" .claude/skills/` — confirm no push in any skill | ✅ (inspection) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/fixtures/pbip-tmdl-no-gitignore/` — copy of TMDL fixture with no `.gitignore` for GIT-03 auto-fix testing
- [ ] `tests/fixtures/pbip-no-repo/` — PBIP model directory with no `.git/` folder for GIT-08 init flow testing
- [ ] Git history in `tests/fixtures/pbip-tmdl/` — run `git init` + initial commit so `git diff HEAD` works for GIT-01/GIT-04 testing

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `/pbi:diff` output uses business names, not JSON paths | GIT-02 | No test runner; output is Claude natural language | Run `/pbi:diff` after modifying a measure in Sales.tmdl; confirm output says "1 measure modified in Sales" not `model.tables[0].measures[2].expression` |
| `.gitignore` auto-fix does not duplicate entries | GIT-03 | Requires multiple runs | Run `/pbi:diff` twice in no-gitignore fixture; inspect `.gitignore` to confirm no duplicate entries |
| Auto-commit message names actual measure/table | GIT-06 | Output is Claude natural language | Run `/pbi:comment` on a known measure; verify auto-commit line shows measure and table names |
| No `git push` in any skill | GIT-07 | Source code inspection | `grep -r "git push" .claude/skills/`; confirm 0 matches |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 1 wave
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
