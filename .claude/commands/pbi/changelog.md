---
name: pbi:changelog
description: "Generate structured release notes from git history in Keep a Changelog format"
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

Ensure .pbi/ directory exists and migrate legacy root-level files.
```bash
python ".claude/skills/pbi/scripts/detect.py" ensure-dir 2>/dev/null
python ".claude/skills/pbi/scripts/detect.py" migrate 2>/dev/null
```

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

Save the PBI_CONFIRM value — use it to decide whether to ask before writing files.
```bash
python ".claude/skills/pbi/scripts/detect.py" settings 2>/dev/null || echo "PBI_CONFIRM=true"
```

### Auto-Resume (session-aware)

After detection, apply the following before executing the command:

1. **PBIP_MODE=file — session load check**:
   Run:
   ```bash
   python ".claude/skills/pbi/scripts/detect.py" session-check 2>/dev/null
   ```
   - If output is `SESSION=active` — context was already loaded this session:
     - Count the table rows in the Model Context table from Session Context.
     - Output on a single line: `Context resumed — [N] tables loaded`
     - Skip any "Model Context Check" (Step 0.5) below — context is already available.
   - If output is `SESSION=new` — first command this session:
     - Output: `Loading model context (first command this session)...`
     - Read all files from File Index, extract table/measure/column/relationship structure, build the Model Context markdown block, write it to `.pbi/context.md`.
     - Write `**Session-Start:** [current UTC time in ISO 8601]` immediately after the `## Model Context` heading line in `.pbi/context.md`.
     - Output the summary table and: `Context loaded — [N] tables. Ready.`

2. **PBIP_MODE=paste — nearby folder check**:
   Run:
   ```bash
   python ".claude/skills/pbi/scripts/detect.py" nearby 2>/dev/null
   ```
   - If NEARBY_PBIP is found: output: `No PBIP project here, but found one at [NEARBY_PBIP]. Run cd "[NEARBY_PBIP]" first.`
   - If NEARBY_PBIP is empty: skip silently. Paste-in commands still work.

After auto-resume completes, proceed to the command instructions below.

---

# /pbi:changelog


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

Read `.pbi/context.md` (Read tool), update these sections, then Write the full file back:
- `## Last Command`: Command = `/pbi:changelog`, Timestamp = current UTC ISO 8601, Measure = `(git operation)`, Outcome = `Changelog generated — [N] entries`
- `## Command History`: Append one row; keep last 20 rows maximum.
- Do NOT modify `## Analyst-Reported Failures`.

### Anti-Patterns
- NEVER include noise-file changes in the changelog
- NEVER fabricate changes not present in git history
- NEVER include merge commits in the changelog output
