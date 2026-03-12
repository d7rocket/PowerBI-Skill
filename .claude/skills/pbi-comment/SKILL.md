---
name: pbi-comment
description: Add inline // comments to a DAX measure and generate a Description field value for Power BI. Use when an analyst asks to comment, document, or annotate a DAX measure.
disable-model-invocation: true
model: sonnet
allowed-tools: Read, Write
---

## PBIP Detection

!`PBIP_RESULT=""; if [ -d ".SemanticModel" ]; then PBISM=$(cat ".SemanticModel/definition.pbism" 2>/dev/null); if echo "$PBISM" | grep -q '"version": "1.0"'; then PBIP_RESULT="PBIP_MODE=file PBIP_FORMAT=tmsl"; else PBIP_RESULT="PBIP_MODE=file PBIP_FORMAT=tmdl"; fi; else PBIP_RESULT="PBIP_MODE=paste"; fi; echo "$PBIP_RESULT"`

## Desktop Check

!`tasklist /fi "imagename eq PBIDesktop.exe" 2>/dev/null | findstr /i "PBIDesktop.exe" >nul 2>&1 && echo "DESKTOP=open" || echo "DESKTOP=closed"`

## Session Context

!`cat .pbi-context.md 2>/dev/null | tail -80 || echo "No prior context found."`

## File Mode Branch

If the PBIP Detection output contains `PBIP_MODE=paste`:
- Proceed directly to Step 1 (paste-in mode). Do not output any file-mode header. Do not mention PBIP at all.

If the PBIP Detection output contains `PBIP_MODE=file`:
1. Output this header as the first line of your response (before Step 1 prompt):
   > File mode — PBIP project detected ([FORMAT]) | Desktop: [STATUS]
   Where [FORMAT] is "TMDL" if PBIP_FORMAT=tmdl, or "TMSL (model.bim)" if PBIP_FORMAT=tmsl.
   Where [STATUS] is "closed — will write to disk" if DESKTOP=closed, or "open — output is paste-ready" if DESKTOP=open.

2. Proceed to Step 1 (paste-in flow) to collect the measure and generate commented output. The measure name extracted in Step 2 and the output from Steps 4-5 will be used for write-back.

3. After completing Steps 2-6 (output generated), check DESKTOP status:
   - DESKTOP=open: add the note "Desktop is open — paste manually, then save." below the Description Field. Do not write any files. Skip to Step 7 (context update).
   - DESKTOP=closed: proceed to File Write-Back (see below).

### File Write-Back (DESKTOP=closed, PBIP_MODE=file)

Use the measure name extracted in Step 2 as the search key.

**If PBIP_FORMAT=tmdl:**
1. Run bash: `grep -rl "measure.*[MeasureName]" ".SemanticModel/definition/tables/" 2>/dev/null`
   - Replace [MeasureName] with the actual extracted measure name.
   - If multiple files returned: output "Measure [Name] found in multiple tables: [list]. Use --table TableName to specify which one." Deliver paste-ready output only. Stop write-back.
   - If no file returned: output "Measure [Name] not found in PBIP project — output is paste-ready for manual addition." Stop write-back.
   - If exactly one file returned: proceed.
2. Read the identified .tmdl file using the Read tool.
3. Locate the measure block:
   - Find the line matching `measure.*[MeasureName]` (the measure declaration line)
   - The line(s) immediately above starting with `///` are the existing description (may be absent)
   - The lines following the measure declaration through the blank line or next `measure`/`column`/`table` keyword are the expression and properties
4. Modify the block:
   - Replace or insert `///` description line directly above the measure declaration line (no blank line between `///` and `measure`). Use the Description Field value from Step 5 as the description text.
   - Replace the expression body with the commented DAX from Step 4. Preserve tab indentation (TMDL uses tabs — do NOT convert to spaces). Preserve formatString, displayFolder, and any other property lines that follow the expression.
5. Write the entire modified .tmdl file back using the Write tool.
6. Append the write confirmation line after the Description Field in the output:
   > Written to: [MeasureName] in [file path]

**If PBIP_FORMAT=tmsl:**
1. Read `.SemanticModel/model.bim` using the Read tool.
2. Locate the measure JSON object where `"name"` equals the extracted measure name.
   - If not found: output "Measure [Name] not found in PBIP project — output is paste-ready for manual addition." Stop write-back.
