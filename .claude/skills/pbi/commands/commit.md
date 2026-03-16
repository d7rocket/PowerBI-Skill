# /pbi commit

> Detection context (PBIP_MODE, PBIP_FORMAT, PBIP_DIR, File Index, Git State, Session Context) is provided by the router.

## Instructions

### Step 0 — Check PBIP detection and git state

**If PBIP_MODE=paste:** output exactly and stop:

> No PBIP project found. Run /pbi commit from a directory containing a *.SemanticModel/ folder.

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
git add "$PBIP_DIR/" ".gitignore" && git commit -m "chore: initial PBIP model commit"
```

**4. Output to analyst:**

> Git repo initialised. Initial commit created: chore: initial PBIP model commit
> To push to a remote: git remote add origin <url> && git push -u origin main

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

- **COMMIT=ok:** output: `Committed. Run: git push`
- **COMMIT=fail:** output: `Commit failed — check git status. File changes are intact.`

---

### Step 5 — Context update

Use Read-then-Write to update `.pbi-context.md`:

1. Update `## Last Command` with these four lines in this exact order:
   - Command: /pbi commit
   - Timestamp: [current UTC ISO 8601]
   - Measure: [comma-separated list of measure names from Step 3 parse; or "(initial commit)" if arriving from Step 1a or Step 1b]
   - Outcome: [commit subject line, or "chore: initial PBIP model commit" for initial commit flows]
2. Append row to `## Command History`; trim to 20 rows max.
3. Do NOT modify `## Model Context`, `## Analyst-Reported Failures`, or any other sections.
