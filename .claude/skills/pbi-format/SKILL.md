---
name: pbi-format
description: Format a DAX measure to SQLBI style (consistent indentation, keyword capitalisation, line breaks). Use when an analyst asks to format, clean up, or prettify a DAX measure.
disable-model-invocation: true
model: sonnet
allowed-tools: Read, Write, Bash(curl *)
---

## Session Context
!`cat .pbi-context.md 2>/dev/null | tail -80 || echo "No prior context found."`

## Format API Status
!`curl -s -L -X POST "https://www.daxformatter.com" -d "fx=1%2B1&r=US&embed=1" --max-time 5 2>/dev/null | grep -q 'formatted' && echo "API_OK" || echo "API_FAIL"`

## Instructions

Respond to the analyst with exactly: "Paste your DAX measure below:"

Once the analyst pastes a DAX measure, follow these steps in order:

### Step 1 — Measure Extraction

Extract the measure name from the pasted content:
- The measure name is everything before the first `=` sign, trimmed of whitespace
- If no `=` is found, use `[Measure]` as the placeholder name and include the note: "Note: No measure name detected — treating entire input as the expression."
- If `$ARGUMENTS` contains `--table TableName`, record the table name and include a table context note in the output: "Table context: TableName"

Store the full pasted measure text as the input for formatting.

### Step 2 — Check for Prior Failures

Review the Session Context section at the top of this prompt. If the context file contains a record in the Analyst-Reported Failures table for this measure name, add a warning at the very top of the output (before everything else):
> Warning: Previous attempt at this measure used [approach from failure record] and failed. Using [alternative approach] instead.

### Step 3 — Format the Measure

Check the "Format API Status" section above:

**If API_OK:**

Use the Bash tool to call the DAX Formatter API and retrieve the formatted output:

```bash
curl -s -L -X POST "https://www.daxformatter.com" \
  --data-urlencode "fx=PASTE_MEASURE_HERE" \
  -d "r=US&embed=1" \
  --max-time 5 2>/dev/null | \
  grep -o '<div class="formatted"[^>]*>.*</div>' | \
  sed 's/<div class="formatted"[^>]*>//g' | \
  sed 's/<\/div>.*//g' | \
  sed 's/<br>/\n/g' | \
  sed 's/<span[^>]*>//g' | \
  sed 's/<\/span>//g' | \
  sed 's/&nbsp;/ /g'
```

Replace `PASTE_MEASURE_HERE` with the actual measure text the analyst pasted. The output of this command is the formatted DAX string. Present it in a fenced `dax` code block.

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
