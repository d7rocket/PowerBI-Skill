# Requirements: PBI Skill v2

**Defined:** 2026-03-23
**Core Value:** Never block a data analyst — solve immediately, interrogate only when stuck or asked

## v1.2 Requirements

Requirements for milestone v1.2: Quality & Distribution.

### Installer

- [x] **INST-01**: Installer downloads all skill files including `detect.py`, `docs.md`, and `shared/api-notes.md`
- [x] **INST-02**: Installer reads version from downloaded SKILL.md rather than hardcoding
- [x] **INST-03**: Installer accepts `-Scope project|user` parameter to choose install path (`.claude/skills/pbi/` vs `~/.claude/skills/pbi/`)
- [x] **INST-04**: Installer creates `scripts/` directory and downloads `detect.py`

### Token Management

- [x] **TOKEN-01**: No command file triggers "file content exceeds 10K tokens" during skill execution
- [x] **TOKEN-02**: Large command files (audit, optimise, error, comment) are trimmed or restructured to stay within limits

### UTF-8 Safety

- [x] **UTF8-01**: All measure search operations use `detect.py search` instead of `grep -rlF` (edit.md, comment.md, error.md, new.md)
- [x] **UTF8-02**: Format.md HTML parsing uses Python instead of grep/sed pipeline
- [x] **UTF8-03**: Help.md version check uses Python instead of grep/sed

### Version History

- [x] **HIST-01**: `/pbi version` command displays full version history from bundled CHANGELOG.md
- [x] **HIST-02**: CHANGELOG.md file included in skill distribution with all versions documented

### Phase 8 - Settings Sub-skill + Blindspot Fixes

- [x] **SETTINGS-01**: `/pbi:settings` is directly invocable as a dedicated slash command (sub-skill file at `settings/SKILL.md`)
- [x] **SETTINGS-02**: Installer downloads `settings` sub-skill and command stub
- [x] **SYNC-01**: All `.claude/commands/pbi/*.md` files write context to `.pbi/context.md` (not `.pbi-context.md`)
- [x] **SYNC-02**: All commands files include `ensure-dir`, `migrate`, and `settings` detection steps and use `detect.py session-check` auto-resume logic

## Future Requirements

None currently deferred.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Converting diff.md gitignore grep to Python | Pure ASCII operation, no UTF-8 risk |
| Splitting SKILL.md router into multiple files | Router must remain single file for Claude Code skill discovery |
| Automated testing of installer | Manual verification sufficient for single-user tool |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INST-01 | Phase 5 | Complete |
| INST-02 | Phase 5 | Complete |
| INST-03 | Phase 5 | Complete |
| INST-04 | Phase 5 | Complete |
| TOKEN-01 | Phase 6 | Complete |
| TOKEN-02 | Phase 6 | Complete |
| UTF8-01 | Phase 6 | Complete |
| UTF8-02 | Phase 6 | Complete |
| UTF8-03 | Phase 6 | Complete |
| HIST-01 | Phase 7 | Complete |
| HIST-02 | Phase 7 | Complete |
| SETTINGS-01 | Phase 8 | Complete |
| SETTINGS-02 | Phase 8 | Complete |
| SYNC-01 | Phase 8 | Complete |
| SYNC-02 | Phase 8 | Complete |

**Coverage:**
- v1.2 requirements: 15 total (11 original + 4 Phase 8)
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-23*
*Last updated: 2026-03-31 after Phase 8 execution (INST marked complete, Phase 8 requirements added)*
