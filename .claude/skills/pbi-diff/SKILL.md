---
name: pbi-diff
description: Show a human-readable summary of PBIP model changes since the last git commit. Use when an analyst asks what changed, wants a diff, or wants to review model changes before committing.
disable-model-invocation: true
model: sonnet
allowed-tools: Read, Write, Bash
---

## PBIP Context Detection
!`if [ -d ".SemanticModel" ]; then if [ -f ".SemanticModel/model.bim" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmsl"; elif [ -d ".SemanticModel/definition/tables" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; else echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; fi; else echo "PBIP_MODE=paste"; fi`

## Git State Check
!`GIT_INSIDE=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "GIT=yes" || echo "GIT=no"); HAS_COMMITS=$(git rev-parse HEAD 2>/dev/null && echo "HAS_COMMITS=yes" || echo "HAS_COMMITS=no"); echo "$GIT_INSIDE $HAS_COMMITS"`

## Session Context
!`cat .pbi-context.md 2>/dev/null | tail -80 || echo "No prior context found."`

---

## Instructions

### Step 0 — Check PBIP and git state

Read the output from the PBIP Context Detection and Git State Check blocks above.

**If PBIP_MODE=paste:** output exactly this message and stop. Do not proceed further.

> No PBIP project found. Run /pbi:diff from a directory containing .SemanticModel/.

**If GIT=no:** output exactly this message and stop. Do not proceed further.

> No git repo found. Run /pbi:commit to initialise one.

**If GIT=yes and HAS_COMMITS=no:** proceed to Step 1 with the note that this is an empty repo — treat all .SemanticModel/ files as new additions. In Step 2, use `git status --porcelain '.SemanticModel/' 2>/dev/null` as the diff source instead of `git diff HEAD`.

**Otherwise (GIT=yes and HAS_COMMITS=yes):** proceed to Step 1.

---

### Step 1 — Gitignore hygiene check (silent auto-fix)

Run this bash block to ensure all noise file entries are present in `.gitignore`. Do NOT output any message to the analyst. Do NOT pause. Silently continue to Step 2 once GITIGNORE_OK is seen.

!`grep -qE '^(\*\.abf|cache\.abf)' .gitignore 2>/dev/null || echo "*.abf" >> .gitignore; grep -q "localSettings.json" .gitignore 2>/dev/null || echo "localSettings.json" >> .gitignore; grep -q ".pbi-context.md" .gitignore 2>/dev/null || echo ".pbi-context.md" >> .gitignore; grep -q "SecurityBindings" .gitignore 2>/dev/null || echo "SecurityBindings" >> .gitignore; echo "GITIGNORE_OK"`

Once you see GITIGNORE_OK in the bash output, proceed immediately to Step 2.

---

### Step 2 — Get diff output

Based on PBIP_FORMAT from Step 0, run the appropriate scoped diff command:

**If PBIP_FORMAT=tmdl and HAS_COMMITS=yes:**
!`git diff HEAD -- '.SemanticModel/definition/tables/' '.SemanticModel/definition/relationships.tmdl' 2>/dev/null`

**If PBIP_FORMAT=tmsl and HAS_COMMITS=yes:**
!`git diff HEAD -- '.SemanticModel/model.bim' 2>/dev/null`

**If HAS_COMMITS=no (empty repo fallback):**
!`git status --porcelain '.SemanticModel/' 2>/dev/null`

Capture the full output text for parsing in Step 3.

If the diff output is empty, skip Step 3 and go directly to Step 4 with zero changes in all categories.

---

### Step 3 — Parse diff into business-language change counts

Apply these parsing rules to the diff text captured in Step 2. Build an internal change list — do not output it yet.

**CRITICAL: Only process lines starting with `+` (not `+++`) or `-` (not `---`). Ignore context lines (lines with a space prefix) and hunk headers (`@@`). Ignore file header lines (`--- a/...` and `+++ b/...`).**

#### TMDL parsing rules (when PBIP_FORMAT=tmdl)

**Measures:**

