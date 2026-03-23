# Phase 5: Installer Overhaul - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Rework install.ps1 so it reliably installs or updates the full PBI skill (all command files, detect.py, shared resources) with a single command. User chooses project or user scope via `-Scope` parameter.

</domain>

<decisions>
## Implementation Decisions

### Default scope
- **D-01:** Default `-Scope` is `user` — installs to `~/.claude/skills/pbi/`. User scope means one install works for all projects. Project scope (`./.claude/skills/pbi/`) available via `-Scope project`.

### File manifest
- **D-02:** Claude's discretion on manifest approach. Key constraint: adding a new command file must not silently break the installer (the `docs.md` / `detect.py` omission that caused the current bug).

### Update behavior
- **D-03:** Overwrite all files on update. No backup, no diffing. Clean replace guarantees latest version. Users who customize command files accept they'll be overwritten.

### GitHub source URL
- **D-04:** Base URL changes to `https://raw.githubusercontent.com/d7rocket/PBI-SKILL/main`. Old URL (`deveshd7/PowerBI-Skill`) is incorrect.

### Version display
- **D-05:** Installer reads version from the downloaded SKILL.md file (parse `version:` from YAML frontmatter) rather than hardcoding. Single source of truth — no more version drift.

### File completeness
- **D-06:** Installer must download ALL skill files: SKILL.md, all 18 command .md files (including `docs.md`), `scripts/detect.py`, and `shared/api-notes.md`. Missing any critical file (especially detect.py) breaks detection.

### Claude's Discretion
- Manifest approach (hardcoded list vs manifest.json vs directory listing)
- Progress bar implementation details
- Error messaging and retry logic
- Banner/summary formatting

</decisions>

<canonical_refs>
## Canonical References

No external specs — requirements fully captured in decisions above and REQUIREMENTS.md (INST-01 through INST-04).

### Installer
- `install.ps1` — Current installer to be rewritten (reference for banner style, progress bar UX)

### Skill structure
- `.claude/skills/pbi/SKILL.md` — Router file, contains `version:` in YAML frontmatter (line 6)
- `.claude/skills/pbi/scripts/detect.py` — Detection script that was missing from installer
- `.claude/skills/pbi/commands/` — 18 command files that must all be included

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `install.ps1`: Existing banner ASCII art, progress bar using Unicode block characters (█░), pre-flight GitHub connectivity check — all reusable patterns
- `SKILL.md` frontmatter: `version: 4.3.0` on line 6 — parse target for dynamic version reading

### Established Patterns
- PowerShell parameter pattern: `param([string]$Target = ".")` — extend with `-Scope` parameter
- Progress bar: Unicode block characters with percentage display
- Error handling: Continue on non-critical failures, hard-fail on SKILL.md (router is required)

### Integration Points
- GitHub raw URL: `https://raw.githubusercontent.com/d7rocket/PBI-SKILL/main/.claude/skills/pbi/...`
- Target directories: `~/.claude/skills/pbi/` (user) or `./.claude/skills/pbi/` (project)
- Directory structure: `commands/`, `scripts/`, `shared/` subdirectories

</code_context>

<specifics>
## Specific Ideas

- User clarified that project-level install means each repo needs its own copy; user-level is preferred because it's install-once for all PBI projects
- The current installer was pointing at the wrong GitHub repo (deveshd7/PowerBI-Skill instead of d7rocket/PBI-SKILL)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-installer-overhaul*
*Context gathered: 2026-03-23*
