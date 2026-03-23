# Roadmap: PBI Skill v2

## Milestones

- ✅ **v1.0 Core** — Phases 1-2 (shipped 2026-03-14)
- ✅ **v1.1 Complete** — Phases 3-4 (shipped 2026-03-14)
- 🚧 **v1.2 Quality & Distribution** — Phases 5-7 (in progress)

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

### 🚧 v1.2 Quality & Distribution (In Progress)

**Milestone Goal:** Fix installer reliability, eliminate token overflow, enforce Python-first file ops, and add version history command.

- [x] **Phase 5: Installer Overhaul** - Installer reliably installs all files with configurable scope (completed 2026-03-23)
- [ ] **Phase 6: Token Safety + UTF-8 Hardening** - No command file triggers token errors; all file ops use Python/UTF-8
- [ ] **Phase 7: Version History Command** - `/pbi version` shows full version history from bundled changelog

## Phase Details

### Phase 5: Installer Overhaul
**Goal**: Users can install or update the full PBI skill with a single command, choosing project or user scope
**Depends on**: Phase 4
**Requirements**: INST-01, INST-02, INST-03, INST-04
**Success Criteria** (what must be TRUE):
  1. Running the installer downloads every skill file including `detect.py`, `docs.md`, and `shared/api-notes.md`
  2. The installed version banner reads the actual version from the downloaded `SKILL.md` (no hardcoded version string)
  3. `-Scope project` installs to `.claude/skills/pbi/` and `-Scope user` installs to `~/.claude/skills/pbi/`
  4. The `scripts/` directory is created automatically and `detect.py` is placed inside it
**Plans**: 1 plan

Plans:
- [ ] 05-01-PLAN.md — Rewrite install.ps1: scope param, full manifest, dynamic version, scripts/ dir

### Phase 6: Token Safety + UTF-8 Hardening
**Goal**: No skill command fails due to token overflow, and all file operations safely handle French accented characters
**Depends on**: Phase 5
**Requirements**: TOKEN-01, TOKEN-02, UTF8-01, UTF8-02, UTF8-03
**Success Criteria** (what must be TRUE):
  1. Running `/pbi audit`, `/pbi optimise`, `/pbi error`, or `/pbi comment` on any model produces no "file content exceeds 10K tokens" error
  2. Measure search in `edit.md`, `comment.md`, `error.md`, and `new.md` uses `detect.py search` — no `grep -rlF` calls remain in those files
  3. `format.md` HTML response parsing uses a Python script instead of a grep/sed pipeline
  4. `help.md` version check reads SKILL.md version via Python instead of grep/sed
**Plans**: 5 plans

Plans:
- [x] 06-01-PLAN.md — Expand detect.py: add html-parse, version-check, gitignore-check subcommands
- [ ] 06-02-PLAN.md — Replace grep in edit.md + comment.md; add TMSL chunked-read guard
- [ ] 06-03-PLAN.md — Replace grep in error.md + new.md; add TMSL chunked-read guard
- [ ] 06-04-PLAN.md — Replace grep/sed in format.md + help.md + diff.md with detect.py calls
- [ ] 06-05-PLAN.md — Add TMSL chunked-read guard to load.md

### Phase 7: Version History Command
**Goal**: Users can see the full skill version history from within Claude Code without leaving the session
**Depends on**: Phase 6
**Requirements**: HIST-01, HIST-02
**Success Criteria** (what must be TRUE):
  1. Typing `/pbi version` displays the full version history with release notes for every shipped version
  2. `CHANGELOG.md` exists in the skill distribution and is included when the installer runs
**Plans**: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Skill Core + Escalation | v1.0 | 2/2 | Complete | 2026-03-13 |
| 2. Context-Aware DAX | v1.0 | 5/5 | Complete | 2026-03-14 |
| 3. Context Field Fixes | v1.1 | 2/2 | Complete | 2026-03-14 |
| 4. Deep Mode Complete | v1.1 | 2/2 | Complete | 2026-03-14 |
| 5. Installer Overhaul | v1.2 | 0/1 | Complete    | 2026-03-23 |
| 6. Token Safety + UTF-8 Hardening | v1.2 | 1/5 | In Progress|  |
| 7. Version History Command | v1.2 | 0/? | Not started | - |
