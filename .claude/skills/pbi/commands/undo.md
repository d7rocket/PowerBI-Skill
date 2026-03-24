# /pbi undo

> Detection context (Git State, Session Context) is provided by the router.

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

1. Update `## Last Command` section: Command = `/pbi undo`, Timestamp = current UTC ISO 8601, Outcome = `Reverted [commit message]`.
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
