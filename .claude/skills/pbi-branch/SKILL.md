---
name: pbi-branch
description: Create and manage feature branches for PBIP model changes. Supports creating branches, switching, listing, and merging back to main. Use when an analyst wants to work on model changes in isolation before merging.
disable-model-invocation: true
model: sonnet
allowed-tools: Read, Write, Bash
---

## PBIP Context Detection

!`if [ -d ".SemanticModel" ]; then if [ -f ".SemanticModel/model.bim" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmsl"; elif [ -d ".SemanticModel/definition/tables" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; else echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; fi; else echo "PBIP_MODE=paste"; fi`

## Git State Check

!`GIT_INSIDE=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "GIT=yes" || echo "GIT=no"); CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "none"); echo "$GIT_INSIDE BRANCH=$CURRENT_BRANCH"`

## Session Context

!`cat .pbi-context.md 2>/dev/null | tail -80 || echo "No prior context found."`

---

## Instructions

### Step 0 — Guards

**If PBIP_MODE=paste:** output and stop:
> No PBIP project found. Run /pbi:branch from a directory containing .SemanticModel/.

**If GIT=no:** output and stop:
> No git repo found. Run /pbi:commit to initialise one first.

Otherwise proceed to Step 1.

---

### Step 1 — Parse Subcommand

Read `$ARGUMENTS` to determine the operation:

- `create [name]` or `new [name]` or just `[name]` (when name looks like a branch name) → **CREATE**
- `merge` or `done` or `finish` → **MERGE**
- `list` or `ls` → **LIST**
- `switch [name]` or `checkout [name]` → **SWITCH**
- Empty or ambiguous → output menu:

```
What would you like to do?

- **create [name]** — start a new feature branch
- **merge** — merge current branch back to main
- **list** — show all branches
- **switch [name]** — switch to a branch

Type your choice:
```

Wait for response and route accordingly.

---

### Step 2a — CREATE

**Validate branch name:**
- If no name provided, ask: "Name for the new branch (e.g., `add-revenue-measures`):"
- Sanitise: lowercase, replace spaces with hyphens, strip special characters except hyphens and slashes
- Prefix with `pbi/` if not already prefixed (e.g., `add-revenue-measures` → `pbi/add-revenue-measures`)

**Check for uncommitted changes:**
```bash
git status --porcelain '.SemanticModel/' 2>/dev/null
```
If output is non-empty:
- Output: "You have uncommitted model changes. Commit them first with /pbi:commit, or they'll carry into the new branch."
- Output: "Continue anyway? (y/N)"
- On n/N/Enter: stop.
- On y/Y: continue.

**Create and switch to branch:**
```bash
git checkout -b "[BRANCH_NAME]" 2>/dev/null && echo "BRANCH_CREATED=[BRANCH_NAME]" || echo "BRANCH_FAIL"
```

- BRANCH_CREATED: Output:
  > Branch `[BRANCH_NAME]` created. You're now on this branch.
  > Make your changes, then run `/pbi:branch merge` when done.

- BRANCH_FAIL: Output:
  > Failed to create branch. A branch with this name may already exist. Check `git branch -a`.

---

### Step 2b — MERGE

**Identify branches:**
```bash
CURRENT=$(git branch --show-current 2>/dev/null); DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main"); echo "CURRENT=$CURRENT DEFAULT=$DEFAULT"
```

If CURRENT equals DEFAULT (already on main/master):
- Output: "You're already on [DEFAULT]. Switch to a feature branch first with `/pbi:branch switch [name]`."
- Stop.

**Check for uncommitted changes:**
```bash
git status --porcelain '.SemanticModel/' 2>/dev/null
```
If non-empty:
- Output: "Uncommitted model changes detected. Commit with /pbi:commit first."
- Stop.

**Show what will be merged:**
```bash
git log --oneline "$DEFAULT".."$CURRENT" 2>/dev/null
```

Output:
```
**Merging `[CURRENT]` → `[DEFAULT]`**

Commits to merge:
[list of commits from git log]

Proceed with merge? (y/N)
```

- On n/N/Enter: stop.
- On y/Y:

```bash
git checkout "$DEFAULT" 2>/dev/null && git merge "$CURRENT" --no-ff -m "merge: [CURRENT] into $DEFAULT" 2>/dev/null && echo "MERGE=ok" || echo "MERGE=conflict"
```

- MERGE=ok:
  > Merged `[CURRENT]` into `[DEFAULT]`.
  > Delete the feature branch? (y/N)
  - On y/Y: `git branch -d "[CURRENT]" 2>/dev/null`; Output "Branch `[CURRENT]` deleted."
  - On n/N/Enter: Output "Branch `[CURRENT]` kept."

- MERGE=conflict:
  > Merge conflict detected. Resolve conflicts manually, then run `git add . && git commit`.
  > To abort: `git merge --abort`

---

### Step 2c — LIST

```bash
git branch -a 2>/dev/null
```

Output:
```
**Branches**
[formatted branch list — mark current branch with *, highlight pbi/ prefixed branches]
```

---

### Step 2d — SWITCH

```bash
git checkout "[BRANCH_NAME]" 2>/dev/null && echo "SWITCHED=[BRANCH_NAME]" || echo "SWITCH_FAIL"
```

- SWITCHED: Output "Switched to `[BRANCH_NAME]`."
- SWITCH_FAIL: Output "Branch `[BRANCH_NAME]` not found. Run `/pbi:branch list` to see available branches."

---

### Step 3 — Update Session Context

Read `.pbi-context.md` (Read tool), update these sections, then Write the full file back:
- `## Last Command`: Command = `/pbi:branch`, Timestamp = current UTC ISO 8601, Measure = `(git operation)`, Outcome = `[operation] — [branch name]`
- `## Command History`: Append one row `| [timestamp] | /pbi:branch | (git operation) | [outcome] |`; keep last 20 rows maximum.
- Do NOT modify `## Analyst-Reported Failures`.
