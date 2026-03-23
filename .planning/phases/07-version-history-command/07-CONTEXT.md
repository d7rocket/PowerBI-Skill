# Phase 7: Version History Command - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Create a `/pbi version` command that displays the full version history from a bundled CHANGELOG.md. Add the CHANGELOG.md to the skill distribution and installer manifest.

</domain>

<decisions>
## Implementation Decisions

### Changelog content
- **D-01:** Claude's discretion on detail level per version. Include all shipped versions (v1.0 through current).

### Command behavior
- **D-02:** Changelog only — display current version and full changelog. No network calls, no update check. Simple and offline-capable.

### File location
- **D-03:** CHANGELOG.md lives in `.claude/skills/pbi/shared/CHANGELOG.md` alongside api-notes.md. Keeps skill root clean.

### Routing
- **D-04:** Add `version` keyword to the routing table in SKILL.md, mapping to `commands/version.md`. Model: Sonnet (direct execution, like help.md).

### Installer update
- **D-05:** Add `shared/CHANGELOG.md` to the installer's shared resources download section (install.ps1 [4/4] block).

### Claude's Discretion
- Exact changelog format (Keep a Changelog style, simple bullets, etc.)
- How much detail per version entry
- Whether to group changes by category (Added/Changed/Fixed) or flat bullets
- version.md command file structure

</decisions>

<canonical_refs>
## Canonical References

No external specs — requirements fully captured in decisions above and REQUIREMENTS.md (HIST-01, HIST-02).

### Key source files
- `.claude/skills/pbi/SKILL.md` — Routing table to add `version` keyword (lines ~62-82)
- `.claude/skills/pbi/commands/help.md` — Reference for similar lightweight command pattern
- `install.ps1` — Installer manifest, needs CHANGELOG.md added to shared downloads
- `.claude/skills/pbi/scripts/detect.py` — Has `version_check` subcommand (reads current version from SKILL.md)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `detect.py version-check` already reads the current version from SKILL.md frontmatter — version.md can call it
- help.md is a similar lightweight command (reads SKILL.md, displays info) — follow same pattern
- install.ps1 shared section already downloads api-notes.md — add CHANGELOG.md alongside it

### Established Patterns
- Command files read shared resources via relative path: `.claude/skills/pbi/shared/`
- Routing table maps keywords to command files with model annotation
- Lightweight commands (help) run on Sonnet directly, no Agent spawn

### Integration Points
- SKILL.md routing table: add `version` keyword entry
- install.ps1: add CHANGELOG.md to [4/4] shared downloads
- SKILL.md empty-args menu: optionally add version to the ? help section

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 07-version-history-command*
*Context gathered: 2026-03-23*
