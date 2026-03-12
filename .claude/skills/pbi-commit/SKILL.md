---
name: pbi-commit
description: Stage PBIP model changes and create a local git commit with an auto-generated business-language message. Use when an analyst wants to commit changes or save a snapshot of the model.
disable-model-invocation: true
model: sonnet
allowed-tools: Read, Write, Bash
---

## PBIP Context Detection
!`PBIP_RESULT=""; if [ -d ".SemanticModel" ]; then PBISM=$(cat ".SemanticModel/definition.pbism" 2>/dev/null); if echo "$PBISM" | grep -q '"version": "1.0"'; then PBIP_RESULT="PBIP_MODE=file PBIP_FORMAT=tmsl"; else PBIP_RESULT="PBIP_MODE=file PBIP_FORMAT=tmdl"; fi; else PBIP_RESULT="PBIP_MODE=paste"; fi; echo "$PBIP_RESULT"`

## Git State Check
!`GIT_INSIDE=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "GIT=yes" || echo "GIT=no"); HAS_COMMITS=$(git rev-parse HEAD 2>/dev/null && echo "HAS_COMMITS=yes" || echo "HAS_COMMITS=no"); echo "$GIT_INSIDE $HAS_COMMITS"`

## Session Context
!`cat .pbi-context.md 2>/dev/null | tail -80 || echo "No prior context found."`

---

## Instructions

### Step 0 — Check PBIP detection and git state

Read the output from the PBIP Context Detection block and Git State Check block above.

**If PBIP_MODE=paste:** output exactly this message and stop. Do not run any git commands. Do not proceed.

> No PBIP project found. Run /pbi:commit from a directory containing .SemanticModel/.

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
```

**3. Stage and create the initial commit:**
```bash
git add '.SemanticModel/' '.gitignore' && git commit -m "chore: initial PBIP model commit"
```

**4. Output to analyst:**

> Git repo initialised. Initial commit created: chore: initial PBIP model commit
> To push to a remote: git remote add origin <url> && git push -u origin main

**5. Proceed to Step 5 (context update). Do NOT run Steps 2–4.**

---

### Step 1b — Initial commit on empty repo (repo exists but no commits yet)

Treat all `.SemanticModel/` files as new.

**1. Stage and create the initial commit:**
```bash
git add '.SemanticModel/' && git commit -m "chore: initial PBIP model commit"
```

**2. Output to analyst:**

> Initial commit created: chore: initial PBIP model commit

**3. Proceed to Step 5 (context update). Do NOT run Steps 2–4.**

---

### Step 2 — Get diff for message generation

Based on PBIP_FORMAT, run the appropriate scoped diff command:

**TMDL (PBIP_FORMAT=tmdl):**
```bash
git diff HEAD -- '.SemanticModel/definition/tables/' '.SemanticModel/definition/relationships.tmdl' 2>/dev/null
```

**TMSL (PBIP_FORMAT=tmsl):**
```bash
git diff HEAD -- '.SemanticModel/model.bim' 2>/dev/null
```

Capture the full diff text output.

**If the diff output is empty (nothing staged or changed):** output exactly this message and stop. Do not run git add or git commit.

> No changes to commit in .SemanticModel/.

---

### Step 3 — Parse diff and generate commit message

Apply the parsing rules below to identify all changes. Then build the conventional commit message.

#### TMDL parsing rules

Only process lines starting with `+` (not `+++`) or `-` (not `---`). Ignore context lines (space prefix) and hunk headers (`@@`).

- **MEASURE ADDED:** a `+ measure Name =` or `+ measure 'Name' =` line with no matching `- measure Name =` in the same file's diff.
- **MEASURE REMOVED:** a `- measure Name =` line with no matching `+ measure Name =` in the same file's diff.
- **MEASURE MODIFIED:** both `+ measure Name =` and `- measure Name =` lines present, OR changed lines inside a measure block (formatString, description `///` lines, expression body) with the declaration line unchanged.
- Extract measure name: text between `measure ` and ` =`; strip single quotes if present.
- Extract table name: from file path `tables/TableName.tmdl` → `TableName`.
- **RELATIONSHIP ADDED:** `+ relationship ` line.
- **RELATIONSHIP REMOVED:** `- relationship ` line.
- **TABLE ADDED:** `+ table ` line in a file path not previously seen.
- **TABLE REMOVED:** `- table ` line.
- **MODEL PROPERTY CHANGE:** only `formatString`, `displayFolder`, or `///` description lines changed within a measure block.

#### TMSL parsing rules

- Identify measure object boundaries by `"name":` fields inside `"measures":` array context.
- If all lines of a measure object are `+` lines → measure added.
- If all lines of a measure object are `-` lines → measure removed.
- If a mix of `+`/`-` lines inside an existing named measure → measure modified.
- Relationship changes: `+`/`-` lines inside `"relationships":` array.

#### Conventional commit prefix inference

| Change detected | Prefix |
|----------------|--------|
| Any measure or table ADDED | feat: |
| Any measure REMOVED | fix: |
| Only expression or description changes | chore: |
| Only formatString / displayFolder changes | chore: |
| Relationship added | feat: |
| Relationship removed | fix: |
| Mixed adds and changes | feat: (most significant wins) |

#### Build the commit message

1. Apply the prefix inference table to determine prefix (`feat:` / `fix:` / `chore:`).
2. Build subject line: `[prefix]: [primary verb] [primary item] in [table/model]` — max 72 chars.
   - Examples:
     - `feat: add [Revenue YTD] measure to Sales`
     - `chore: update display folder for 3 measures in Products`
     - `fix: remove bidirectional filter on Sales → Date relationship`
3. Build body: one bullet per changed item.
   - Format: `- add [Name] to Table`, `- modify [Name] expression in Table`, `- remove [Name] from Table`
4. Full commit message = subject + blank line + body. Omit body if only one change.

Show the analyst the planned commit message before executing:

```
**Committing with message:**
[subject line]

[body if present]
```

---

### Step 4 — Stage and commit

Run as a single bash block:

```bash
git add '.SemanticModel/' 2>/dev/null && git commit -m "[full message]" 2>/dev/null && echo "COMMIT=ok" || echo "COMMIT=fail"
```

Replace `[full message]` with the actual generated commit message (subject + blank line + body).

- **COMMIT=ok:** output exactly: `Committed. Run: git push` (this is output text only — push is always manual, never automatic)
- **COMMIT=fail:** output exactly: `Commit failed — check git status. File changes are intact.`

---

### Step 5 — Context update

Use Read-then-Write to update `.pbi-context.md`:

1. Read `.pbi-context.md` using the Read tool.
2. Update:
   - `## Last Command` section: Command = `/pbi:commit`, Timestamp = current UTC, Outcome = the commit subject line (e.g. `feat: add [Revenue YTD] measure to Sales`).
   - `## Command History` section: append a row with same values; trim to 20 rows max.
3. Do NOT modify `## Model Context`, `## Analyst-Reported Failures`, or any other sections.
4. Write the full updated file using the Write tool.
