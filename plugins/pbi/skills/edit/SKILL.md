---
name: edit
description: "Change one model object (measure, column, table property, relationship) from a plain-English instruction: rename, new expression, format string, display folder, description, add, remove. Edits the live Desktop model when the Power BI Modeling MCP is connected, otherwise the TMDL or TMSL files. Always previews and asks before writing."
model: sonnet
argument-hint: "[what to change]"
allowed-tools: Read, Write, Edit, Bash
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:edit

Change one model object safely.
The analyst describes the business change, this command handles the file format or the live model.

Request: $ARGUMENTS

## Step 1 - Guard and snapshot

- `PBIP_MODE=paste`: say `No PBIP project here. Run /pbi:edit from a folder that contains a *.SemanticModel folder.` and stop.
- Run `detect.py snapshot` once (live changes saved in Desktop get committed before a new change is made).

## Step 2 - Understand the change

If the request is empty, ask `What do you want to change?` and wait.

Extract:

- **Object type**: measure, column, table property, relationship.
- **Object name** and **table** when given.
- **Change**: rename, update expression, update `formatString`, `displayFolder` or description, add, remove, relationship direction or activation.

If the change is a new expression and none was given, ask `Paste the new DAX for [Name]:` and wait.
For a new measure with real logic to design, suggest `/pbi:new` instead and stop.

## Step 3 - Resolve the object

- Measures: `detect.py measure "<name>"`.
  - No match: list up to three close names from the model index and ask `Did you mean ...?`
  - Several matches: ask which table. Never pick one.
- Other objects: locate them from the model index, then read only that table file (or `relationships.tmdl`). In live tier use the MCP Get operation.
- Add: the target table must exist in the model index.

## Step 4 - Work out the exact change

Do this in memory. Nothing is written yet.

- **Rename**: change the name in the declaration. TMDL quoting: wrap the name in single quotes when it contains a space or special character.
  - Search for other uses with `detect.py search "[Old Name]"`.
  - If other objects reference the old name, list them and include those reference updates in the same change. Show them in the preview. A rename that leaves broken references is not acceptable.
- **Update expression**: replace the expression only. Keep every property.
- **Update a property**: replace the value, or insert the property after the expression when it does not exist.
- **Add a measure**: expression, `formatString`, `displayFolder` and description. Never skip the format string (currency `#,##0.00`, whole number `#,##0`, percentage `0.0%`). Follow the DAX style guide.
- **Remove**: the whole object block. First run `detect.py search "[Name]"` and warn when other objects still reference it.
- **Relationship**: change `crossFilteringBehavior` or `isActive`. When asked to make a relationship bidirectional, explain the risk in one sentence and offer the measure-based alternative first.

## Step 5 - Preview, confirm, apply, verify

Follow the write procedure of the active tier (core rules sections 4 to 7, or live mode).

Preview format:

````
Target: [object] in [table]  ([file path] or "live model")

**Before**
```tmdl
[only the affected lines]
```

**After**
```tmdl
[the same lines after the change]
```

Apply? (y/N)
````

Use `json` fences for TMSL.

Commit message:

- rename, expression, metadata: `chore: [verb] [Name] in [Table]`
- addition: `feat: add [Name] to [Table]`
- removal: `fix: remove [Name] from [Table]`

## Step 6 - Report and log

Report in three lines at most: what changed, how it was verified, and the Desktop notice from the core rules.

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:edit" "[Name] in [Table]" "[change] applied ([tier])"
```

## Never

- Write without an explicit `y`.
- Convert tabs to spaces in a TMDL file, or touch lines unrelated to the change.
- Pick a table when the name exists in several.
- Edit a `.tmdl` file for a change already applied live.
- Apply more than one unrelated change per run. Bulk rewrites are out of scope for this command.
