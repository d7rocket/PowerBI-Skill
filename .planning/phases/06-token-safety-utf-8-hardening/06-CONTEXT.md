# Phase 6: Token Safety + UTF-8 Hardening - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Eliminate "file content exceeds 10K tokens" errors during skill execution and replace all grep/sed usage with Python/UTF-8 operations. No command should fail due to model file size, and no shell text processing should remain in any command file.

</domain>

<decisions>
## Implementation Decisions

### Token error source
- **D-01:** The 10K token error occurs when reading large model files (model.bim, .tmdl files), NOT from reading command .md files. The fix targets how skills read model data.

### Large model file handling
- **D-02:** Use chunked reading with offset/limit parameters on the Read tool when processing large model files. Commands that read model files (load, audit, extract, edit, comment, error, new) must use offset/limit to stay within token limits.

### grep/sed replacement scope
- **D-03:** Replace ALL grep/sed usage across ALL command files with Python equivalents. Zero shell text processing in the skill. This includes:
  - Measure search in edit.md, comment.md, error.md, new.md → `detect.py search`
  - HTML parsing in format.md → `detect.py html-parse`
  - Version check in help.md → `detect.py version-check`
  - Gitignore checks in diff.md → `detect.py gitignore-check`
  - Any other grep/sed/awk/cat in command files

### Python function location
- **D-04:** All new Python functions go into the existing `detect.py` as new subcommands. One file, many commands. No separate scripts.

### Claude's Discretion
- Exact chunking strategy (how to split large model.bim reads)
- detect.py subcommand signatures and output formats
- Which commands need chunked reading vs which are already safe
- How to handle the format.md HTML response parsing in Python (regex vs html.parser)

</decisions>

<canonical_refs>
## Canonical References

No external specs — requirements fully captured in decisions above and REQUIREMENTS.md (TOKEN-01, TOKEN-02, UTF8-01, UTF8-02, UTF8-03).

### Key source files
- `.claude/skills/pbi/scripts/detect.py` — Existing detection script to be expanded with new subcommands
- `.claude/skills/pbi/commands/edit.md` line 40, 44 — grep -rlF for measure search
- `.claude/skills/pbi/commands/comment.md` line 24 — grep -rlF for measure search
- `.claude/skills/pbi/commands/error.md` line 39 — grep -rlF for measure search
- `.claude/skills/pbi/commands/new.md` line 184 — grep -rlF for table verification
- `.claude/skills/pbi/commands/format.md` lines 7, 58-64 — grep/sed for HTML parsing
- `.claude/skills/pbi/commands/help.md` lines 14-18 — grep/sed for version check
- `.claude/skills/pbi/commands/diff.md` line 28 — grep for gitignore checks
- `.claude/skills/pbi/shared/api-notes.md` — DAX Formatter API response format (needed for html-parse subcommand)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `detect.py` already has 7 subcommands: pbip, files, pbir, git, context, nearby, search
- `detect.py search` already implements UTF-8 safe measure name search — pattern to follow for new subcommands
- All subcommands share the same UTF-8 stdout reconfiguration at script entry

### Established Patterns
- detect.py subcommand pattern: `sys.argv[1]` dispatch, print output to stdout, Claude reads via `!` execution blocks
- Detection blocks in SKILL.md use `python ".claude/skills/pbi/scripts/detect.py" <subcommand>` syntax
- Commands reference detect.py via relative path from project root

### Integration Points
- format.md calls curl for DAX Formatter API → response HTML needs Python parsing
- help.md reads SKILL.md frontmatter for version → detect.py can parse YAML-ish frontmatter
- diff.md checks/updates .gitignore entries → detect.py can check/append lines
- 4 command files use grep -rlF for measure search → already have detect.py search as replacement

</code_context>

<specifics>
## Specific Ideas

- User confirmed the token error is from model files specifically, not command files — so TOKEN-01/TOKEN-02 focus on chunked reading in commands that process model data
- User wants zero grep/sed anywhere in the skill — strict "all Python" policy, including format.md HTML parsing and diff.md gitignore checks which have no UTF-8 risk but are being replaced for consistency

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-token-safety-utf-8-hardening*
*Context gathered: 2026-03-23*
