---
name: format
description: "Format DAX in SQLBI style."
model: sonnet
allowed-tools: Read, Write, Edit, Bash, Agent
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:format

<purpose>
Consistent formatting makes DAX scannable and reviewable. Unformatted DAX hides logic in walls of text — formatted DAX reveals structure at a glance.
</purpose>

<core_principle>
Use the external DAX Formatter API for consistent, community-standard formatting. Never invent formatting rules — defer to the API. If the API is unavailable, format manually following DAX Formatter conventions.
</core_principle>

> DAX Formatter API reference is in `${CLAUDE_PLUGIN_ROOT}/shared/api-notes.md` (read if needed).

## Format API Status
!`TMPCHECK=$(mktemp); curl -s -L -X POST "https://www.daxformatter.com" -d "fx=1%2B1&r=US&embed=1" --max-time 5 -o "$TMPCHECK" 2>/dev/null; CURL_EXIT=$?; if [ "$CURL_EXIT" -eq 28 ]; then echo "API_TIMEOUT"; elif python -c "import sys; d=open('$TMPCHECK','r',errors='replace').read(); sys.exit(0 if 'formatted' in d else 1)" 2>/dev/null; then echo "API_OK"; else echo "API_FAIL"; fi; rm -f "$TMPCHECK"`

## Instructions

### Step 0 - Get the measure

- `$ARGUMENTS` contains DAX: use it.
- `$ARGUMENTS` names a measure and `PBIP_MODE=file`: fetch it with `detect.py measure "<name>"` (in live tier, get it from the live model). Several matches: ask which table.
- Otherwise ask `Paste your DAX measure, or name one from the model:` and wait.
- If what comes back has no DAX in it, say `Please paste a DAX measure to format.` and stop.

### Step 1 — Measure Extraction

Extract the measure name from the pasted content:
- The measure name is everything before the first `=` sign, trimmed of whitespace
- If no `=` is found, use `[Measure]` as the placeholder name and include the note: "Note: No measure name detected — treating entire input as the expression."
- If `$ARGUMENTS` contains `--table TableName`, record the table name and include a table context note in the output: "Table context: TableName"

Store the full pasted measure text as the input for formatting.

### Step 2 — Check for Prior Failures

Check the preflight block. If the context file contains a record in the Analyst-Reported Failures table for this measure name, add a warning at the very top of the output (before everything else):
> Warning: Previous attempt at this measure used [approach from failure record] and failed. Using [alternative approach] instead.

### Step 3 — Format the Measure

Check the "Format API Status" section above:

**If API_TIMEOUT:**

Add exactly this one line at the top of the output (or after the prior-failure warning if one is present):
`_DAX Formatter API timed out (5 s) — formatted inline by Claude_`

Then format using the Claude inline SQLBI rules in Step 4.

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
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" html-parse "$TMPHTML"
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
DIVIDE ( CurrentYear - PriorYear, PriorYear )
```

### Step 5 — Output Structure

Present the output in this order:

1. (Only if prior failure warning applies): Warning line
2. (Only if API_TIMEOUT): `_DAX Formatter API timed out (5 s) — formatted inline by Claude_`
3. (Only if API_FAIL): `_DAX Formatter API unavailable — formatted inline by Claude_`
4. (Only if --table flag was passed): `Table context: TableName`
5. The formatted measure in a fenced `dax` code block
6. Next steps line: `**Next steps:** /pbi:explain · /pbi:optimise · /pbi:comment · /pbi:error`

### Step 6 - Log

If PBIP_MODE=file, log the command (one call, no file reads):

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:format" "<measure or target>" "<one-line outcome>"
```

### Step 7 - Write-back (PBIP_MODE=file only)

Only when the measure came from the project (it was named, or the pasted name matches exactly one measure in the model index) and the formatted expression differs from the stored one:

1. Ask through the normal preview: Before is the stored expression, After is the formatted one.
2. The change replaces the expression only. Keep every property and the description.
3. Apply with the write procedure of the active tier (core rules section 5, or live mode).
4. Commit message: `style: format [Measure Name] in [Table]`.

Formatting never changes what a measure returns. If a live test shows a different value after formatting, revert and report it.

### Anti-Patterns
- NEVER change DAX logic — formatting is cosmetic only
- NEVER remove comments from the original measure
- NEVER change the measure name
- NEVER skip the DAX Formatter API check — always try API first
