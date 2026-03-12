---
name: pbi-changelog
description: Generate a human-readable CHANGELOG.md from git history. Parses conventional commit messages and groups changes by type. Use when an analyst wants a changelog or release notes.
disable-model-invocation: true
model: sonnet
allowed-tools: Read, Write, Bash
---

## PBIP Context Detection

!`if [ -d ".SemanticModel" ]; then if [ -f ".SemanticModel/model.bim" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmsl"; elif [ -d ".SemanticModel/definition/tables" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; else echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; fi; else echo "PBIP_MODE=paste"; fi`

## Git State Check

!`GIT_INSIDE=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "GIT=yes" || echo "GIT=no"); HAS_COMMITS=$(git rev-parse HEAD 2>/dev/null && echo "HAS_COMMITS=yes" || echo "HAS_COMMITS=no"); echo "$GIT_INSIDE $HAS_COMMITS"`

## Git Log

!`git log --oneline --no-decorate -50 2>/dev/null || echo "NO_LOG"`

## Session Context

!`cat .pbi-context.md 2>/dev/null | tail -80 || echo "No prior context found."`

---

## Instructions

### Step 0 — Guards

**If PBIP_MODE=paste:** output and stop:
> No PBIP project found. Run /pbi:changelog from a directory containing .SemanticModel/.

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
Project: .SemanticModel

---

## Added
- [description] ([hash])
- [description] ([hash])

## Fixed
- [description] ([hash])

## Changed
- [description] ([hash])
```

Rules:
- Omit any category section that has zero entries
- Within each category, list in reverse chronological order (newest first)
- Strip the conventional commit prefix from the description (e.g., `feat: add [Revenue YTD]` → `add [Revenue YTD]`)
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

Read `.pbi-context.md` (Read tool), update these sections, then Write the full file back:
- `## Last Command`: Command = `/pbi:changelog`, Timestamp = current UTC ISO 8601, Measure = `(git operation)`, Outcome = `Changelog generated — [N] entries`
- `## Command History`: Append one row `| [timestamp] | /pbi:changelog | (git operation) | Changelog generated |`; keep last 20 rows maximum.
- Do NOT modify `## Analyst-Reported Failures`.