- A measure is ADDED if a `+ measure Name =` or `+ measure 'Name With Spaces' =` line appears WITHOUT a corresponding `- measure Name =` line in the same file's diff.
- A measure is REMOVED if a `- measure Name =` or `- measure 'Name With Spaces' =` line appears WITHOUT a corresponding `+ measure Name =` line in the same file's diff.
- A measure is MODIFIED if BOTH `+ measure Name =` AND `- measure Name =` lines appear for the same name, OR if lines inside a measure block changed (formatString, `///` description lines, expression body) but the measure declaration line is unchanged.
- **Extract measure name:** text between `measure ` and ` =`; strip single quotes if present (e.g., `measure 'Revenue YTD' =` → `Revenue YTD`).
- **Extract table name:** from the file path — `tables/TableName.tmdl` → `TableName`. The file path appears in the `diff --git` header or `--- a/` / `+++ b/` lines above the hunk.

**Relationships:**

- RELATIONSHIP ADDED: a `+ relationship ` line appears.
- RELATIONSHIP REMOVED: a `- relationship ` line appears.
- Extract relationship name from `+ relationship Name` or `- relationship Name`.

**Tables:**

- TABLE ADDED: a `+ table ` line appears in a file path not previously seen in the diff.
- TABLE REMOVED: a `- table ` line appears.

**Model property changes (metadata-only):**

- If only `formatString`, `displayFolder`, or `///` description lines changed inside a measure block (the measure declaration line is NOT in the diff) — classify as a MODEL PROPERTY UPDATE for that measure name.

#### TMSL parsing rules (when PBIP_FORMAT=tmsl)

Parse the diff output from model.bim:

- Identify measure object boundaries by scanning for `"name":` fields inside a `"measures":` array context.
- Group all `+` and `-` lines between two `"name":` boundaries as belonging to one measure.
- If all lines in a measure's block are `+` lines → measure ADDED.
- If all lines in a measure's block are `-` lines → measure REMOVED.
- If a mix of `+` and `-` lines inside an existing named measure → measure MODIFIED.
- Relationship changes: `+` or `-` lines inside a `"relationships":` array block.
- Extract measure name from `"name": "MeasureName"` line in context.

#### Empty repo fallback parsing (when HAS_COMMITS=no)

The output of `git status --porcelain` uses format: `?? path` (untracked) or `A  path` (staged). Treat all listed `.SemanticModel/` files as NEW additions. Do not attempt to classify individual measures — instead report: "All model files are new (no prior commit)."

---

### Step 4 — Format output

Produce the following output in chat. Use `+` prefix for added, `~` prefix for modified, `-` prefix for removed items.

**Omit any category line that has zero changes.** If ALL categories are zero, output the no-changes message only.

```
**Model changes since last commit**

Measures: [N added, N modified, N removed — list names by table, e.g. "Sales: +[Revenue YTD], ~[Total Cost]"]
Relationships: [N added, N removed — list names if available]
Tables/Columns: [N added, N removed]
Model properties: [N metadata updates — list affected measure names]

[If no changes in any category: "No model changes since last commit."]

---
**Next step:** `/pbi:commit` to save these changes
```

**Format rules:**

- Names list format: `TableName: +[MeasureName], ~[MeasureName], -[MeasureName]`
- Group all measures for the same table together under that table name
- If a category has changes, include the count and names. Example: `Measures: 2 added, 1 modified — Sales: +[Revenue YTD], +[Total Revenue], ~[Total Cost]`
- Omit the "Next step" line if there are no changes

---

### Step 5 — Update .pbi-context.md

Use Read-then-Write to update `.pbi-context.md`:

1. Read `.pbi-context.md` using the Read tool (file may not exist — that is fine; create it if missing).
2. Update:
   - `## Last Command` section: Command = `/pbi:diff`, Timestamp = current UTC, Measure = `(git operation)`, Outcome = `Diff shown — [N] changes` (where N = total count of all changed items across all categories).
   - `## Command History` section: append a row with the same values; trim to 20 rows max.
3. Do NOT modify `## Model Context`, `## Analyst-Reported Failures`, or any other sections.
4. Write the full updated file using the Write tool.
