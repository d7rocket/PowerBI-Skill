---
name: pbi:undo
description: "Revert the most recent auto-commit created by any PBI skill command (edit, comment, error, new, audit). Uses git revert to preserve history. Shows what will be reverted before executing. Only reverts PBI auto-commits."
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

# /pbi:undo

<purpose>
Auto-commits are convenient but sometimes wrong. One-command undo makes auto-commit safe — the analyst can always roll back without understanding git internals.
</purpose>

<core_principle>
Use git revert (not git reset) to preserve history. Only revert commits made by PBI skill commands — never revert manual commits. Show the diff before reverting.
</core_principle>

## Instructions

### Step 0 — Check git state

**If GIT=no:** output exactly this message and stop:

> No git repo found. Nothing to undo.

**If GIT=yes:** proceed to Step 1.

---

### Step 1 — Show last commit

Run these two commands:

```bash
git log --oneline -1 2>/dev/null
```

```bash
git diff HEAD~1..HEAD --stat 2>/dev/null
```

Capture both outputs.

**Auto-commit check:** If the last commit message does NOT start with `chore:`, `feat:`, or `fix:` (i.e., it doesn't look like an auto-commit from PBI skills), output this warning:

> The last commit does not appear to be a PBI auto-commit. Proceed with caution.

Output to analyst:

```
Last commit: [commit hash] [message]
Files changed: [stat output]

Revert this commit? (y/N)
```

---

### Step 2 — Wait for confirmation

- **y or Y:** proceed to Step 3.
- **n, N, Enter, or anything else:** output "Undo cancelled. No changes made." and stop.

---

### Step 3 — Revert

Run:

```bash
git revert HEAD --no-edit 2>/dev/null && echo "REVERT=ok" || echo "REVERT=fail"
```

- **REVERT=ok:** output "Reverted. The model files have been restored to their state before the last commit."
- **REVERT=fail:** output "Revert failed — there may be merge conflicts. Run `git status` to see the state, or `git revert --abort` to cancel."

---

### Step 4 — Update .pbi-context.md

Read `.pbi-context.md` (Read tool), update these sections, then Write the full file back:

1. Update `## Last Command` section: Command = `/pbi:undo`, Timestamp = current UTC ISO 8601, Outcome = `Reverted [commit message]`.
2. Append a new row to `## Command History`. Keep last 20 rows maximum.
3. Do NOT modify `## Analyst-Reported Failures` or any other sections.

### Anti-Patterns
- NEVER revert without showing the commit details and getting confirmation
- NEVER revert more than one commit at a time — use git revert for a single commit only
- NEVER use git reset --hard — always use git revert to preserve history

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
