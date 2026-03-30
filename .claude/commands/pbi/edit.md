---
name: pbi:edit
description: "Modify measures, columns, and tables using plain-English instructions with before/after preview and auto-commit"
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

### Auto-Resume

After detection, apply the following before executing the command:

1. **PBIP_MODE=file, context exists** — Session Context output contains `## Model Context` with a table:
   - Count the table rows in the Model Context table.
   - Output on a single line: `Context resumed — [N] tables loaded`
   - Skip any "Model Context Check" (Step 0.5) below — context is already available.

2. **PBIP_MODE=file, no context yet** — Session Context has no `## Model Context` or `.pbi-context.md` does not exist:
   - Output: `No model context — auto-loading project...`
   - Read all files from File Index, extract table/measure/column/relationship structure, build the Model Context markdown block, write it to `.pbi-context.md`.
   - Output the summary table and: `Auto-loaded [N] tables. Context ready.`

3. **PBIP_MODE=paste — nearby folder check**:
   Run: `python ".claude/skills/pbi/scripts/detect.py" nearby 2>/dev/null`
   - If NEARBY_PBIP is found: output: `No PBIP project here, but found one at [NEARBY_PBIP]. Run cd "[NEARBY_PBIP]" first.`
   - If NEARBY_PBIP is empty: skip silently. Paste-in commands still work.

After auto-resume completes, proceed to the command instructions below.

---

# /pbi:edit


## Instructions

### Step 0: PBIP-Only Guard

If PBIP_MODE=paste:
- Output: "No PBIP project found. Run /pbi:edit from a directory containing a *.SemanticModel/ folder."
- Stop.

If PBIP_MODE=file: output header:
> File mode — PBIP project detected ([FORMAT])

Where [FORMAT] is "TMDL" if PBIP_FORMAT=tmdl, or "TMSL (model.bim)" if PBIP_FORMAT=tmsl.

Then proceed to Step 1.

### Step 1: Collect Change Description

Output: "Describe the change you want to make:"

Wait for analyst input. Parse the description to extract:
- **Entity type**: measure / column / table / relationship / table property
- **Entity name**: the specific name in brackets (e.g., [Revenue]) or plain name
- **Table name**: if given in description (e.g., "in Sales table")
- **Change type**: rename / update-expression / update-formatString / update-displayFolder / update-description / add / remove

If change type is `update-expression`:
  - Do NOT generate the Before/After preview yet.
  - First ask: "Paste the new DAX expression for [EntityName]:"
  - Wait for the expression paste, then proceed to Step 2.

### Step 2: Entity Resolution

**If PBIP_FORMAT=tmdl:**
Run bash:
```bash
python ".claude/skills/pbi/scripts/detect.py" search "[EntityName]" "$PBIP_DIR" 2>/dev/null
```
(Replace [EntityName] with the extracted name — omit brackets if present)

- **Zero results**: Run bash:
  ```bash
  python ".claude/skills/pbi/scripts/detect.py" search "measure " "$PBIP_DIR" 2>/dev/null
  ```
  Read each returned file to list measure names. Compare requested name to the list using common-typo reasoning. Output up to 3 candidates: "No measure named [RequestedName] found. Did you mean: [Candidate1] (Table1), [Candidate2] (Table1)?" Wait for clarification or stop.
- **One result**: Proceed to Step 3 with this file.
- **Multiple results**: Output: "Found [EntityName] in: [Table1], [Table2], [Table3]. Which table?" Wait for analyst to specify, then re-run the search scoped to that table's file.

If change type is `add` (new entity creation):
  - Confirm the target table file exists under `$PBIP_DIR/definition/tables/[TableName].tmdl`.
  - If table not found: output "Table [TableName] not found in $PBIP_DIR/definition/tables/. Check the table name and try again." Stop.
  - If found: proceed directly to Step 3.

**If PBIP_FORMAT=tmsl:**
Read `$PBIP_DIR/model.bim` using the Read tool. If model.bim is >2000 lines, use offset/limit parameters to read in chunks of 1000 lines — read the full file across multiple reads before searching. Search the JSON `"measures"` arrays for `"name"` matching EntityName.
- Zero matches → fuzzy-match; output up to 3 candidates.
- One match → proceed to Step 3.
- Multiple matches → list tables and ask.

### Step 3: Pre-Write Checklist

**unappliedChanges.json check:**
Run bash: `ls "$PBIP_DIR/unappliedChanges.json" 2>/dev/null && echo "UNAPPLIED=yes" || echo "UNAPPLIED=no"`
If UNAPPLIED=yes:
  - Output: "unappliedChanges.json detected — Desktop may have unsaved changes. Proceed anyway? (y/N)"
  - If analyst types y or Y: continue.
  - Otherwise: Output "Write cancelled. No files modified." Stop.

