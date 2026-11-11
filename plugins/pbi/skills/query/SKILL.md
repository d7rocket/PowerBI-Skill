---
name: query
description: "Run a DAX query against the model open in Power BI Desktop and show the result, optionally with timings. Accepts a DAX query, a measure name, or a plain-English question about the data. Read-only. Needs live mode (/pbi:setup)."
model: sonnet
argument-hint: "[DAX query | measure name | question] [--timings]"
allowed-tools: Read, Bash
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:query

Request: $ARGUMENTS

Run DAX against the live model and show what comes back.
This command never changes the model.

## Step 1 - Live mode is required

Follow the Connect section of live mode.

- MCP tools not available: say `Running DAX needs live mode. Run /pbi:setup once, then open the project in Power BI Desktop.` and stop.
- Desktop not running, or open on another file: say which, and stop.

Do not fall back to guessing results from the files.

## Step 2 - Build the query

Read the DAX style guide (query section) first.

- **The request is a DAX query** (starts with `EVALUATE` or `DEFINE`): run it as given.
- **The request is a measure name**: `EVALUATE ROW("[Name]", [Name])`.
- **A measure name plus "by <column>"**: `SUMMARIZECOLUMNS` grouped by that column, with `ORDER BY`.
- **A question in plain English**: write the query from the model index, using real table, column and measure names. Show the query before the result.
- **Empty request**: ask `What do you want to run? (a DAX query, a measure name, or a question)`.

Rules for queries you write:

- Always `ORDER BY` when more than one row can come back.
- Never return a whole fact table. Wrap exploratory table results in `TOPN ( 50, ... )` and say so.
- To try a variation of a measure, use a query-scoped `DEFINE MEASURE`. It changes nothing in the model.
- Columns always with their table, measures always without.

## Step 3 - Run it

Use `dax_query_operations`.

- With `--timings`, or when the analyst asks how fast it is: use the tool's execution-metrics option, one warm-up run then two timed runs with the cache cleared, as described in the performance guide.
- On an error: show the exact error text, the part of the query it points at, and a corrected query. Run the corrected query once. Do not loop.

## Step 4 - Show the result

```
[the query, in a dax block, only if you wrote or changed it]

[result as a table; a single value on one line]

[N] rows[, first 50 shown]
[with timings: Total [x] ms  (formula engine [y] ms, storage engine [z] ms, [n] storage queries)]
```

- Show numbers as returned. Do not round or reformat beyond the measure's own format.
- One sentence of interpretation only when the analyst asked a question.
- If the result looks wrong for the question (blank, zero, a total repeated on every row), say what that usually means in one line.

## Step 5 - Log

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:query" "<measure or subject>" "<rows returned or error>"
```

## Never

- Use any MCP operation that writes, refreshes or deploys.
- Connect to a Fabric or Power BI service workspace.
- Present a number that was not returned by the query.
