---
name: comment
description: "Add comments and a tooltip description to a measure."
model: sonnet
allowed-tools: Read, Write, Edit, Bash, Agent
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:comment

<purpose>
Uncommented measures are technical debt. When a measure breaks six months later, the comments are the first thing the next developer reads. Good comments explain WHY, not WHAT.
</purpose>

<core_principle>
Comment business intent, not DAX syntax. "Filter to current year" is useful. "CALCULATE with DATESYTD filter" is noise. Write comments that help someone unfamiliar with the business domain understand the measure.
</core_principle>

## Write-back (PBIP_MODE=file only)

In paste mode the output of Step 6 is the deliverable. Do not mention PBIP.

In a project, after Step 6:

1. Resolve the measure with `detect.py measure "<name>"`.
   - No match: say `Measure [Name] is not in this project. The output above is paste-ready.` and stop.
   - Several matches: ask which table.
2. The change is: the description (TMDL `///` line directly above the `measure` line, TMSL `"description"`) set to the Description Field from Step 5, and the expression replaced by the commented DAX from Step 4. For a trivial measure only the description changes.
3. Keep `formatString`, `displayFolder` and every other property untouched.
4. Apply it with the write procedure of the active tier (core rules section 5, or live mode). Preview and confirm first.
5. Commit message: `chore: update [Measure Name] comment in [Table]`.

## Instructions

### Step 1 — Initial Response

If `$ARGUMENTS` already contains a DAX expression, use it directly and skip the paste prompt.

Otherwise respond immediately with:

> Paste your DAX measure below:

Wait for the analyst to paste their DAX measure before proceeding.

**Empty input guard:** If the pasted content is empty, whitespace-only, or contains no DAX-like text, output: "Please paste a DAX measure to comment." and stop.

### Step 2 — Measure Extraction

- Extract the measure name from the text before the first `=` sign (strip whitespace). Example: `Revenue YTD = CALCULATE(...)` → measure name is `Revenue YTD`.
- If there is no `=` in the pasted text, use `[Measure]` as the placeholder name and append a note: `_Note: No measure name found — treating full input as expression._`
- If `$ARGUMENTS` contains `--table TableName`, use that table name as additional business context when writing comments (e.g., "filters to rows in the TableName table where…").

### Step 3 — Prior Failure Check

Check the preflight block for the extracted measure name under the `Analyst-Reported Failures` section. If a matching entry exists, prepend this flag at the very top of the output (before the measure name heading):

> Previous attempt at this measure was reported as failed. Review comments carefully before use.

### Step 4 — Comment Placement Rules

Add `//` inline comments to the DAX measure according to these rules:

**Where to comment:**
- Add one comment immediately **above the measure name line** (the `MeasureName =` line) describing the overall business purpose in one plain-English sentence. Example: `// Returns year-to-date revenue, filtered to the selected region`.
- Add comments **on or above CALCULATE arguments** explaining the filter logic in business terms — not DAX terms. Say `// Filter to current year only`, not `// DATESYTD applies a year-to-date time intelligence filter`.
- Add comments **above or on VAR declarations** explaining what each variable holds in business terms. Example: `// Total orders placed before the selected date`.
- Add a comment **above the RETURN statement** (when variables are used) stating plainly what is being returned. Example: `// Return the ratio of converted leads to total leads`.
- For **simple single-line self-explanatory measures** (e.g., `Revenue = SUM(Sales[Amount])`): do NOT add an inline comment — write only the description property (Step 5). Reserve inline comments for measures whose intent is non-obvious.

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

### Step 7 - Log

If PBIP_MODE=file, log the command (one call, no file reads):

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:comment" "<measure or target>" "<one-line outcome>"
```

### Anti-Patterns
- NEVER translate DAX syntax word-for-word into English — explain business logic
- NEVER remove existing comments — only add or update
- NEVER modify the DAX expression while adding comments
- NEVER exceed 300 characters in the Description Field
