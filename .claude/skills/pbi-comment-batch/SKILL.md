---
name: pbi-comment-batch
description: Apply commenting across all measures in a table or the entire model at once. Generates inline // comments and Description fields for every measure. Use when an analyst wants to document all measures in bulk.
disable-model-invocation: true
model: sonnet
allowed-tools: Read, Write, Bash
---

## PBIP Detection

!`if [ -d ".SemanticModel" ]; then if [ -f ".SemanticModel/model.bim" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmsl"; elif [ -d ".SemanticModel/definition/tables" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; else echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; fi; else echo "PBIP_MODE=paste"; fi`

## Desktop Check

!`tasklist /fi "imagename eq PBIDesktop.exe" 2>/dev/null | findstr /i "PBIDesktop.exe" >nul 2>&1 && echo "DESKTOP=open" || echo "DESKTOP=closed"`

## PBIP File Index

!`if [ -d ".SemanticModel/definition/tables" ]; then find ".SemanticModel/definition/tables/" -name "*.tmdl" 2>/dev/null; elif [ -f ".SemanticModel/model.bim" ]; then echo "tmsl:.SemanticModel/model.bim"; fi`

## Session Context

!`cat .pbi-context.md 2>/dev/null | tail -80 || echo "No prior context found."`

---

## Instructions

### Step 0 — PBIP-Only Guard

If PBIP Detection output contains `PBIP_MODE=paste`:
- Output: "Batch commenting requires a PBIP project. Run /pbi:comment-batch from a directory containing .SemanticModel/. For a single measure, use /pbi:comment instead."
- Stop.

If `PBIP_MODE=file`: output header:
> File mode — PBIP project detected ([FORMAT]) | Desktop: [STATUS]

---

### Step 1 — Scope Selection

If `$ARGUMENTS` contains a table name (e.g., `--table Sales` or just `Sales`):
- Set SCOPE=table, TARGET_TABLE=[table name]

If `$ARGUMENTS` contains `--all` or `all`:
- Set SCOPE=all

Otherwise output: "Comment all measures in one table, or the entire model?"
- "**One table** — type the table name"
- "**All** — type `all`"

Wait for response and set SCOPE accordingly.

---

### Step 2 — Discover Measures

**If PBIP_FORMAT=tmdl:**

Read each `.tmdl` file (from PBIP File Index) that matches the scope:
- SCOPE=table: read only `[TARGET_TABLE].tmdl`
- SCOPE=all: read all `.tmdl` files

For each file, extract all measure blocks:
- Measure name: text after `measure ` up to ` =`, stripping single quotes
- Expression: lines from the `=` through the next property line (`formatString:`, `displayFolder:`) or next entity block
- Existing description: `///` lines immediately above the measure keyword (may be absent)

**If PBIP_FORMAT=tmsl:**

Read `.SemanticModel/model.bim`. For each table matching the scope, extract:
- Measure name, expression, existing description

Build the measure list. Output progress:
> Found [N] measures in [scope description]. Processing...

If N=0: Output "No measures found in [scope]. Nothing to comment." Stop.

---

### Step 3 — Generate Comments for Each Measure

For each measure in the list, generate:

**Inline comments** (following the same rules as /pbi:comment Step 4):
- One comment above the measure name line describing overall business purpose
- Comments above CALCULATE arguments explaining filter logic in business terms
- Comments above VAR declarations explaining what each variable holds
- Comment above RETURN statement
- Do NOT comment every line — only non-obvious business logic
- Do NOT translate DAX syntax word-for-word

**Description field** (following /pbi:comment Step 5 rules):
- 1–3 sentences, plain business English
- Max 300 characters, no DAX function names, no markdown
- Ends with a period

**Skip rule:** If a measure already has a `///` description AND the expression already contains `//` comments, mark it as "already commented" and skip. Include it in the summary as skipped.

---

### Step 4 — Preview and Confirmation

Output a summary table:

```
**Batch Comment Preview**

| # | Measure | Table | Status |
|---|---------|-------|--------|
| 1 | [Name] | [Table] | New comments |
| 2 | [Name] | [Table] | Updated comments |
| 3 | [Name] | [Table] | Skipped (already commented) |

[N] measures will be commented, [M] skipped.

Apply all comments? (y/N)
```

- y or Y: proceed to Step 5.
- n, N, Enter, or anything else: Output "Batch cancelled. No files modified." Stop.

---

### Step 5 — Write Back

**If DESKTOP=open:**
- Output each measure's commented DAX and description in sequence (paste-ready format, same as /pbi:comment output structure)
- Output: "Desktop is open — paste each measure manually."
- Skip to Step 6.

**If DESKTOP=closed:**

**TMDL path:**
For each table file that contains measures to update:
1. Read the .tmdl file (Read tool)
2. For each measure in that file:
   - Replace or insert `///` description line directly above the measure declaration (no blank line between `///` and `measure`)
   - Replace the expression body with the commented DAX
   - Preserve tab indentation, formatString, displayFolder, and all other properties
3. Write the entire modified file back (Write tool) — one write per table file

**TMSL path:**
1. Read `.SemanticModel/model.bim` (Read tool)
2. For each measure to update:
   - Set `"description"` to the generated description
   - Update `"expression"` with commented DAX (use array form if multiline)
   - Preserve all other fields
3. Write the entire model.bim back (Write tool) — single write

Output for each file written:
> Written: [N] measures in [file path]

**Auto-commit (single commit for all changes):**
```bash
GIT_STATUS=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "yes" || echo "no")
if [ "$GIT_STATUS" = "yes" ]; then
  git add '.SemanticModel/' 2>/dev/null
  git commit -m "chore: batch comment [N] measures in [scope]" 2>/dev/null && echo "AUTO_COMMIT=ok" || echo "AUTO_COMMIT=fail"
else
  echo "AUTO_COMMIT=skip_no_repo"
fi
```
- AUTO_COMMIT=ok: Output "Auto-committed: chore: batch comment [N] measures in [scope]"
- AUTO_COMMIT=skip_no_repo: Output "No git repo — run /pbi:commit to initialise one."
- AUTO_COMMIT=fail: silent (non-fatal)

---

### Step 6 — Update Session Context

Read `.pbi-context.md` (Read tool), update these sections, then Write the full file back:
- `## Last Command`: Command = `/pbi:comment-batch`, Timestamp = current UTC ISO 8601, Measure = `[N] measures in [scope]`, Outcome = `Batch commented`
- `## Command History`: Append one row `| [timestamp] | /pbi:comment-batch | [N] measures | Batch commented |`; keep last 20 rows maximum.
- Do NOT modify `## Analyst-Reported Failures`.

---

### Anti-Patterns
- NEVER write one file per measure — batch all changes for a table file into a single Write
- NEVER skip the confirmation prompt
- NEVER modify measures marked as "already commented" unless the analyst explicitly requests overwrite
- NEVER convert tabs to spaces in TMDL files
- NEVER write when Desktop is open
