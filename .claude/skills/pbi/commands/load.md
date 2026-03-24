# /pbi load

> Detection context (PBIP_MODE, PBIP_FORMAT, PBIP_DIR, File Index, Session Context) is provided by the router.

## Instructions

### Step 0 — Check detection output

**If PBIP_MODE=paste:**

Respond with exactly this message and stop — do not read any files, do not update `.pbi-context.md`:

> No PBIP project found in this directory. All commands work with pasted DAX — paste a measure into any /pbi command to get started.

---

**If PBIP_MODE=file:** proceed to Step 1 below.

---

### Step 1 — Output the file mode header immediately

Determine the format from the detection output:
- `PBIP_FORMAT=tmdl` → format label is **TMDL**
- `PBIP_FORMAT=tmsl` → format label is **TMSL (model.bim)**

Output immediately:

```
File mode — PBIP project detected ([FORMAT]) | Loading model context...
```

---

### Step 2 — Read model files and extract structure

**For TMDL (`PBIP_FORMAT=tmdl`):**

The File Index has already listed all `.tmdl` file paths under `$PBIP_DIR/definition/tables/`.

Use the Read tool to read each `.tmdl` file from that list.

**Malformed file guard:** If a `.tmdl` file cannot be read or does not contain a `table` keyword on any line, output: `Warning: [filename] could not be parsed — skipping.` and continue with the next file. Do not fail the entire load.

From each file, extract:
- **Table name:** from the `table TableName` declaration at the top of the file
- **Measure names:** lines matching `measure 'Name'` or `measure Name` (single-word). Extract the text after `measure ` up to ` =` or end of line, stripping any single quotes.
- **Column names:** lines matching `column 'Name'` or `column Name`. Same extraction rule — strip single quotes if present.

Also check for `$PBIP_DIR/definition/relationships.tmdl` using the Read tool (if it exists). Extract relationship pairs from lines containing `fromTable:`, `fromColumn:`, `toTable:`, `toColumn:`. Build pairs: `[FromTable][FromColumn] → [ToTable][ToColumn] (many-to-one)`.

**Disambiguation rule (TMDL only):** If the same measure name appears in multiple table files, log it as `[MeasureName] (found in: Table1, Table2)` in the Measures column of the summary table. Do not fail — report all locations.

---

**For TMSL (`PBIP_FORMAT=tmsl`):**

Read `$PBIP_DIR/model.bim` with the Read tool. If model.bim is >2000 lines, use offset/limit parameters to read it in chunks of 1000 lines — read the full file across multiple reads before navigating the JSON structure.

Navigate the JSON structure:
- `model.tables[]` → for each table extract: `name`, `measures[].name`, `columns[].name`
- `model.relationships[]` → for each relationship extract: `fromTable`, `fromColumn`, `toTable`, `toColumn`

Build relationship pairs: `[FromTable][FromColumn] → [ToTable][ToColumn] (many-to-one)`.

---

### Step 3 — Format the Model Context section

Build the following markdown block:

```markdown
## Model Context
**Loaded:** [current UTC time in ISO 8601 format]
**Format:** [TMDL or TMSL (model.bim)]
**Project:** $PBIP_DIR

| Table | Measures | Columns |
|-------|----------|---------|
| [TableName] | [measure1, measure2] | [col1, col2] |
| [TableName] | (none) | [col1, col2] |

**Relationships summary:** [FromTable][FromColumn] → [ToTable][ToColumn] (many-to-one) · [additional relationships separated by ·]
```

Rules:
- If no relationships file or data is found: omit the **Relationships summary** line entirely.
- If a table has no measures: write `(none)` in the Measures column.

---

### Step 4 — Write `.pbi-context.md` (Read-then-Write, single pass)

Perform a single Read-then-Write pass to update `.pbi-context.md`:

1. **Read** `.pbi-context.md` using the Read tool.

2. **Build the updated file content** — in one pass, update three things:
   a. **`## Model Context` section:** If it already exists, replace everything from `## Model Context` through the end of that section (up to the next `##` heading or end of file) with the new Model Context block. If it does not exist, append the new Model Context block after the last existing section.
   b. **`## Last Command` section:** Update with:
      - Command: `/pbi load`
      - Timestamp: current UTC time
      - Measure: `[N tables loaded]` where N is the count of tables found
      - Outcome: `Model context loaded ([FORMAT])`
   c. **`## Command History` section:** Append a row with the same values. Keep history to 20 rows max — remove the oldest row if the count exceeds 20.

3. **CRITICAL:** Do not remove or modify `## Analyst-Reported Failures` or any other sections not listed above. Only `## Model Context`, `## Last Command`, and `## Command History` are updated.

4. **Write** the entire updated file back using the Write tool.

---

### Step 5 — Output the summary table to the analyst

After writing `.pbi-context.md`, output:

```
File mode — PBIP project detected ([FORMAT]) | Context loaded.

| Table | Measures | Columns |
|-------|----------|---------|
[same table as written to .pbi-context.md]

**Relationships summary:** [same as written, if present]

Context loaded — all DAX commands will now use model-aware analysis.
```

### Anti-Patterns
- NEVER overwrite existing Model Context without re-reading .pbi-context.md first
- NEVER output raw file contents to the analyst — only the summary table
- NEVER fail silently on unreadable files — log a warning and skip the file
- NEVER modify Analyst-Reported Failures section

## Post-Command Footer

After ALL steps above are complete (including session context update), output the context usage bar as the final line:

```bash
python ".claude/skills/pbi/scripts/detect.py" context-bar 2>/dev/null
```

Print the output of this command as the very last line shown to the user. Do not skip this step.