**TMDL indentation check (PBIP_FORMAT=tmdl only):**
Read the target .tmdl file (Read tool). Note whether it uses tabs or spaces and the indent depth. Record this for use in Step 5 — do NOT convert the indentation style when writing back.

### Step 4: Compute Change

Read the target file (Read tool) if not already read in Step 3.

Apply the change in memory — do NOT write yet:

For **rename**: Find the measure/column declaration line matching the entity name. Replace the name in the declaration. Apply TMDL quoting rule: if the new name contains a space or special character, wrap in single quotes; otherwise unquoted.

For **update-expression**: Find the expression body lines. Replace with new expression lines. Preserve tab indentation from the file. Preserve all other properties (formatString, displayFolder, description).

For **update-formatString / update-displayFolder / update-description**: Locate the property line in the measure block. Replace the value. If the property line does not exist, insert it after the expression body.

For **add (new measure, TMDL)**: Ask the analyst for formatString and displayFolder if not provided (or use defaults: formatString: 0, displayFolder: ""). Scaffold:
```
	measure '[EntityName]' =
			[expression]
		formatString: [value]
		displayFolder: "[value]"
```
Insert after the last existing measure block in the table file. Preserve the file's indent style.

For **add (new measure, TMSL)**: Insert a new JSON object in the `"measures"` array.

For **TMSL expression preservation**: If the original expression was a JSON array, write back as a JSON array. If it was a string, write back as a string. Only convert string → array if the new expression contains line breaks.

For **remove**: Locate and delete the full entity block. Auto-commit prefix: `fix:`.

### Step 5: Before/After Preview and Confirmation

Output the preview using this exact locked format:

```
File: [target file path]

**Before**
```tmdl
[original block — just the affected lines/section, not the entire file]
```

**After**
```tmdl
[modified block]
```

Write this change? (y/N)
```

For TMSL files, use ` ```json ` instead of ` ```tmdl `.

- y or Y: proceed to Step 6.
- n, N, Enter, or anything else: Output "Change discarded. No files modified." Stop.

### Step 6: Write Back and Auto-Commit

Write the entire file back using the Write tool (full file content — never partial write). Preserve all unchanged content exactly. Match the indentation style recorded in Step 3.

Output: "Written to: [EntityName] in [file path]"

Run the auto-commit bash block:
```bash
GIT_STATUS=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "yes" || echo "no")
if [ "$GIT_STATUS" = "yes" ]; then
  git add "$PBIP_DIR/" 2>/dev/null
  git commit -m "[PREFIX]: [VERB] [ENTITY_NAME] in [TABLE_NAME]" 2>/dev/null && echo "AUTO_COMMIT=ok" || echo "AUTO_COMMIT=fail"
else
  echo "AUTO_COMMIT=skip_no_repo"
fi
```
Where [PREFIX] is: `chore:` for rename/expression/metadata updates, `feat:` for additions, `fix:` for removals.

On AUTO_COMMIT=ok: Output "Auto-committed: [full commit message]"
On AUTO_COMMIT=skip_no_repo: Output "No git repo — run /pbi:commit to initialise one."
On AUTO_COMMIT=fail: silent (non-fatal).

### Step 7: Update Session Context

Read `.pbi-context.md` (Read tool), update these sections, then Write the full file back:
- `## Last Command`: Write these four lines exactly, replacing placeholders:
  - Command: /pbi:edit
  - Timestamp: [current UTC ISO 8601]
  - Measure: [EntityName] in [TableName]
  - Outcome: [Change type] applied
- `## Command History`: Append one row in this format: `| [timestamp] | /pbi:edit | [EntityName] in [TableName] | [Change type] applied |`; keep last 20 rows maximum.
- Do NOT modify `## Analyst-Reported Failures`.

### Anti-Patterns
- NEVER write only the changed block back. Always Write the full file.
- NEVER convert tabs to spaces or spaces to tabs. Read the file's style and match it.
- NEVER auto-select a table when the same entity name appears in multiple tables. Always ask.
- NEVER write on Enter or N at the confirm prompt. Default is cancel.

## Post-Command Footer

After ALL steps above are complete (including session context update), output the context usage bar as the final line:

```bash
python ".claude/skills/pbi/scripts/detect.py" context-bar 2>/dev/null
```

Print the output of this command as the very last line shown to the user. Do not skip this step.