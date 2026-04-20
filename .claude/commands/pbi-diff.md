---
name: pbi:diff
description: "Human-readable summary of uncommitted model changes grouped by entity type"
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

# /pbi-diff


## Instructions

### Step 0 — Check PBIP and git state

**If PBIP_MODE=paste:** output exactly this message and stop:

> No PBIP project found. Run /pbi-diff from a directory containing a *.SemanticModel/ folder.

**If GIT=no:** output exactly this message and stop:

> No git repo found. Run /pbi-commit to initialise one.

**If GIT=yes and HAS_COMMITS=no:** proceed to Step 1 with the note that this is an empty repo — treat all $PBIP_DIR/ files as new additions. In Step 2, use `git status --porcelain "$PBIP_DIR/" 2>/dev/null` as the diff source instead of `git diff HEAD`.

**Otherwise (GIT=yes and HAS_COMMITS=yes):** proceed to Step 1.

---

### Step 1 — Gitignore hygiene check (silent auto-fix)

Run this bash block to ensure all noise file entries are present in `.gitignore`. Do NOT output any message to the analyst. Silently continue to Step 2.

```bash
python .claude/skills/pbi/scripts/detect.py gitignore-check
```

---

### Step 2 — Get diff output

Based on PBIP_FORMAT, run the appropriate scoped diff command:

**If PBIP_FORMAT=tmdl and HAS_COMMITS=yes:**
```bash
git diff HEAD -- "$PBIP_DIR/definition/tables/" "$PBIP_DIR/definition/relationships.tmdl" 2>/dev/null
```

**If PBIP_FORMAT=tmsl and HAS_COMMITS=yes:**
```bash
git diff HEAD -- "$PBIP_DIR/model.bim" 2>/dev/null
```

**If HAS_COMMITS=no (empty repo fallback):**
```bash
git status --porcelain "$PBIP_DIR/" 2>/dev/null
```

Capture the full output text for parsing in Step 3.

If the diff output is empty, skip Step 3 and go directly to Step 4 with zero changes in all categories.

---

### Step 3 — Parse diff into business-language change counts

Apply these parsing rules to the diff text captured in Step 2. Build an internal change list — do not output it yet.

**CRITICAL: Only process lines starting with `+` (not `+++`) or `-` (not `---`). Ignore context lines (lines with a space prefix) and hunk headers (`@@`). Ignore file header lines (`--- a/...` and `+++ b/...`).**

#### TMDL parsing rules (when PBIP_FORMAT=tmdl)

**Measures:**
- A measure is ADDED if a `+ measure Name =` line appears WITHOUT a corresponding `- measure Name =` line in the same file's diff.
- A measure is REMOVED if a `- measure Name =` line appears WITHOUT a corresponding `+ measure Name =` line.
- A measure is MODIFIED if BOTH `+` and `-` lines appear for the same measure name, OR if property lines (formatString, displayFolder, description `///`) or expression body lines changed within a measure block while the `measure Name =` declaration line itself is unchanged.
- **Extract measure name:** text between `measure ` and ` =`; strip single quotes.
- **Extract table name:** from the file path — `tables/TableName.tmdl` → `TableName`.

**Relationships:**
- RELATIONSHIP ADDED: a `+ relationship ` line appears.
- RELATIONSHIP REMOVED: a `- relationship ` line appears.

**Tables:**
- TABLE ADDED: a `+ table ` line appears in a file path not previously seen in the diff.
- TABLE REMOVED: a `- table ` line appears.

**Model property changes (metadata-only):**
- If only `formatString`, `displayFolder`, or `///` description lines changed inside a measure block — classify as a MODEL PROPERTY UPDATE.

#### TMSL parsing rules (when PBIP_FORMAT=tmsl)

Parse the diff output from model.bim:
- Identify measure object boundaries by scanning for `"name":` fields inside a `"measures":` array context.
- Group all `+` and `-` lines between two `"name":` boundaries as belonging to one measure.
- All `+` lines → measure ADDED. All `-` lines → measure REMOVED. Mix → measure MODIFIED.

#### Empty repo fallback parsing (when HAS_COMMITS=no)

Treat all listed `$PBIP_DIR/` files as NEW additions. Report: "All model files are new (no prior commit)."

---

### Step 4 — Format output

**Omit any category line that has zero changes.** If ALL categories are zero, output the no-changes message only.

```
**Model changes since last commit**

Measures: [N added, N modified, N removed — list names by table]
Relationships: [N added, N removed — list names if available]
Tables/Columns: [N added, N removed]
Model properties: [N metadata updates — list affected measure names]

[If no changes: "No model changes since last commit."]

---
**Next step:** `/pbi-commit` to save these changes
```

**Format rules:**
- Names list format: `TableName: +[MeasureName], ~[MeasureName], -[MeasureName]`
- Group all measures for the same table together under that table name
- Omit the "Next step" line if there are no changes

---

### Step 5 — Update .pbi/context.md

Use Read-then-Write to update `.pbi/context.md`:

1. Update `## Last Command` with these four lines in this exact order:
   - Command: /pbi-diff
   - Timestamp: [current UTC ISO 8601]
   - Measure: [comma-separated list of changed measure names from Step 3 parse, or "(no measures changed)" if diff showed no measure changes]
   - Outcome: Diff shown — [N] changes
2. Append row to `## Command History`; trim to 20 rows max.
3. Do NOT modify `## Model Context`, `## Analyst-Reported Failures`, or any other sections.

### Anti-Patterns
- NEVER modify any files — diff is strictly read-only
- NEVER include noise files (*.abf, localSettings.json, .pbi/context.md) in the diff output
- NEVER run git pull, git push, or any remote operation
