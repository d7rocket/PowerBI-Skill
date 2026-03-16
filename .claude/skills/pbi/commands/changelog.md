# /pbi changelog

> Detection context (PBIP_MODE, PBIP_FORMAT, PBIP_DIR, Git State, Session Context) is provided by the router.

## Git Log
!`git log --oneline --no-decorate -50 2>/dev/null || echo "NO_LOG"`

## Instructions

### Step 0 — Guards

**If PBIP_MODE=paste:** output and stop:
> No PBIP project found. Run /pbi changelog from a directory containing a *.SemanticModel/ folder.

**If GIT=no:** output and stop:
> No git repo found. Run /pbi commit to initialise one first.

**If HAS_COMMITS=no:** output and stop:
> No commits found. Make some changes and commit with /pbi commit first.

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

Read `.pbi-context.md` (Read tool), update these sections, then Write the full file back:
- `## Last Command`: Command = `/pbi changelog`, Timestamp = current UTC ISO 8601, Measure = `(git operation)`, Outcome = `Changelog generated — [N] entries`
- `## Command History`: Append one row; keep last 20 rows maximum.
- Do NOT modify `## Analyst-Reported Failures`.
