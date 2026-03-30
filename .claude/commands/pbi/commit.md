---
name: pbi:commit
description: "Auto-generated business-language commits for semantic model changes (local only, never pushes)"
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

# /pbi:commit


> **LOCAL-FIRST POLICY (CRITICAL):** All commits are local only. NEVER run `git pull`, `git fetch`, `git push`, `git merge`, or any command that syncs with a remote. NEVER suggest pushing or pulling. NEVER create pull requests. The local copy is ALWAYS the source of truth. If a remote exists and is ahead, that is irrelevant — local wins.

## Instructions

### Step 0 — Check PBIP detection and git state

**If PBIP_MODE=paste:** output exactly and stop:

> No PBIP project found. Run /pbi:commit from a directory containing a *.SemanticModel/ folder.

**If PBIP_MODE=file AND GIT=no:** proceed to Step 1a (git init flow).

**If PBIP_MODE=file AND GIT=yes AND HAS_COMMITS=no:** proceed to Step 1b (initial commit on existing empty repo).

**If PBIP_MODE=file AND GIT=yes AND HAS_COMMITS=yes:** proceed to Step 2 (normal commit flow).

---

### Step 1a — Git init flow (no git repo exists)

Run these in sequence:

**1. Initialise the repo:**
```bash
git init
```

**2. Write `.gitignore`** using the Write tool with this exact content:

```
# Power BI noise files
*.abf
localSettings.json
.pbi-context.md
SecurityBindings
*.pbids
cache/
unappliedChanges.json
```

**3. Stage and create the initial commit:**
```bash
git add "$PBIP_DIR/" ".gitignore" && git commit -m "chore: initial PBIP model commit"
```

**4. Output to analyst:**

> Git repo initialised. Initial commit created: chore: initial PBIP model commit

**5. Proceed to Step 5 (context update). Do NOT run Steps 2–4.**

---

### Step 1b — Initial commit on empty repo (repo exists but no commits yet)

```bash
git add "$PBIP_DIR/" && git commit -m "chore: initial PBIP model commit"
```

> Initial commit created: chore: initial PBIP model commit

Proceed to Step 5 (context update).

---

### Step 2 — Get diff for message generation

**TMDL:**
```bash
git diff HEAD -- "$PBIP_DIR/definition/tables/" "$PBIP_DIR/definition/relationships.tmdl" 2>/dev/null
```

**TMSL:**
```bash
git diff HEAD -- "$PBIP_DIR/model.bim" 2>/dev/null
```

**If the diff output is empty:** output and stop:

> No changes to commit in $PBIP_DIR/.

---

### Step 3 — Parse diff and generate commit message

#### TMDL parsing rules

Only process lines starting with `+` (not `+++`) or `-` (not `---`). Ignore context lines and hunk headers.

- **MEASURE ADDED:** a `+ measure Name =` line with no matching `- measure Name =`.
- **MEASURE REMOVED:** a `- measure Name =` line with no matching `+ measure Name =`.
- **MEASURE MODIFIED:** both `+` and `-` lines for same name, OR changed lines inside a measure block.
- Extract measure name: text between `measure ` and ` =`; strip single quotes.
- Extract table name: from file path `tables/TableName.tmdl`.
- **RELATIONSHIP ADDED/REMOVED:** `+`/`-` relationship lines.
- **TABLE ADDED/REMOVED:** `+`/`-` table lines.

#### TMSL parsing rules

- Identify measure objects by `"name":` fields inside `"measures":` arrays.
- All `+` lines → added, all `-` → removed, mix → modified.

#### Conventional commit prefix inference

| Change detected | Prefix |
|----------------|--------|
| Any measure or table ADDED | feat: |
| Any measure REMOVED | fix: |
| Only expression or description changes | chore: |
| Only formatString / displayFolder changes | chore: |
| Relationship added | feat: |
| Relationship removed | fix: |
| Mixed adds and changes | feat: |

#### Build the commit message

1. Apply prefix inference.
2. Build subject line: `[prefix] [primary verb] [primary item] in [table/model]` — max 72 chars.
3. Build body: one bullet per changed item.
4. Full commit message = subject + blank line + body. Omit body if only one change.

Show the analyst the planned commit message before executing:

```
**Committing with message:**
[subject line]

[body if present]
```

---

### Step 4 — Stage and commit

```bash
git add "$PBIP_DIR/definition/" "$PBIP_DIR/model.bim" "$PBIP_DIR/definition.pbism" 2>/dev/null && git commit -m "[full message]" 2>/dev/null && echo "COMMIT=ok" || echo "COMMIT=fail"
```

- **COMMIT=ok:** output: `Committed locally.`
- **COMMIT=fail:** output: `Commit failed — check git status. File changes are intact.`

---

### Step 5 — Context update

Use Read-then-Write to update `.pbi-context.md`:

1. Update `## Last Command` with these four lines in this exact order:
   - Command: /pbi:commit
   - Timestamp: [current UTC ISO 8601]
   - Measure: [comma-separated list of measure names from Step 3 parse; or "(initial commit)" if arriving from Step 1a or Step 1b]
   - Outcome: [commit subject line, or "chore: initial PBIP model commit" for initial commit flows]
2. Append row to `## Command History`; trim to 20 rows max.
3. Do NOT modify `## Model Context`, `## Analyst-Reported Failures`, or any other sections.

### Anti-Patterns
- NEVER run git pull, git fetch, git push, git merge, or any remote-syncing command
- NEVER commit noise files (*.abf, localSettings.json, .pbi-context.md, SecurityBindings)
- NEVER amend previous commits — always create new commits
- NEVER suggest pushing to a remote

## Post-Command Footer

After ALL steps above are complete (including session context update), output the context usage bar as the final line:

```bash
python ".claude/skills/pbi/scripts/detect.py" context-bar 2>/dev/null
```

Print the output of this command as the very last line shown to the user. Do not skip this step.