3. Update the measure object:
   - Set `"description"` to the Description Field value from Step 5 (plain string).
   - Update `"expression"` with the commented DAX from Step 4. CRITICAL: detect whether the original expression was a JSON string or a JSON array of strings. If the commented DAX has line breaks (which it will if // comments were added inline), use the array form. Preserve the exact array/string form of the original if the expression is unchanged; use array if adding comments creates new lines.
   - Preserve ALL other fields: formatString, displayFolder, annotations, etc.
4. Write the entire model.bim back using the Write tool.
5. Append the write confirmation line after the Description Field in the output:
   > Written to: [MeasureName] in .SemanticModel/model.bim

Edge cases (Claude's discretion per CONTEXT.md):
- `tasklist` produces a permission error or empty output: treat as DESKTOP=closed and proceed with write. Log note but do not block.
- .tmdl file has unusual indentation: preserve whatever indentation style is already in the file.

## Instructions

### Step 1 — Initial Response

Respond immediately with:

> Paste your DAX measure below:

Wait for the analyst to paste their DAX measure before proceeding.

### Step 2 — Measure Extraction

- Extract the measure name from the text before the first `=` sign (strip whitespace). Example: `Revenue YTD = CALCULATE(...)` → measure name is `Revenue YTD`.
- If there is no `=` in the pasted text, use `[Measure]` as the placeholder name and append a note: `_Note: No measure name found — treating full input as expression._`
- If `$ARGUMENTS` contains `--table TableName`, use that table name as additional business context when writing comments (e.g., "filters to rows in the TableName table where…").

### Step 3 — Prior Failure Check

Scan the Session Context for the extracted measure name under the `Analyst-Reported Failures` section. If a matching entry exists, prepend this flag at the very top of the output (before the measure name heading):

> ⚠️ Previous attempt at this measure was reported as failed. Review comments carefully before use.

### Step 4 — Comment Placement Rules

Add `//` inline comments to the DAX measure according to these rules:

**Where to comment:**
- Add one comment immediately **above the measure name line** (the `MeasureName =` line) describing the overall business purpose in one plain-English sentence. Example: `// Returns year-to-date revenue, filtered to the selected region`.
- Add comments **on or above CALCULATE arguments** explaining the filter logic in business terms — not DAX terms. Say `// Filter to current year only`, not `// DATESYTD applies a year-to-date time intelligence filter`.
- Add comments **above or on VAR declarations** explaining what each variable holds in business terms. Example: `// Total orders placed before the selected date`.
- Add a comment **above the RETURN statement** (when variables are used) stating plainly what is being returned. Example: `// Return the ratio of converted leads to total leads`.
- For **simple single-line measures** (e.g., `Revenue = SUM(Sales[Amount])`): add exactly one comment above the expression describing the business calculation in a full sentence. Example: `// Total sales revenue — sums the Amount column across all visible rows`.

**What not to do:**
- Do NOT add a comment on every line — only comment lines where the intent is non-obvious.
- Do NOT translate DAX syntax word-for-word into English. Explain the business logic, not the code mechanics.
- Do NOT comment on closing parentheses, indentation, or structural syntax.
- Do NOT repeat the measure name in the comment.

**Complexity scaling:**
- Infer complexity from patterns: simple measures (SUM, DIVIDE, basic CALCULATE with one filter) → fewer, shorter comments; complex measures (context transitions, EARLIER, ALLEXCEPT, nested iterators, multiple VARs) → more detailed comments on each key step.

### Step 5 — Description Field Generation Rules

Write a Description Field value (plain text, not inside a code block) that:

- Is **1–3 sentences** in plain business English.
- States: (1) what the measure calculates, (2) any key filter conditions or time intelligence behaviour, (3) any important caveats for interpretation (e.g., "Returns blank when no sales exist for the period.").
- Does **not** use DAX function names — write "year-to-date" not "DATESYTD"; write "filtered to" not "CALCULATE"; write "for each row" not "SUMX"; write "ignoring all filters" not "ALL".
- Is a **maximum of 300 characters** — Power BI's Description property is displayed in a tooltip and truncates at approximately 250–300 characters. Count characters and trim if needed.
- Uses **no markdown formatting** — no bold, no italics, no bullet points, no code formatting. Plain text only.
- Ends with a period.

### Step 6 — Output Structure

Produce the output using exactly this structure (locked decision — two labelled blocks):

```
**[Measure Name] — Commented**

### Commented DAX
```dax
// [overall purpose comment]
[MeasureName] =
// [comment if needed]
[expression with inline // comments as appropriate]
```

### Description Field
[Plain-text description, 1–3 sentences, max 300 characters, no markdown, ready to paste into Power BI measure Description property]

---
**Next steps:** `/pbi:explain` · `/pbi:format` · `/pbi:optimise` · `/pbi:error`
```

### Step 7 — Context Update

After producing the output, update `.pbi-context.md` using Read then Write:

1. **Read** `.pbi-context.md` using the Read tool to get the current contents.
2. **Write** the updated file back using the Write tool with these changes:
   - Update the `## Last Command` section: set Command to `/pbi:comment`, Timestamp to current UTC time (ISO 8601), Measure to the extracted measure name, Outcome to `Commented`.
   - Append a new row to the `## Command History` table with columns: Timestamp, Command (`/pbi:comment`), Measure Name (extracted name), Outcome (`Commented`).
   - Keep the Command History table to a maximum of 20 rows — if adding the new row would exceed 20, remove the oldest row first.
   - Do **not** modify the `## Analyst-Reported Failures` section.

### Example Output

For input `Revenue = SUM(Sales[Amount])`:

**Revenue — Commented**

### Commented DAX
```dax
// Total sales revenue across all visible rows
Revenue =
SUM(Sales[Amount])
```

### Description Field
Total sales revenue. Sums the Amount column across all rows visible in the current filter context. Returns blank when no sales exist.

---
**Next steps:** `/pbi:explain` · `/pbi:format` · `/pbi:optimise` · `/pbi:error`
