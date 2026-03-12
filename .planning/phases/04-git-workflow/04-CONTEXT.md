# Phase 4: Git Workflow - Context

**Gathered:** 2026-03-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Two git-focused commands: `/pbi:diff` produces a human-readable summary of model changes since the last commit; `/pbi:commit` stages PBIP changes and commits locally with an auto-generated business-language message. Phase also covers: auto-commit after any PBIP file write (GIT-06), `.gitignore` hygiene enforcement, and git init on first commit (GIT-08). Push to remote is always manual — never triggered automatically.

</domain>

<decisions>
## Implementation Decisions

### Diff output depth
- Count summary format: "3 measures modified in Sales, 1 relationship removed" — not full before/after DAX diff
- Covers all four change categories: measures (added/modified/removed), relationships, tables and columns, model properties (format strings, display folders, descriptions)
- Scope: diffs against last commit (standard `git diff HEAD` against PBIP model files)
- Filters to PBIP model files only — .tmdl / model.bim / relationships / tables files; ignores cache, settings, and lock files entirely

### Gitignore handling
- `/pbi:diff` checks `.gitignore` for noise file entries before presenting output
- If entries are missing: **auto-fix silently** — add the missing entries to `.gitignore` then proceed with the diff (no warning prompt)
- If no `.gitignore` at all: created as part of `git init` (see below)
- Standard noise file entries always included: `cache.abf`, `localSettings.json`, `.pbi-context.md`, `SecurityBindings`

### Auto-commit trigger (GIT-06)
- Auto-commit logic lives **inside each writing skill** (pbi-comment, pbi-error) — self-contained, no shared utility skill
- Surface to analyst: silent commit + one confirmation line at end of output: `Auto-committed: chore: update [MeasureName] comment in TableName`
- If no git repo when auto-commit triggers: skip the commit, show hint: "No git repo — run /pbi:commit to initialise one." File write still succeeds.

### Commit message format
- **Conventional commits** format: `feat:` / `fix:` / `chore:` prefix
- Subject line: one concise summary of the primary change
- Body: one bullet per changed item (measure, relationship, table) — e.g. `- add [Revenue YTD] to Sales` / `- modify [Total Cost] in Products`
- Auto-commits from file writes always use `chore:` prefix — e.g. `chore: update [Revenue YTD] comment in Sales`
- `/pbi:commit` infers prefix from change type: `feat` for adds, `fix` for corrections, `chore` for metadata updates

### Git init (GIT-08)
- `/pbi:commit` initialises a git repo if none exists — `git init` + creates `.gitignore` with standard PBIP noise file entries + initial commit
- Push to remote is always manual — no command auto-pushes under any circumstances

### Claude's Discretion
- Exact `git diff` command construction to scope to PBIP model files only
- How to parse raw git diff output into business-language change categories
- `.gitignore` creation template formatting and ordering
- Handling of edge cases: empty repo (no commits yet), detached HEAD

</decisions>

<specifics>
## Specific Ideas

- No specific references — standard git workflow expectations apply

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- PBIP detection bash block (PBIP_MODE, PBIP_FORMAT) — identical startup pattern used by pbi-audit, pbi-load; pbi-diff and pbi-commit use the same
- `pbi-comment/SKILL.md` and `pbi-error/SKILL.md` — both do PBIP file writes and need a git commit block added after the write step
- Session context injection pattern: `!`cat .pbi-context.md 2>/dev/null | tail -80`` — all existing skills use this; pbi-diff and pbi-commit should too

### Established Patterns
- PBIP_MODE=paste fallback: if no PBIP project detected, stop with a clear message — pbi-diff and pbi-commit should do the same (git workflow only makes sense with a PBIP project)
- Read-then-Write for `.pbi-context.md` updates — applies to both new skills
- Haiku for file reading/retrieval, Sonnet for reasoning — pbi-diff analysis (reading git diff, translating to business language) is Sonnet work
- `allowed-tools: Read, Write, Bash` — both new skills need Bash for git operations

### Integration Points
- `pbi-comment/SKILL.md` — add auto-commit block after the successful file write step
- `pbi-error/SKILL.md` — add auto-commit block after the successful file write step (after confirm prompt, on y response)
- `.pbi-context.md` — both new skills update it after execution; auto-commit confirmation line also surfaces there
- New skills live at: `.claude/skills/pbi-diff/SKILL.md` and `.claude/skills/pbi-commit/SKILL.md`

</code_context>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-git-workflow*
*Context gathered: 2026-03-12*
