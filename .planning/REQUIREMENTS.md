# Requirements: PBI Skill v2

**Defined:** 2026-03-23
**Core Value:** Never block a data analyst — solve immediately, interrogate only when stuck or asked

## v1.2 Requirements

Requirements for milestone v1.2: Quality & Distribution.

### Installer

- [ ] **INST-01**: Installer downloads all skill files including `detect.py`, `docs.md`, and `shared/api-notes.md`
- [ ] **INST-02**: Installer reads version from downloaded SKILL.md rather than hardcoding
- [ ] **INST-03**: Installer accepts `-Scope project|user` parameter to choose install path (`.claude/skills/pbi/` vs `~/.claude/skills/pbi/`)
- [ ] **INST-04**: Installer creates `scripts/` directory and downloads `detect.py`

### Token Management

- [x] **TOKEN-01**: No command file triggers "file content exceeds 10K tokens" during skill execution
- [x] **TOKEN-02**: Large command files (audit, optimise, error, comment) are trimmed or restructured to stay within limits

### UTF-8 Safety

- [ ] **UTF8-01**: All measure search operations use `detect.py search` instead of `grep -rlF` (edit.md, comment.md, error.md, new.md)
- [x] **UTF8-02**: Format.md HTML parsing uses Python instead of grep/sed pipeline
- [x] **UTF8-03**: Help.md version check uses Python instead of grep/sed

### Version History

- [ ] **HIST-01**: `/pbi version` command displays full version history from bundled CHANGELOG.md
- [ ] **HIST-02**: CHANGELOG.md file included in skill distribution with all versions documented

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
| INST-01 | Phase 5 | Pending |
| INST-02 | Phase 5 | Pending |
| INST-03 | Phase 5 | Pending |
| INST-04 | Phase 5 | Pending |
| TOKEN-01 | Phase 6 | Complete |
| TOKEN-02 | Phase 6 | Complete |
| UTF8-01 | Phase 6 | Pending |
| UTF8-02 | Phase 6 | Complete |
| UTF8-03 | Phase 6 | Complete |
| HIST-01 | Phase 7 | Pending |
| HIST-02 | Phase 7 | Pending |

**Coverage:**
- v1.2 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-23*
*Last updated: 2026-03-23 after roadmap creation (phases 5-7 assigned)*
