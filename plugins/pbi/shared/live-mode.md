# Live mode: Power BI Modeling MCP

Read this only when the Power BI Modeling MCP tools are available in the session.
In live mode the open Desktop model is the source of truth, and changes appear in Desktop immediately.

## Ground rules

- Each MCP tool takes an `operation` argument. Read the tool's own schema for the exact operation names and parameters. Never guess them.
- If a call answers that the EULA has not been accepted, stop and say: `Live mode needs Microsoft's EULA accepted. Run /pbi:setup.` Never call `accept_eula` outside `/pbi:setup`.
- The MCP may show its own write confirmation once per model. That is expected.
- Local only. Connect to Power BI Desktop only. Never connect to a Fabric workspace, never deploy.
- If any MCP call fails for a reason you cannot fix in one retry, fall back to FILE tier and say so in one line.

## Connect (once per session)

1. If `DESKTOP=not-running`, use FILE tier. Do not start Desktop.
2. Use `connection_operations` to list local Power BI Desktop instances.
3. Connect to the instance whose file name matches this project (the `PBIP_DIR` name without `.SemanticModel`).
4. If several instances could match, ask which one. If none match, use FILE tier and say `Desktop is open on a different file, working on the project files instead.`

## Read

- Use the Get and List operations for the objects you are about to change or explain.
- The preflight model index comes from disk. If the live model differs, trust the live model and tell the analyst that Desktop has unsaved changes.
- Do not read `.tmdl` files for an object you can get from the live model.

## Write

1. Get the current definition of the target object. This is the Before block and the journal `before` value.
2. Preview and confirm (core rules, section 4).
3. Apply with the matching tool (`measure_operations`, `column_operations`, `table_operations`, `relationship_operations` and so on).
4. For a change that touches more than one object, wrap it in `transaction_operations`: begin, apply all, commit. Roll back on any error.
5. Verify:
   - Get the object again and compare it with what was previewed.
   - For a measure, run `EVALUATE ROW("Result", [Measure Name])` with `dax_query_operations` and report the value.
   - If the query errors, show the exact error and ask `Revert this change? (y/N)`. On `y`, apply the Before definition again.
6. Record the change with `"tier": "live"` (core rules, section 7).
7. Say once: `Applied live in Desktop. Press Ctrl+S in Desktop to save it to the project files.`
8. Do not also edit the `.tmdl` file for the same change. Desktop writes it on save.

## Commit

A live change reaches the project files only when the analyst saves in Desktop.
`detect.py snapshot` (the same script path the core rules use) commits those saved files with the journaled business message.

- Run `snapshot` at the start of every command that writes, and in `/pbi:commit` and `/pbi:undo`.
- `SNAPSHOT_COMMITTED=<sha> <message>`: say `Committed your Desktop save: <message>`.
- `SNAPSHOT=waiting ...`: say nothing unless the preflight block shows `PENDING_LIVE_CHANGES`, then remind once: `Earlier live changes are not saved in Desktop yet (Ctrl+S).`

## Test a measure before proposing it

When live, test new or rewritten DAX before showing it as final.

```dax
DEFINE
    MEASURE 'Sales'[__candidate] = <expression>
EVALUATE
    ROW("Result", [__candidate])
```

A query-scoped `DEFINE MEASURE` changes nothing in the model.
Report the value, or fix the expression when it errors.

## After a FILE tier edit while Desktop is open

Desktop offers to refresh when project files change on disk.
Tell the analyst to accept that prompt.
Do not attempt to reload Desktop yourself.
