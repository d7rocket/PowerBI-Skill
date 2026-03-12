---
name: pbi-edit
description: Describe any model change in plain language and have Claude apply it directly to PBIP files. Use when an analyst wants to rename a measure, update an expression, change a format string, update a display folder, modify a description, add a new entity, or make any other model property change.
disable-model-invocation: true
model: sonnet
allowed-tools: Read, Write, Bash
---

## PBIP Detection

!`if [ -d ".SemanticModel" ]; then if [ -f ".SemanticModel/model.bim" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmsl"; elif [ -d ".SemanticModel/definition/tables" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; else echo "PBIP_MODE=file PBIP_FORMAT=tmdl"; fi; else echo "PBIP_MODE=paste"; fi`

## Desktop Check

!`tasklist /fi "imagename eq PBIDesktop.exe" 2>/dev/null | findstr /i "PBIDesktop.exe" >nul 2>&1 && echo "DESKTOP=open" || echo "DESKTOP=closed"`

Note: `tasklist` is Windows-only. On non-Windows environments (WSL, macOS), this will always return DESKTOP=closed, which is the safe default (write-to-disk mode).

## Session Context

!`cat .pbi-context.md 2>/dev/null | tail -80 || echo "No prior context found."`

## Instructions

### Step 0: PBIP-Only Guard

If PBIP Detection output contains `PBIP_MODE=paste`:
- Output: "No PBIP project found. Run /pbi:edit from a directory containing .SemanticModel/."
- Stop. Do not proceed.

If `PBIP_MODE=file`: output header:
> File mode — PBIP project detected ([FORMAT]) | Desktop: [STATUS]

Where [FORMAT] is "TMDL" if PBIP_FORMAT=tmdl, or "TMSL (model.bim)" if PBIP_FORMAT=tmsl.
Where [STATUS] is "closed" if DESKTOP=closed, or "open" if DESKTOP=open.

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
grep -rlF "[EntityName]" ".SemanticModel/definition/tables/" 2>/dev/null
```
(Replace [EntityName] with the extracted name — omit brackets if present)

- **Zero results**: Run `grep -r "measure " ".SemanticModel/definition/tables/" 2>/dev/null` to list all measure names. Compare requested name to the list using common-typo reasoning (transposed letters, dropped letters, wrong capitalisation). Output up to 3 candidates: "No measure named [RequestedName] found. Did you mean: [Candidate1] (Table1), [Candidate2] (Table1)?" Wait for clarification or stop.
- **One result**: Proceed to Step 3 with this file.
- **Multiple results**: Output: "Found [EntityName] in: [Table1], [Table2], [Table3]. Which table?" Wait for analyst to specify, then re-run grep scoped to that table's file.

If change type is `add` (new entity creation):
  - Confirm the target table file exists under `.SemanticModel/definition/tables/[TableName].tmdl`.
  - If table not found: output "Table [TableName] not found in .SemanticModel/definition/tables/. Check the table name and try again." Stop.
  - If found: proceed directly to Step 3 (the Before state is the current end of the table file).

**If PBIP_FORMAT=tmsl:**
Read `.SemanticModel/model.bim` (Read tool). Search the JSON `"measures"` arrays for the `"name"` field matching EntityName.
- Zero matches → fuzzy-match from all measure names in the measures arrays; output up to 3 candidates.
- One match → proceed to Step 3 with the located JSON object.
- Multiple matches → list the tables and ask which one.

### Step 3: Pre-Write Checklist

Run these checks before computing the After state:

**Desktop guard:**
If DESKTOP=open:
  - Output: "Power BI Desktop is open — close Desktop before editing files. Paste-in mode is not available for /pbi:edit."
  - Stop.

**unappliedChanges.json check:**
Run bash: `ls ".SemanticModel/unappliedChanges.json" 2>/dev/null && echo "UNAPPLIED=yes" || echo "UNAPPLIED=no"`
If UNAPPLIED=yes:
  - Output: "unappliedChanges.json detected — Desktop may have unsaved changes. Proceed anyway? (y/N)"
  - If analyst types y or Y: continue.
  - If analyst types n, N, presses Enter, or types anything else: Output "Write cancelled. No files modified." Stop.

**TMDL indentation check (PBIP_FORMAT=tmdl only):**
Read the target .tmdl file (Read tool). Note whether it uses tabs or spaces and the indent depth. Record this for use in Step 5 — do NOT convert the indentation style when writing back.

### Step 4: Compute Change

Read the target file (Read tool) if not already read in Step 3.

Apply the change in memory — do NOT write yet:

For **rename**: Find the measure/column declaration line matching the entity name. Replace the name in the declaration. Apply TMDL quoting rule: if the new name contains a space or special character, wrap in single quotes; otherwise unquoted.

For **update-expression**: Find the expression body lines (between the declaration line and the next property line or next entity block). Replace with new expression lines. Preserve tab indentation from the file. Preserve all other properties (formatString, displayFolder, description).

For **update-formatString / update-displayFolder / update-description**: Locate the property line in the measure block. Replace the value. If the property line does not exist (e.g., no description yet), insert it after the expression body, before the closing blank line of the block.

For **add (new measure, TMDL)**: Ask the analyst for formatString and displayFolder if not provided (or use defaults: formatString: 0, displayFolder: ""). Scaffold:
```
	measure '[EntityName]' =
			[expression]
		formatString: [value]
		displayFolder: "[value]"
