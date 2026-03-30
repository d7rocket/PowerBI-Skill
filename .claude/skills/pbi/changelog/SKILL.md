---
name: pbi:changelog
description: "Generate structured release notes from local git history in Keep a Changelog format. Groups commits by type (Added, Changed, Fixed, Removed). Covers a configurable range. Writes to CHANGELOG.md. Translates commit messages into user-facing release notes."
model: haiku
allowed-tools: Read, Write, Bash, Agent
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 6.0.0
  category: data-analytics
  tags: [power-bi, dax, pbip, semantic-model]
---

## Detection (run once)

**Folder naming:** Real PBIP projects use `<ProjectName>.SemanticModel` and `<ReportName>.Report`. Test fixtures may use `.SemanticModel`. Detection globs for both patterns.

### PBIP Detection
!`python ".claude/skills/pbi/scripts/detect.py" pbip 2>/dev/null || echo "PBIP_MODE=paste"`

Save the `PBIP_DIR` value from the output — all subsequent steps must use it instead of a hardcoded `.SemanticModel`.

### File Index
!`python ".claude/skills/pbi/scripts/detect.py" files 2>/dev/null`

### PBIR Detection
!`python ".claude/skills/pbi/scripts/detect.py" pbir 2>/dev/null || echo "PBIR=no"`

### Git State
!`python ".claude/skills/pbi/scripts/detect.py" git 2>/dev/null || (echo "GIT=no" && echo "HAS_COMMITS=no")`

### Session Context
!`python ".claude/skills/pbi/scripts/detect.py" context 2>/dev/null || echo "No prior context found."`

### Auto-Resume

After detection blocks run, apply the following before executing the command:

1. **PBIP_MODE=file, context exists** — Session Context output contains `## Model Context` with a table:
   - Count the table rows in the Model Context table.
   - Output on a single line: `Context resumed — [N] tables loaded`
   - Skip any "Model Context Check" (Step 0.5) below — context is already available.

2. **PBIP_MODE=file, no context yet** — Session Context has no `## Model Context` or `.pbi-context.md` does not exist:
   - Output: `No model context — auto-loading project...`
   - Read all files from File Index, extract table/measure/column/relationship structure, build the Model Context markdown block, write it to `.pbi-context.md`.
   - Output the summary table and: `Auto-loaded [N] tables. Context ready.`

3. **PBIP_MODE=paste — nearby folder check**:
   Run: `python ".claude/skills/pbi/scripts/detect.py" nearby 2>/dev/null`
   - If NEARBY_PBIP is found: output: `No PBIP project here, but found one at [NEARBY_PBIP]. Run cd "[NEARBY_PBIP]" first.`
   - If NEARBY_PBIP is empty: skip silently. Paste-in commands still work.

After auto-resume completes, proceed to the command instructions below.


---

# /pbi:changelog

<purpose>
Stakeholders need to know what changed in the model without reading git logs. This command turns commit history into polished release notes that anyone can understand.
</purpose>

<core_principle>
Write for stakeholders, not developers. "Added year-to-date revenue measure" is useful. "feat: add Revenue YTD to Sales table via /pbi:new" is not. Strip technical prefixes and translate to business language.
</core_principle>

## Git Log
!`git log --oneline --no-decorate -50 2>/dev/null || echo "NO_LOG"`

## Instructions

### Step 0 — Guards

**If PBIP_MODE=paste:** output and stop:
> No PBIP project found. Run /pbi:changelog from a directory containing a *.SemanticModel/ folder.

**If GIT=no:** output and stop:
> No git repo found. Run /pbi:commit to initialise one first.

**If HAS_COMMITS=no:** output and stop:
> No commits found. Make some changes and commit with /pbi:commit first.

Otherwise proceed to Step 1.

---

### Step 1 — Parse Scope

Read `$ARGUMENTS`:
- `--since [tag/date/hash]` → only include commits after that ref
- `--all` or empty → include all commits
- `--last [N]` → include last N commits

Default: all commits.

