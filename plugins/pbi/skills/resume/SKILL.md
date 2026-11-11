---
name: resume
description: "Pick up where the last session stopped: recent /pbi commands, the last change and whether it is committed, unsaved live changes, uncommitted model edits, and saved notes such as the business question. Read-only."
model: haiku
allowed-tools: Read, Bash
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:resume

Tell the analyst where things stand, in a few lines, and suggest the next step.
This command is read-only.

## Instructions

- `PBIP_MODE=paste`: say `No PBIP project here, so there is no session to resume.` and stop.

Gather:

1. From the preflight block: the model summary line, recent commands, notes (Business Question, Visual Context, Escalation State and any other named section), Analyst-Reported Failures, `PENDING_LIVE_CHANGES`.
2. `detect.py journal-last` for the last model change.
3. If `GIT=yes`: `git status --porcelain -- "<PBIP_DIR>"` and `git log --oneline -3`.

Output:

```
**[PBIP_DIR]**  [N] tables, [M] measures

Last change: [message] ([command], [when], [live|file], [committed|not committed])
Recent: [last three commands, newest first, one line]
Uncommitted model edits: [none | N files]
Unsaved live changes: [none | N, press Ctrl+S in Desktop]
Notes: [one line per saved note, or omit the line]
Known failures: [one line per reported failure, or omit the line]

Next: [one concrete suggestion]
```

Choosing the suggestion:

- Unsaved live changes: `Save in Desktop (Ctrl+S), then /pbi:commit`.
- Uncommitted model edits: `/pbi:diff` to review, then `/pbi:commit`.
- Last command was `/pbi:audit`: `/pbi:edit` for the top finding.
- No history at all: `/pbi:load` to see the model, or describe what you need to `/pbi:menu`.
- Otherwise continue the topic of the last command.

Omit any line that has nothing to report.
Do not log this command.
