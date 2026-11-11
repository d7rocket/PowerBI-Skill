---
name: changelog
description: "Generate structured release notes from local git history in Keep a Changelog format. Groups commits by type (Added, Changed, Fixed, Removed). Covers a configurable range. Writes to .pbi/changelog.md. Translates commit messages into user-facing release notes."
model: haiku
allowed-tools: Read, Write, Edit, Bash, Agent
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:changelog

<purpose>
Stakeholders need to know what changed in the model without reading git logs. This command turns commit history into polished release notes that anyone can understand.
</purpose>

<core_principle>
Write for stakeholders, not developers. "Added year-to-date revenue measure" is useful. "feat: add Revenue YTD to Sales table via /pbi:new" is not. Strip technical prefixes and translate to business language.
</core_principle>

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
- `--all` → include all commits (no cap)
- `--last [N]` → include last N commits

Default (no argument): last 50 commits.

---

### Step 2 — Read and Parse Commit History

Run the git log command that matches the scope from Step 1:

**`--all`:**
```bash
git log --oneline --no-decorate 2>/dev/null || echo "NO_LOG"
```

**`--since [ref]`:**
```bash
git log --oneline --no-decorate "[ref]..HEAD" 2>/dev/null || echo "NO_LOG"
```

**`--last [N]`:**
```bash
git log --oneline --no-decorate -[N] 2>/dev/null || echo "NO_LOG"
```

**Default (no argument):**
```bash
git log --oneline --no-decorate -50 2>/dev/null || echo "NO_LOG"
```

If the output is `NO_LOG` or empty: output "No commit history available." and stop.

For each commit line (`[hash] [message]`), classify by conventional commit prefix:

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

Output the changelog to chat as a preview.

Then write to `.pbi/changelog.md`:
1. Attempt to Read `.pbi/changelog.md` (may not exist)
2. Write the full changelog to `.pbi/changelog.md` using the Write tool

**Do NOT touch a root-level `CHANGELOG.md`** — if one exists in the project root, leave it as-is.

Output: "Changelog written to .pbi/changelog.md" — and if a root `CHANGELOG.md` exists, add: "(root CHANGELOG.md left untouched)"

---

### Step 5 - Log

If PBIP_MODE=file, log the command (one call, no file reads):

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:changelog" "<measure or target>" "<one-line outcome>"
```

### Anti-Patterns
- NEVER include noise-file changes in the changelog
- NEVER fabricate changes not present in git history
- NEVER include merge commits in the changelog output
