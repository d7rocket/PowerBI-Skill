---
name: pbi-commit
description: "Stage all semantic model changes and create a local git commit with an auto-generated business-language message. Analyzes diffs to produce messages like 'feat: add Revenue YTD measure'. Auto-initializes git if needed. All commits are LOCAL only — never pushes."
model: haiku
allowed-tools: Read, Write, Bash, Agent
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 6.1.0
  category: data-analytics
  tags: [power-bi, dax, pbip, semantic-model]
---

## Detection (run once)

**Folder naming:** Real PBIP projects use `<ProjectName>.SemanticModel` and `<ReportName>.Report`. Test fixtures may use `.SemanticModel`. Detection globs for both patterns.

### PBI Directory Setup
!`python ".claude/skills/pbi/scripts/detect.py" ensure-dir 2>/dev/null && python ".claude/skills/pbi/scripts/detect.py" migrate 2>/dev/null`

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

### Settings
!`python ".claude/skills/pbi/scripts/detect.py" settings 2>/dev/null || echo "PBI_CONFIRM=true"`

Save the `PBI_CONFIRM` value — commands use it to decide whether to ask before writing files.

### Auto-Resume (session-aware)

After detection blocks run, apply the following before executing the command:

1. **PBIP_MODE=file — session load check**:
   Run: `python ".claude/skills/pbi/scripts/detect.py" session-check 2>/dev/null`
   - If output is `SESSION=active` — context was already loaded this session:
     - Output on a single line: `Context resumed — [N] tables loaded` (count from Session Context)
     - Skip any "Model Context Check" (Step 0.5) below — context is already available.
   - If output is `SESSION=new` — first command this session:
     - Output: `Loading model context (first command this session)...`
     - Read all files from File Index, extract table/measure/column/relationship structure, build the Model Context markdown block, write it to `.pbi/context.md`.
     - Write `**Session-Start:** [current UTC time in ISO 8601]` immediately after the `## Model Context` heading line in `.pbi/context.md`.
     - Output the summary table and: `Context loaded — [N] tables. Ready.`

2. **PBIP_MODE=paste — nearby folder check**:
   Run: `python ".claude/skills/pbi/scripts/detect.py" nearby 2>/dev/null`
   - If NEARBY_PBIP is found: output: `No PBIP project here, but found one at [NEARBY_PBIP]. Run cd "[NEARBY_PBIP]" first.`
   - If NEARBY_PBIP is empty: skip silently. Paste-in commands still work.

After auto-resume completes, proceed to the command instructions below.


---

# /pbi-commit

<purpose>
Version control for PBIP projects should describe business changes, not file changes. Auto-generated messages ensure every commit is meaningful and searchable by business context.
</purpose>

<core_principle>
Commit messages describe business impact. Use conventional commit prefixes (feat, fix, refactor, docs). Never push, pull, or interact with remotes — local-first policy protects against overwriting PBIP relationships.
</core_principle>

> **LOCAL-FIRST POLICY (CRITICAL):** All commits are local only. NEVER run `git pull`, `git fetch`, `git push`, `git merge`, or any command that syncs with a remote. NEVER suggest pushing or pulling. NEVER create pull requests. The local copy is ALWAYS the source of truth. If a remote exists and is ahead, that is irrelevant — local wins.

## Instructions

### Step 0 — Check PBIP detection and git state

**If PBIP_MODE=paste:** output exactly and stop:

> No PBIP project found. Run /pbi-commit from a directory containing a *.SemanticModel/ folder.

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
python ".claude/skills/pbi/scripts/detect.py" gitignore-check 2>/dev/null
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

Use Read-then-Write to update `.pbi/context.md`:

1. Update `## Last Command` with these four lines in this exact order:
   - Command: /pbi-commit
   - Timestamp: [current UTC ISO 8601]
   - Measure: [comma-separated list of measure names from Step 3 parse; or "(initial commit)" if arriving from Step 1a or Step 1b]
   - Outcome: [commit subject line, or "chore: initial PBIP model commit" for initial commit flows]
2. Append row to `## Command History`; trim to 20 rows max.
3. Do NOT modify `## Model Context`, `## Analyst-Reported Failures`, or any other sections.

### Anti-Patterns
- NEVER run git pull, git fetch, git push, git merge, or any remote-syncing command
- NEVER commit noise files (*.abf, localSettings.json, .pbi/context.md, SecurityBindings)
- NEVER amend previous commits — always create new commits
- NEVER suggest pushing to a remote

## Shared Rules

- **PYTHON-FIRST FILE OPERATIONS (CRITICAL):** All file read/write and text search operations MUST use Python with `encoding='utf-8'` to correctly handle accented characters (French: é, è, ê, ç, à, ù, etc.). Do NOT use `grep`, `cat`, `sed`, `awk`, or shell redirects for reading/writing model files. For measure name search, use `python ".claude/skills/pbi/scripts/detect.py" search "MeasureName" "$PBIP_DIR"` instead of `grep -rlF`. Shell/bash is allowed ONLY for: git CLI commands and Python script invocation.
- **PBIP folder naming:** Always use the `PBIP_DIR` value from detection (e.g., `Sales.SemanticModel`) — never hardcode `.SemanticModel`. Same for Report: use `PBIR_DIR` (e.g., `Sales.Report`).
- All bash paths must be double-quoted (e.g., `"$VAR"`, `"$SM_DIR/"`)
- Session context: Read-then-Write `.pbi/context.md`, 20 row max Command History, never touch Analyst-Reported Failures
- TMDL: tabs only for indentation
- TMSL expression format: preserve original form (string vs array); use array if expression has line breaks
- Escalation state: `## Escalation State` in `.pbi/context.md` tracks gathered context during escalation.
- **LOCAL-FIRST GIT POLICY (CRITICAL):** NEVER `git pull`, `git fetch`, `git merge`, `git rebase`, `git push`, or create PRs. Allowed: `git init`, `git add`, `git commit`, `git diff`, `git log`, `git status`, `git revert`, `git rev-parse`.
- **Post-write staging:** After any command writes files to `$PBIP_DIR/` (and PBIP_MODE=file, GIT=yes), auto-stage: `git add "$PBIP_DIR/" 2>/dev/null`. Skip if the command already auto-committed.
- **Confirm mode (PBI_CONFIRM):** When `PBI_CONFIRM=true`: show preview and ask `(y/N)` before writing model files or output files. When `PBI_CONFIRM=false`: write directly without asking. Commands that already have a `(y/N)` prompt respect this — if PBI_CONFIRM=false, skip the prompt and proceed.
