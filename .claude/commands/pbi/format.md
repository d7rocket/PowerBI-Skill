---
name: pbi:format
description: "Reformat DAX for readability using DAX Formatter API"
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

# /pbi:format

> DAX Formatter API reference is in `shared/api-notes.md` (read if needed).

## Format API Status
!`TMPCHECK=$(mktemp); curl -s -L -X POST "https://www.daxformatter.com" -d "fx=1%2B1&r=US&embed=1" --max-time 5 -o "$TMPCHECK" 2>/dev/null; python3 -c "import sys; d=open('$TMPCHECK','r',errors='replace').read(); print('API_OK' if 'formatted' in d else 'API_FAIL')"; rm -f "$TMPCHECK"`

## Instructions

Respond to the analyst with exactly: "Paste your DAX measure below:"

Once the analyst pastes a DAX measure, follow these steps in order.

**Empty input guard:** If the pasted content is empty, whitespace-only, or contains no DAX-like text, output: "Please paste a DAX measure to format." and stop.

### Step 0.5 — Model Context Check

Read Session Context for `## Model Context` section.

- If `## Model Context` is present and non-empty: note the table context. Use it when inferring display folder in Step 5 output. Proceed to Step 1.
- If `## Model Context` is absent or empty:
  - Ask: "Which table does this measure belong to? (optional — skip if you just want formatting)"
  - If the analyst answers: Read `.pbi-context.md` with Read tool. Add `## Model Context` section with the answer. Write back with Write tool. Use the table context in output.
  - If the analyst skips or says "skip": note "Table context not available — formatting pasted measure as-is." Proceed to Step 1 without blocking.

### Step 1 — Measure Extraction

Extract the measure name from the pasted content:
- The measure name is everything before the first `=` sign, trimmed of whitespace
- If no `=` is found, use `[Measure]` as the placeholder name and include the note: "Note: No measure name detected — treating entire input as the expression."
- If `$ARGUMENTS` contains `--table TableName`, record the table name and include a table context note in the output: "Table context: TableName"

Store the full pasted measure text as the input for formatting.

### Step 2 — Check for Prior Failures

Review the Session Context. If the context file contains a record in the Analyst-Reported Failures table for this measure name, add a warning at the very top of the output (before everything else):
> Warning: Previous attempt at this measure used [approach from failure record] and failed. Using [alternative approach] instead.

### Step 3 — Format the Measure

Check the "Format API Status" section above:

**If API_OK:**

Use the Bash tool to call the DAX Formatter API. To avoid shell injection from DAX metacharacters (`$`, backticks, etc.), write the measure to a temp file first using a single-quoted heredoc delimiter:

```bash
TMPFILE=$(mktemp)
TMPHTML=$(mktemp)
cat > "$TMPFILE" <<'ENDDAX'
PASTE_MEASURE_HERE
ENDDAX
curl -s -L -X POST "https://www.daxformatter.com" \
  --data-urlencode "fx@$TMPFILE" \
  -d "r=US&embed=1" \
  --max-time 5 -o "$TMPHTML" 2>/dev/null
python .claude/skills/pbi/scripts/detect.py html-parse "$TMPHTML"
rm -f "$TMPFILE" "$TMPHTML"
```

Replace `PASTE_MEASURE_HERE` with the actual measure text the analyst pasted (between the `<<'ENDDAX'` and `ENDDAX` lines — the single-quoted delimiter prevents shell expansion). The output of this command is the formatted DAX string. Present it in a fenced `dax` code block.

If the API call succeeds but returns empty output or garbled text, treat it as API_FAIL and use the inline fallback below.

**If API_FAIL:**

Add exactly this one line at the top of the output (or after the prior-failure warning if one is present):
`_DAX Formatter API unavailable — formatted inline by Claude_`

Then format the measure using the Claude inline SQLBI formatting rules below.

### Step 4 — Claude Inline SQLBI Formatting Rules

Use these rules when API_FAIL, or when API_OK but the API returned unusable output:

