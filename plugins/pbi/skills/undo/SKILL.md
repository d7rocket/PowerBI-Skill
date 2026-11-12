---
name: undo
description: "Undo the last /pbi change, live or on disk."
model: sonnet
allowed-tools: Read, Write, Bash
disable-model-invocation: true
---

## Preflight

!`python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || python3 "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" preflight 2>&1 || echo "PREFLIGHT=failed"`

The block above is the project state and the core rules for every /pbi command. Follow the core rules. In this file `detect.py` means `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py"`. If the block shows `PREFLIGHT=failed`, read `${CLAUDE_PLUGIN_ROOT}/shared/core.md` and continue in paste mode.

---

# /pbi:undo

Undo exactly one change: the most recent one a /pbi command made.
History is preserved. This command uses `git revert`, never `git reset`.

## Step 1 - Guard and snapshot

- `PBIP_MODE=paste`: say `No PBIP project here. Nothing to undo.` and stop.
- Run `detect.py snapshot` so a Desktop save of an earlier live change is committed before anything is reversed.

## Step 2 - Find the change

Run `detect.py journal-last`.

- It prints a change record: go to Step 3.
- `JOURNAL=empty`: there is no journaled change (for example the project was last edited with version 7). Fall back to the last commit:
  - `GIT=no` or `HAS_COMMITS=no`: say `Nothing to undo.` and stop.
  - Otherwise run `git log --oneline -1` and `git show --stat HEAD`, and treat it as a file change with that commit. If the message does not look like a /pbi commit (`feat:`, `fix:`, `chore:` or `style:` followed by a model object), add `This commit was not made by a /pbi command.` to the preview.

## Step 3 - Preview and confirm

```
Undo: [message]
Made by: [command] at [timestamp]  ([tier] change)
Effect: [what the model returns to, in one line]

Undo this change? (y/N)
```

This confirmation is always required. Anything other than `y` or `Y`: say `Cancelled. Nothing was changed.` and stop.

## Step 4 - Reverse it

**Live change, MCP connected to the same model** (see live mode):

1. Apply the reverse through the MCP:
   - `create`: delete the object.
   - `update` or `rename`: restore the `before` definition.
   - `delete`: recreate the object from `before`.
2. Verify with the Get operation that the object now matches `before` (or is gone).
3. Say `Reversed live in Desktop. Press Ctrl+S in Desktop to save it to the project files.`
4. Do not run `git revert` here. The next Desktop save is committed by `detect.py snapshot`, which keeps Desktop and the files in step.

**Live change, MCP not available:**

- The change was committed (the journal has a snapshot commit for it): revert that commit as a file change, below.
- The change was never saved in Desktop: there is nothing on disk to undo. Say so, and tell the analyst to close Desktop without saving or to restore the object by hand. Do not mark it undone.

**File change:**

1. Check the working tree first: `git status --porcelain -- "<PBIP_DIR>"`. If it shows uncommitted changes, stop and say `There are uncommitted changes in the model. Commit them with /pbi:commit or discard them before undoing.`
2. Revert: `git revert --no-edit <commit>`.
3. If the revert fails, run `git revert --abort`, then say `The revert conflicts with later changes. Nothing was changed.` and stop.
4. Verify: `detect.py measure "<name>"` (or read the object) shows the `before` definition.
5. Give the Desktop notice from the core rules.

## Step 5 - Record

Only after a successful reversal:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" journal-undone
python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "/pbi:undo" "[object]" "Reverted: [message]"
```

## Never

- Undo more than one change per run.
- Use `git reset`, or any command that rewrites history.
- Revert a commit while the model folder has uncommitted changes.
- Edit `.tmdl` files to reverse a change that is live in Desktop.
