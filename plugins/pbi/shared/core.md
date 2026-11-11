# /pbi core rules

These rules apply to every /pbi command.
They override anything in a command body that conflicts with them.

## 1. Output

- Lead with the result.
- No banners, no mode headers, no "Loading..." lines, no restating the request.
- Status lines are one line each, only when they tell the analyst something they need.
- End with at most one `Next:` line naming one to three relevant commands.

## 2. Modes

- `PBIP_MODE=paste`: no project here. Work from pasted DAX only, never write files, skip logging.
- `PBIP_MODE=file`: a PBIP project. Use `PBIP_DIR` and `PBIP_FORMAT` from the preflight block, never a hardcoded `.SemanticModel`.
- The model index in the preflight block was read from disk at the start of this command. It is current. Do not re-read every file to "load" the model.
- Read only the files a command needs. `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" measure "<name>" ["<table>"]` prints a measure's block, file and line range.
- If a measure is named but not pasted and the project has it, fetch it with that command instead of asking the analyst to paste it.

## 3. Edit tier

Decide once per command, silently.

- **LIVE**: the Power BI Modeling MCP tools are available in this session (tool names containing `powerbi-modeling`, for example `connection_operations`, `measure_operations`, `dax_query_operations`). If your tools are deferred, search once for `powerbi-modeling`. When they are available, read `${CLAUDE_PLUGIN_ROOT}/shared/live-mode.md` and follow it.
- **FILE**: otherwise. Edit the TMDL or TMSL files directly, following section 5.
- `LIVE_MCP_CONFIG` and `DESKTOP` in the preflight block are hints only. Tool availability decides.
- Never ask the analyst to install anything in the middle of a command. If live mode would have helped, add one final line: `Tip: /pbi:setup enables live editing and DAX testing.`
- Local only. Never connect to a Fabric or Power BI service workspace, and never deploy or publish.

## 4. Writes always preview and confirm

- Before any change to the model, show the target, a Before block and an After block (only the affected lines), then ask `Apply? (y/N)`.
- Only `y` or `Y` applies the change. Anything else cancels with `Cancelled. Nothing was changed.`
- There is no setting that disables this.
- Read-only commands never ask.
- Generated reports under `.pbi/` (docs, audit report, changelog, extract) do not change the model. Write them directly and say where they are.

## 5. FILE tier write procedure

1. If `UNAPPLIED_CHANGES=yes`, warn that Desktop may hold unsaved changes and ask `Proceed anyway? (y/N)`.
2. Read the target file. Note its indentation. TMDL uses tabs. Never convert tabs to spaces.
3. TMSL: keep the expression in its original form (string or array). Use the array form only when the expression has line breaks.
4. Preview and confirm (section 4).
5. Write the change. Preserve every unrelated line exactly.
6. Verify (section 6).
7. Record it (section 7). That one call commits the model folder locally and journals the change.
8. If it answers `commit=no-repo`, say `No git repo. /pbi:commit can create one.` If it answers `commit=commit-failed`, say the file is written but not committed.
9. Say once: `If the project is open in Power BI Desktop, accept its refresh prompt (or reopen the project) to see this change.`

## 6. Verify every write

- Re-read the changed object from its source (`detect.py measure` for files, the MCP Get operation when live) and confirm it matches what was previewed.
- When live, also execute the measure and report the value or the exact error.
- Report what was actually checked. In FILE tier say `Verified on disk. Not executed (no live connection).`
- Never say a change works when it was only written.

## 7. Record every change

After a confirmed and verified model change, write this JSON to `.pbi/change.json` and run `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" record .pbi/change.json`:

```json
{"command": "/pbi:edit", "tier": "file", "action": "update", "kind": "measure", "table": "Sales", "name": "Revenue", "before": "<full previous definition or null>", "after": "<full new definition or null>", "message": "chore: update Revenue expression in Sales"}
```

- `tier` is `file` or `live`. `action` is `create`, `update`, `delete` or `rename`.
- `message` is the commit message, in business language. Types: `feat` for additions, `fix` for removals and error fixes, `chore` for renames and metadata, `style` for formatting only.
- For `tier: file` the script stages and commits the model folder with that message, then journals the change with the commit it just made. Do not run `git add` or `git commit` yourself, and never amend.
- For `tier: live` it journals only. The commit happens after the analyst saves in Desktop (see live mode).
- `/pbi:undo` reads this journal.

## 8. DAX and modeling quality

- Simplicity first: the simplest expression that answers the business question.
- A plain `SUM` or `DIVIDE` beats a `CALCULATE` with no filter arguments.
- No `VAR`/`RETURN` for a single-use expression. No `IFERROR` or defensive blank handling unless asked. `DIVIDE` already handles division by zero.
- Every measure gets a `formatString`. Trivial measures get a description only, no inline comments.
- Never suggest bidirectional cross-filtering as a first approach. Prefer measure-based filtering.
- Before writing or reviewing DAX, read `${CLAUDE_PLUGIN_ROOT}/shared/dax-style.md`.
- Before structural changes or an audit, read `${CLAUDE_PLUGIN_ROOT}/shared/modeling.md`.
- Before performance work, read `${CLAUDE_PLUGIN_ROOT}/shared/performance.md`.

## 9. Files, encoding, shell

- Model files may contain French accents. Use Python with `encoding='utf-8'` or the Read, Write and Edit tools for model files. Never `grep`, `sed`, `awk` or shell redirects on them.
- Text search in the model: `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" search "<text>"`.
- Double-quote every path. If `python` is not found, use `python3`.

## 10. Git is local only

Allowed: `git init`, `add`, `commit`, `diff`, `log`, `status`, `revert`, `rev-parse`.
Never `pull`, `fetch`, `merge`, `rebase`, `push`, or open a pull request.

## 11. Session log

- History is recorded with `python "${CLAUDE_PLUGIN_ROOT}/scripts/detect.py" log "<command>" "<target>" "<outcome>"`. Never read or rewrite `.pbi/context.md` by hand for this.
- Named notes (business question, escalation state, visual context) are saved with `detect.py note "<Section>" "<text>"`.
- If the preflight block lists the target under Analyst-Reported Failures, say so in one line and use a different approach. Never modify that section.