---

### Step 2 — Parse Commit Messages

Read the Git Log output. For each commit line (`[hash] [message]`), classify by conventional commit prefix:

| Prefix | Category |
|--------|----------|
| `feat:` | Added |
| `fix:` | Fixed |
| `chore:` | Changed |
| `merge:` | (skip — merge commits) |
| No prefix | Other |

Extract from each message:
- Category (from prefix)
- Description (everything after the prefix, trimmed)
- Hash (short form)

Group commits by category.

---

### Step 3 — Format Changelog

Build the changelog in this format:

```markdown
# Changelog

Generated: [current UTC date YYYY-MM-DD]
Project: $PBIP_DIR

---

## Added
- [description] ([hash])

## Fixed
- [description] ([hash])

## Changed
- [description] ([hash])
```

Rules:
- Omit any category section that has zero entries
- Within each category, list in reverse chronological order (newest first)
- Strip the conventional commit prefix from the description
- Skip merge commits entirely
- If `--since` was used, add a note: `Changes since: [ref]`

---

### Step 4 — Output and Write

Output the changelog to chat.

Then write to `CHANGELOG.md` in the project root:
1. Attempt to Read `CHANGELOG.md` (may not exist)
2. Write the full changelog using the Write tool

Output: "Changelog written to CHANGELOG.md"

---

### Step 5 — Update Session Context

Read `.pbi-context.md` (Read tool), update these sections, then Write the full file back:
- `## Last Command`: Command = `/pbi:changelog`, Timestamp = current UTC ISO 8601, Measure = `(git operation)`, Outcome = `Changelog generated — [N] entries`
- `## Command History`: Append one row; keep last 20 rows maximum.
- Do NOT modify `## Analyst-Reported Failures`.

### Anti-Patterns
- NEVER include noise-file changes in the changelog
- NEVER fabricate changes not present in git history
- NEVER include merge commits in the changelog output

## Post-Command Footer

After ALL steps above are complete (including session context update), output the context usage bar as the final line:

```bash
python ".claude/skills/pbi/scripts/detect.py" context-bar 2>/dev/null
```

Print the output of this command as the very last line shown to the user. Do not skip this step.


## Shared Rules

- **PYTHON-FIRST FILE OPERATIONS (CRITICAL):** All file read/write and text search operations MUST use Python with `encoding='utf-8'` to correctly handle accented characters (French: é, è, ê, ç, à, ù, etc.). Do NOT use `grep`, `cat`, `sed`, `awk`, or shell redirects for reading/writing model files. For measure name search, use `python ".claude/skills/pbi/scripts/detect.py" search "MeasureName" "$PBIP_DIR"` instead of `grep -rlF`. Shell/bash is allowed ONLY for: git CLI commands and Python script invocation.
- **PBIP folder naming:** Always use the `PBIP_DIR` value from detection (e.g., `Sales.SemanticModel`) — never hardcode `.SemanticModel`. Same for Report: use `PBIR_DIR` (e.g., `Sales.Report`).
- All bash paths must be double-quoted (e.g., `"$VAR"`, `"$SM_DIR/"`)
- Session context: Read-then-Write `.pbi-context.md`, 20 row max Command History, never touch Analyst-Reported Failures
- TMDL: tabs only for indentation
- TMSL expression format: preserve original form (string vs array); use array if expression has line breaks
- Escalation state: `## Escalation State` in `.pbi-context.md` tracks gathered context during escalation.
- **LOCAL-FIRST GIT POLICY (CRITICAL):** NEVER `git pull`, `git fetch`, `git merge`, `git rebase`, `git push`, or create PRs. Allowed: `git init`, `git add`, `git commit`, `git diff`, `git log`, `git status`, `git revert`, `git rev-parse`.
- **Post-write staging:** After any command writes files to `$PBIP_DIR/` (and PBIP_MODE=file, GIT=yes), auto-stage: `git add "$PBIP_DIR/" 2>/dev/null`. Skip if the command already auto-committed.
