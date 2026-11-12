---
name: commit
description: "Save a local commit with a business-language message."
model: haiku
allowed-tools: Read, Write, Edit, Bash, Agent
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:commit

<purpose>
Version control for PBIP projects should describe business changes, not file changes. Auto-generated messages ensure every commit is meaningful and searchable by business context.
</purpose>

<core_principle>
Commit messages describe business impact. Use conventional commit prefixes (feat, fix, refactor, docs). Never push, pull, or interact with remotes — local-first policy protects against overwriting PBIP relationships.
</core_principle>

> **LOCAL-FIRST POLICY (CRITICAL):** All commits are local only. NEVER run `git pull`, `git fetch`, `git push`, `git merge`, or any command that syncs with a remote. NEVER suggest pushing or pulling. NEVER create pull requests. The local copy is ALWAYS the source of truth. If a remote exists and is ahead, that is irrelevant — local wins.

## Instructions

### Step 0 — Check PBIP detection and git state

**Live changes first:** if the preflight block shows `PENDING_LIVE_CHANGES`, run `detect.py snapshot`. `SNAPSHOT_COMMITTED` means the Desktop save was committed with its original message: report it and continue only if other changes remain. `SNAPSHOT=waiting` means the live changes are not saved in Desktop yet: say `Press Ctrl+S in Desktop first, then run /pbi:commit again.` and stop.

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

**2. Ensure `.gitignore`** — run this instead of writing a hardcoded file (detect.py is the single source of truth for gitignore entries):
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" gitignore-check 2>/dev/null
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
git diff HEAD -- "$PBIP_DIR/definition/" 2>/dev/null
```

This covers the whole definition folder — tables, relationships.tmdl, expressions.tmdl, model.tmdl, and any other definition files.

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
- **POWER QUERY EXPRESSION CHANGED:** any `+`/`-` lines in `expressions.tmdl` (or inside a `partition`/`source` M block) → describe as "Power Query expression changed" (extract the expression/table name if visible).
- **MODEL-LEVEL PROPERTY CHANGED:** any `+`/`-` lines in `model.tmdl` → describe as "model-level property changed" (e.g., culture, discourageImplicitMeasures, annotations).

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

### Step 5 - Log

If PBIP_MODE=file, log the command (one call, no file reads):

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:commit" "<measure or target>" "<one-line outcome>"
```

### Anti-Patterns
- NEVER add a `Co-Authored-By` line or any other trailer. The commit message is the business message only.
- NEVER amend or rewrite an existing commit.
- NEVER run git pull, git fetch, git push, git merge, or any remote-syncing command
- NEVER commit noise files (*.abf, localSettings.json, .pbi/context.md, SecurityBindings)
- NEVER amend previous commits — always create new commits
- NEVER suggest pushing to a remote