```
Insert after the last existing measure block in the table file, before the trailing blank line. Preserve the file's indent style.

For **add (new measure, TMSL)**: Insert a new JSON object in the `"measures"` array: `{"name": "[EntityName]", "expression": "[expression]", "formatString": "[value]", "displayFolder": "[value]"}`.

For **TMSL expression preservation**: If the original expression was a JSON array, write back as a JSON array. If it was a string, write back as a string. Only convert string → array if the new expression contains line breaks and the original was a string.

For **remove**: Locate and delete the full entity block (from declaration line through the closing blank line). Update context noting removal. Auto-commit prefix: `fix:`.

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

For TMSL files, use ` ```json ` instead of ` ```tmdl ` in the code fence.

- y or Y: proceed to Step 6.
- n, N, Enter, or anything else: Output "Change discarded. No files modified." Stop.

### Step 6: Write Back and Auto-Commit

Write the entire file back using the Write tool (full file content — never partial write). Preserve all unchanged content exactly. Match the indentation style recorded in Step 3.

Output: "Written to: [EntityName] in [file path]"

Run the auto-commit bash block:
```bash
GIT_STATUS=$(git rev-parse --is-inside-work-tree 2>/dev/null && echo "yes" || echo "no")
if [ "$GIT_STATUS" = "yes" ]; then
  git add '.SemanticModel/' 2>/dev/null
  git commit -m "[PREFIX]: [VERB] [ENTITY_NAME] in [TABLE_NAME]" 2>/dev/null && echo "AUTO_COMMIT=ok" || echo "AUTO_COMMIT=fail"
else
  echo "AUTO_COMMIT=skip_no_repo"
fi
```
Where [PREFIX] is: `chore:` for rename/expression/metadata updates, `feat:` for additions, `fix:` for removals.
Where [VERB] is: rename, update, add, remove — matching the change type.

On AUTO_COMMIT=ok: Output "Auto-committed: [full commit message]"
On AUTO_COMMIT=skip_no_repo: Output "No git repo — run /pbi:commit to initialise one."
On AUTO_COMMIT=fail: silent (non-fatal).

### Step 7: Update Session Context

Read `.pbi-context.md` (Read tool), update these sections, then Write the full file back:
- `## Last Command`: Command = `/pbi:edit`, Timestamp = current UTC ISO 8601, Measure = [EntityName] in [TableName], Outcome = [Change type] applied
- `## Command History`: Append one row; keep last 20 rows maximum.
- Do NOT modify `## Analyst-Reported Failures`.

### Anti-Patterns (instructions for executor — do not skip)
- NEVER write only the changed block back. Always Write the full file.
- NEVER convert tabs to spaces or spaces to tabs. Read the file's style and match it.
- NEVER auto-select a table when the same entity name appears in multiple tables. Always ask.
- NEVER write on Enter or N at the confirm prompt. Default is cancel.
- NEVER show the full command list in the router — this skill is only invoked via /pbi:edit.
