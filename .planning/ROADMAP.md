# Roadmap: PBI Skill v2

## Milestones

- ✅ **v1.0 Core** — Phases 1-2 (shipped 2026-03-14)
- ✅ **v1.1 Complete** — Phases 3-4 (shipped 2026-03-14)
- ✅ **v1.2 Quality & Distribution** — Phases 5-8 (shipped 2026-03-31)

## Phases

<details>
<summary>✅ v1.0 Core (Phases 1-2) — SHIPPED 2026-03-14</summary>

- [x] Phase 1: Skill Core + Escalation (2/2 plans) — completed 2026-03-13
- [x] Phase 2: Context-Aware DAX (5/5 plans) — completed 2026-03-14

Full phase details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

<details>
<summary>✅ v1.1 Complete (Phases 3-4) — SHIPPED 2026-03-14</summary>

- [x] Phase 3: Context Field Fixes (2/2 plans) — completed 2026-03-14
- [x] Phase 4: Deep Mode Complete (2/2 plans) — completed 2026-03-14

Full phase details: `.planning/milestones/v1.1-ROADMAP.md`

</details>

<details>
<summary>✅ v1.2 Quality & Distribution (Phases 5-8) — SHIPPED 2026-03-31</summary>

- [x] Phase 5: Installer Overhaul (1/1 plan) — completed 2026-03-23
- [x] Phase 6: Token Safety + UTF-8 Hardening (5/5 plans) — completed 2026-03-23
- [x] Phase 7: Version History Command (2/2 plans) — completed 2026-03-23
- [x] Phase 8: Audit & Settings Sub-skill (3/3 plans) — completed 2026-03-31

Full phase details: `.planning/milestones/v1.2-ROADMAP.md`

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Skill Core + Escalation | v1.0 | 6/6 | Complete    | 2026-04-20 |
| 2. Context-Aware DAX | v1.0 | 5/5 | Complete | 2026-03-14 |
| 3. Context Field Fixes | v1.1 | 2/2 | Complete | 2026-03-14 |
| 4. Deep Mode Complete | v1.1 | 2/2 | Complete | 2026-03-14 |
| 5. Installer Overhaul | v1.2 | 1/1 | Complete | 2026-03-23 |
| 6. Token Safety + UTF-8 Hardening | v1.2 | 5/5 | Complete | 2026-03-23 |
| 7. Version History Command | v1.2 | 2/2 | Complete | 2026-03-23 |
| 8. Audit & Settings Sub-skill | v1.2 | 3/3 | Complete | 2026-03-31 |

### Phase 1: Replace pbi colon commands with dash commands and update whole skill repo

**Goal:** Rename every `/pbi:<cmd>` invocation to `/pbi-<cmd>` across the entire repo (skill files, command descriptors, CLAUDE.md, README, install scripts, CHANGELOG, shared files) AND restructure directories so commands actually resolve as `/pbi-<cmd>` in Claude Code — flat `.claude/commands/pbi-<cmd>.md` descriptors and flat-prefixed `.claude/skills/pbi-<cmd>/` sub-skill dirs. Base `/pbi` menu/router stays at its original path.
**Requirements**: PBI-RENAME-CMDS, PBI-RENAME-SUBSKILLS, PBI-RENAME-REWIRE, PBI-RENAME-VERIFY
**Depends on:** Phase 0
**Plans:** 6/6 plans complete

Plans:
- [ ] 01-PLAN.md — Move + rewrite the 22 command descriptor files into flat `.claude/commands/pbi-<cmd>.md`
- [ ] 02-PLAN.md — Move + rewrite the 22 sub-skill SKILL.md files into `.claude/skills/pbi-<cmd>/`
- [ ] 03-PLAN.md — Rewire base SKILL.md routing, installers, README, CLAUDE.md, PROJECT-OVERVIEW, shared files, scripts/gen_*.py, tests fixture; prepend v7.1.0 CHANGELOG entry
- [ ] 04-PLAN.md — Repo-wide verification, bump base version to 7.1.0, human-verify checkpoint