**Keyword capitalisation:**
All DAX keywords must be UPPERCASE: CALCULATE, SUMX, AVERAGEX, MAXX, MINX, FILTER, ALL, ALLEXCEPT, ALLSELECTED, VALUES, RELATED, RELATEDTABLE, DIVIDE, IF, BLANK, VAR, RETURN, SUM, SUMX, COUNT, COUNTROWS, COUNTBLANK, AVERAGE, MIN, MAX, HASONEVALUE, SELECTEDVALUE, SWITCH, TRUE, FALSE, AND, OR, NOT, ISBLANK, IFERROR, DATESYTD, DATEADD, SAMEPERIODLASTYEAR, DATESBETWEEN, TOTALYTD, RANKX, TOPN, EARLIER, EARLIER, UNION, INTERSECT, EXCEPT, GENERATE, CROSSJOIN, NATURALINNERJOIN, NATURALLEFTOUTERJOIN, etc.

**Structure rules:**
- Measure name and `=` on the first line, then expression body on the next line indented 4 spaces
- Each CALCULATE argument on its own line, indented 4 spaces from the CALCULATE call
- Each VAR and RETURN on its own line
- Opening parenthesis stays on the same line as the function name (no line break before `(`)
- Closing parenthesis on its own line, aligned with the indent level of the function name
- Nested functions follow the same pattern recursively

**Example — simple measure:**
```dax
Revenue =
SUM ( Sales[Amount] )
```

**Example — CALCULATE with filters:**
```dax
Sales YTD =
CALCULATE(
    [Revenue],
    DATESYTD ( 'Date'[Date] )
)
```

**Example — VAR/RETURN:**
```dax
YoY Growth % =
VAR CurrentYear = [Revenue]
VAR PriorYear =
    CALCULATE(
        [Revenue],
        DATEADD ( 'Date'[Date], -1, YEAR )
    )
RETURN
DIVIDE ( CurrentYear - PriorYear, PriorYear, BLANK () )
```

### Step 5 — Output Structure

Present the output in this order:

1. (Only if prior failure warning applies): Warning line
2. (Only if API_FAIL): `_DAX Formatter API unavailable — formatted inline by Claude_`
3. (Only if --table flag was passed): `Table context: TableName`
4. The formatted measure in a fenced `dax` code block
5. Next steps line: `**Next steps:** /pbi:explain · /pbi:optimise · /pbi:comment · /pbi:error`

### Step 6 — Update .pbi-context.md

After producing the output, update the `.pbi-context.md` file:

1. Use the Read tool to read the current contents of `.pbi-context.md`
2. If the file does not exist or is empty, start with the full schema below
3. Update the `## Last Command` section with:
   - Command: /pbi:format
   - Timestamp: current UTC timestamp
   - Measure: the measure name extracted in Step 1
   - Outcome: "Success — formatted via API" or "Success — formatted inline by Claude (API unavailable)"
4. Append a new row to the `## Command History` table with the same info
5. If the Command History table has more than 20 rows, remove the oldest rows to keep it at 20
6. Do NOT modify the `## Analyst-Reported Failures` section
7. Use the Write tool to write the complete updated file back to `.pbi-context.md`

**Full schema for new file creation:**
```markdown
# PBI Context

## Last Command
- Command: /pbi:format
- Timestamp: [current timestamp]
- Measure: [measure name]
- Outcome: [outcome]

## Command History
| Timestamp | Command | Measure Name | Outcome |
|-----------|---------|--------------|---------|
| [timestamp] | /pbi:format | [measure name] | [outcome] |

## Analyst-Reported Failures
| Timestamp | Command | Measure Name | What Failed | Notes |
|-----------|---------|--------------|-------------|-------|
```

### Anti-Patterns
- NEVER change DAX logic — formatting is cosmetic only
- NEVER remove comments from the original measure
- NEVER change the measure name
- NEVER skip the DAX Formatter API check — always try API first

## Post-Command Footer

After ALL steps above are complete (including session context update), output the context usage bar as the final line:

```bash
python ".claude/skills/pbi/scripts/detect.py" context-bar 2>/dev/null
```

Print the output of this command as the very last line shown to the user. Do not skip this step.