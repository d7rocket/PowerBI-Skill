---
name: load
description: "Show the current semantic model at a glance: tables, measure and column counts, relationships, format, and whether live editing is available. The model is indexed from disk on every /pbi command, so this is a view, not a required first step."
model: haiku
allowed-tools: Read, Bash
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:load

Show the model the other commands are working with.
Nothing needs to be loaded or cached: every command reads the model index fresh.

## Instructions

- `PBIP_MODE=paste`: say `No PBIP project here.` If `NEARBY_PBIP` is set, add `Found one at [path]. Start Claude Code from that folder.` Then stop.
- `PBIP_FORMAT=unknown`: say `Found [PBIP_DIR] but it has neither model.bim nor definition/tables. Open and save the project in Power BI Desktop.` and stop.

Otherwise output, from the preflight block only (no file reads):

```
**[PBIP_DIR]** ([TMDL or TMSL])  [N] tables, [M] measures, [R] relationships

| Table | Columns | Measures |
|---|---|---|
[one row per table]

Relationships
- [each relationship line; mark BIDIRECTIONAL and inactive ones]

Editing: [Live (Desktop connected) | Files (Desktop [running/not running], live mode [not set up/set up])]
Git: [repo with commits | repo, no commits yet | no repo]
```

Rules:

- For more than 25 tables, show the 25 with the most measures and add `... and [N] more tables`.
- Decide the Editing line from the tools actually available, as in the core rules. Do not attempt a connection just for this.
- If any relationship is bidirectional, add one line: `Next: /pbi:audit`.
- If `PENDING_LIVE_CHANGES` is shown, add: `[N] live change(s) are not saved in Desktop yet (Ctrl+S).`

Do not log this command.
