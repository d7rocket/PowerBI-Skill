---
name: pbi:format-batch
description: "Apply SQLBI-standard DAX formatting to every measure in the model in one pass — no API dependency"
allowed-tools:
  - Read
  - Write
  - Bash
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

Save the `PBIP_DIR` value — all subsequent steps must use it.

```bash
python ".claude/skills/pbi/scripts/detect.py" files 2>/dev/null
```

```bash
python ".claude/skills/pbi/scripts/detect.py" git 2>/dev/null || (echo "GIT=no" && echo "HAS_COMMITS=no")
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
   - If `SESSION=active`: output `Context resumed — [N] tables loaded` (from Session Context), skip full load.
   - If `SESSION=new`: load all model files, build Model Context, write to `.pbi/context.md`, output summary.

2. **PBIP_MODE=paste**: run nearby check and surface location hint if found.

---

# /pbi:format-batch

<purpose>
Batch-format every DAX measure in the model to SQLBI standard. No API calls — Claude applies formatting directly, making it reliable even when the DAX Formatter API is unavailable.
</purpose>

<core_principle>
Formatting is cosmetic. Never change DAX logic, measure names, or property values (formatString, displayFolder, description). Only reformat the expression body.
</core_principle>

## Instructions

### Step 0 — PBIP-Only Guard

If PBIP_MODE=paste:
> Batch formatting requires a PBIP project. Run `/pbi:format-batch` from a directory containing a `*.SemanticModel/` folder. For a single measure, use `/pbi:format` instead.

Stop.

If PBIP_MODE=file: output:
```
Batch format — PBIP project detected ([FORMAT])
Loading measures...
```

---

### Step 1 — Read All Measure Expressions

Read every `.tmdl` file listed in the File Index using the Read tool (TMDL), or `$PBIP_DIR/model.bim` (TMSL).

For each file, extract all measure blocks:
- `file`: path to the .tmdl file
- `table`: infer from filename
- `name`: measure name (strip single quotes if present)
- `expression`: the full DAX expression text (raw, as written)
- `already_formatted`: true if expression already follows SQLBI conventions

Build the measure inventory. Output:
```
Found [N] measures across [M] tables.
```

---

### Step 2 — Apply SQLBI Formatting

For each measure, apply the following formatting rules. Mark as `changed=true` if the formatted version differs from the original.

**Keyword capitalisation — ALL DAX keywords must be UPPERCASE:**
CALCULATE FILTER ALL ALLEXCEPT ALLSELECTED VALUES RELATED RELATEDTABLE DIVIDE IF BLANK VAR RETURN SUM SUMX AVERAGE AVERAGEX COUNT COUNTROWS COUNTBLANK MIN MAX MAXX MINX HASONEVALUE SELECTEDVALUE SWITCH TRUE FALSE AND OR NOT ISBLANK IFERROR DATESYTD DATEADD SAMEPERIODLASTYEAR DATESBETWEEN TOTALYTD RANKX TOPN EARLIER UNION INTERSECT EXCEPT GENERATE CROSSJOIN NATURALINNERJOIN NATURALLEFTOUTERJOIN USERELATIONSHIP TREATAS REMOVEFILTERS KEEPFILTERS

**Structure rules:**
1. Measure name and `=` stay on the first line; expression body starts on the next line, indented 4 spaces
2. Each CALCULATE argument on its own line, indented 4 spaces from the CALCULATE call
3. Each VAR on its own line; each RETURN on its own line
4. Opening `(` stays on the same line as the function name
5. Closing `)` on its own line, aligned with the function's indent level
6. Nested functions follow the same pattern recursively
7. Spaces inside parentheses: `SUM ( Table[Column] )` — one space after `(` and before `)`

**Skip rule:** If a measure is single-line trivial and already follows all rules, mark as `already_formatted=true` and do not modify.

---

### Step 3 — Preview

Output a summary table:

```
**Batch Format Preview**

| # | Measure | Table | Status |
|---|---------|-------|--------|
| 1 | [Name]  | [Table] | Will reformat |
| 2 | [Name]  | [Table] | Already formatted — skip |

[N] measures to reformat, [M] already formatted.
```

**If PBI_CONFIRM=false:** skip the prompt below and proceed directly to Step 4.

```
Apply all formatting changes? (y/N)
```

- y / Y: proceed
- n / N / Enter: `Batch cancelled. No files modified.` Stop.

---

### Step 4 — Write Back

**TMDL path:**
For each `.tmdl` file that contains measures with `changed=true`:
1. Read the file (Read tool)
2. For each changed measure: replace only the expression text in-place.
   - Preserve the `measure Name =` declaration line
   - Replace expression lines with the formatted version (4-space indent)
   - Preserve all properties (`formatString:`, `displayFolder:`, `description:`, `/// comments`) unchanged
   - Keep tab indentation for the overall TMDL structure
3. Write the entire modified file back (Write tool) — one write per file

**TMSL path:**
1. Read `$PBIP_DIR/model.bim`
2. For each changed measure, update the `"expression"` field (use array form if expression contains line breaks)
3. Write entire model.bim back (Write tool)

Output per file:
```
Formatted: [N] measures in [file]
```

**Auto-commit:**
```bash
if git rev-parse --is-inside-work-tree 2>/dev/null; then
  git add "$PBIP_DIR/" 2>/dev/null
  git commit -m "style: batch-format [TOTAL_N] DAX measures — SQLBI standard" 2>/dev/null && echo "AUTO_COMMIT=ok" || echo "AUTO_COMMIT=fail"
fi
```

---

### Step 5 — Update Session Context

Read `.pbi/context.md`, update `## Last Command` and `## Command History` (20-row max), write back. Do NOT modify `## Analyst-Reported Failures`.

---

### Anti-Patterns
- NEVER change DAX logic — only cosmetic reformatting
- NEVER modify `formatString`, `displayFolder`, `description`, or `///` comment properties
- NEVER convert TMDL tab indentation to spaces
- NEVER call the DAX Formatter API — use Claude inline formatting only
- NEVER write one file per measure — batch all changes per table file into a single Write
