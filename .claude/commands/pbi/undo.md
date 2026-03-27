---
name: pbi:undo
description: "Revert the last auto-commit"
allowed-tools:
  - Read
  - Write
  - Bash
  - Agent
  - Glob
  - Grep
---

## Detection

Run ALL of the following detection commands using the Bash tool before proceeding. Save the output — subsequent steps reference these values.

```bash
python ".claude/skills/pbi/scripts/detect.py" pbip 2>/dev/null || echo "PBIP_MODE=paste"
```

Save the `PBIP_DIR` value from the output — all subsequent steps must use it instead of a hardcoded `.SemanticModel`.

```bash
python ".claude/skills/pbi/scripts/detect.py" files 2>/dev/null
```

```bash
python ".claude/skills/pbi/scripts/detect.py" pbir 2>/dev/null || echo "PBIR=no"
```

```bash
python ".claude/skills/pbi/scripts/detect.py" git 2>/dev/null || (echo "GIT=no" && echo "HAS_COMMITS=no")
```

```bash
python ".claude/skills/pbi/scripts/detect.py" context 2>/dev/null || echo "No prior context found."
```

### Auto-Resume

After detection, apply the following before executing the command:

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