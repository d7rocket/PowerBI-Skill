---
name: pbi
description: Power BI DAX co-pilot. Explains, formats, optimises, comments, and scaffolds DAX measures. Audits PBIP semantic models for hidden columns, bidirectional filters, and naming issues with auto-fix. Tracks model changes with local git versioning. Use when user mentions "DAX", "Power BI", "PBIP", "semantic model", asks to "explain this measure", "format DAX", "optimise DAX", "audit my model", "create a measure", "comment DAX", "fix DAX error", "edit measure", "diff changes", "undo last change", "extract project summary", or works with .tmdl/.bim files. Supports both TMDL and TMSL formats.
license: MIT
disable-model-invocation: true
model: sonnet
allowed-tools: Read, Write, Bash, Agent
argument-hint: "[explain|format|optimise|comment|error|new|load|audit|diff|commit|edit|undo|comment-batch|changelog|deep|extract|docs|help|version]"
metadata:
  author: d7rocket
  version: 4.3.0
  category: data-analytics
  tags: [power-bi, dax, pbip, semantic-model]
---

## Detection Blocks (run once, shared by all subcommands)

**Folder naming:** Real PBIP projects use `<ProjectName>.SemanticModel` and `<ReportName>.Report` (e.g., `Sales.SemanticModel`, `Sales.Report`). Test fixtures may use `.SemanticModel`. Detection globs for both patterns.

### PBIP Detection
!`python ".claude/skills/pbi/scripts/detect.py" pbip 2>/dev/null || echo "PBIP_MODE=paste"`

Save the `PBIP_DIR` value from the output — all subsequent commands must use it instead of a hardcoded `.SemanticModel`.

### File Index
!`python ".claude/skills/pbi/scripts/detect.py" files 2>/dev/null`

### PBIR Detection
!`python ".claude/skills/pbi/scripts/detect.py" pbir 2>/dev/null || echo "PBIR=no"`

### Git State
!`python ".claude/skills/pbi/scripts/detect.py" git 2>/dev/null || (echo "GIT=no" && echo "HAS_COMMITS=no")`

### Session Context
!`python ".claude/skills/pbi/scripts/detect.py" context 2>/dev/null || echo "No prior context found."`

### Auto-Resume (every invocation)

After detection blocks run, apply the following before routing:

1. **PBIP_MODE=file, context exists** — Session Context output contains `## Model Context` with a table:
   - Count the table rows in the Model Context table.
   - Output on a single line: `Context resumed — [N] tables loaded`
   - All subcommands can skip their "Model Context Check" (Step 0.5) — context is already available.

2. **PBIP_MODE=file, no context yet** — Session Context has no `## Model Context` or `.pbi-context.md` does not exist:
   - Output: `No model context — auto-loading project...`
   - Execute `/pbi load` Steps 2–4 inline: read all files from File Index, extract table/measure/column/relationship structure, build the Model Context markdown block, write it to `.pbi-context.md`.
   - Output the summary table and: `Auto-loaded [N] tables. Context ready.`

3. **PBIP_MODE=paste — nearby folder check**: Check parent directories for a PBIP project:
   Run: `python ".claude/skills/pbi/scripts/detect.py" nearby 2>/dev/null`
   - If NEARBY_PBIP is found (non-empty value): output: `No PBIP project here, but found one at [NEARBY_PBIP]. Run cd "[NEARBY_PBIP]" first.`
   - If NEARBY_PBIP is empty: skip silently. Paste-in commands still work.

After auto-resume completes, proceed to Routing.

## Routing

Parse `$ARGUMENTS` first word/keyword to determine the subcommand. Match against these patterns:

| Keyword(s) | Subcommand | Execution |
|------------|-----------|-----------|
| explain, "what does", understand, "how does" | commands/explain.md | sonnet direct |
| format, "clean up", prettify, style | commands/format.md | sonnet direct |
| optimise, optimize, performance, "speed up", slow | commands/optimise.md | sonnet direct |
| comment (not "comment-batch"/"comment all"), annotate, document, describe | commands/comment.md | sonnet direct |
| error, fix, diagnose, broken, failing | commands/error.md | sonnet direct |
| new, create, "add measure", scaffold | commands/new.md | sonnet direct |
| edit, rename, update, change, modify | commands/edit.md | sonnet direct |
| "comment-batch", "comment all", "batch comment", "document all" | commands/comment-batch.md | sonnet direct |
| audit, "health check", "review model", "find issues" | commands/audit.md | sonnet direct (spawns haiku agents for 5+ table models) |
| load, context, "model context", "load project" | commands/load.md | haiku Agent |
| diff, "what changed", changes, "show changes" | commands/diff.md | haiku Agent |
| commit, save, snapshot, git | commands/commit.md | haiku Agent |
| undo, revert, "go back" | commands/undo.md | haiku Agent |
| changelog, "release notes", history, "what shipped" | commands/changelog.md | haiku Agent |
| deep | commands/deep.md | sonnet direct |
| extract, "project summary", "model summary", "export model" | commands/extract.md | sonnet direct |
| docs, documentation, "generate docs", "document project", "project docs" | commands/docs.md | sonnet direct |
| help, commands, "what can you do", "list commands" | commands/help.md | sonnet direct |
| version, "version history", "what version" | commands/version.md | sonnet direct |
| (no keyword match — free-text) | Solve-first handler (inline below) | sonnet direct |

If intent is ambiguous between two commands: pick the most specific match and note it — "Routing to /pbi edit (you can also use /pbi comment if you only need to add comments)."

### Execution

**For sonnet subcommands** (explain, format, optimise, comment, error, new, edit, comment-batch, audit, deep, extract, docs, help):
1. Determine the skill directory: find where this SKILL.md file is located (typically `.claude/skills/pbi/` relative to the project root). Use the Glob tool to find the skill directory if needed: `**/.claude/skills/pbi/commands/[cmd].md`.
2. Use the Read tool to load the command file at that path (e.g., `.claude/skills/pbi/commands/explain.md`).
3. Execute the loaded instructions directly in the current context. Pass through the detection block outputs above and any remaining `$ARGUMENTS` after the subcommand keyword. **All file operations (Read, Write, Bash) must target the user's CWD (their project folder), NOT the skill directory.**

**For haiku subcommands** (load, diff, commit, undo, changelog):
1. Determine the skill directory as above and use the Read tool to load the command file (e.g., `.claude/skills/pbi/commands/load.md`).
2. Spawn a **haiku Agent** with:
   - The full command file content as instructions
   - The detection block outputs above (PBIP_MODE, PBIP_FORMAT, File Index, Git State, Session Context)
   - Any remaining `$ARGUMENTS` after the subcommand keyword
   - Description: "pbi [cmd] — [one-line summary]"

### Empty $ARGUMENTS — Category Menu

If `$ARGUMENTS` is empty or absent, output the following category menu exactly:

---
What would you like to do?

**A — Work on a DAX measure**
  explain · format · optimise · comment · new

**B — Audit the model**
  audit (includes hidden column hygiene, auto-fix, and PBIR visual audit)

**C — See, commit, or undo changes**
  diff · commit · undo · changelog

**D — Edit a model file**
  edit · comment-batch

**E — Deep mode**
  Full structured workflow with upfront context gathering

**F — Extract project summary**
  extract (overview · standard · deep-dive)

**G — Generate project documentation**
  docs (polished, stakeholder-ready model documentation)

**? — Help**
  List all commands

Type A, B, C, D, E, F, G, or ? — or describe what you need and I'll route you directly.

---

On analyst response:

- "A": Ask — "Which DAX command? **explain** · **format** · **optimise** · **comment** · **new**" — then route.
- "B": Route directly to audit. Output "Routing to /pbi audit — running a full model health check." then proceed.
- "C": Ask — "Which command? **diff** — see what changed · **commit** — save a snapshot · **undo** — revert the last commit · **changelog** — generate release notes" — then route.
- "D": Ask — "Which command? **edit** — change a specific entity · **comment-batch** — comment all measures at once" — then route.
- "E": Route to `/pbi deep`.
- "F": Route to `/pbi extract`.
- "G": Route to `/pbi docs`. Output "Routing to /pbi docs — generating project documentation." then proceed.
- "?": Route to `/pbi help`.
- Free-text response: Apply the keyword matching from the Routing table above. If no keyword matches, route to **Solve-First Default** handler and treat the text as the request.
- Any response that does not match A/B/C/D/E/F/G/? or a recognisable keyword: Output "I didn't catch that — type A, B, C, D, E, F, G, or ? — or describe what you need."

## Solve-First Default

When no keyword matches (catch-all route), this handler runs.

### Behavior

1. **Attempt immediately.** Read the user's request as a DAX/Power BI question. Generate a solution right away — no questions, no mode announcement, no preamble. Just solve.
   - Use detection context (PBIP_MODE, File Index, Session Context) to ground the answer in the user's actual model when available.
   - If Session Context contains ## Model Context, reference actual table/column names.
   - If Session Context contains ## Escalation State with previously gathered context, use it.

2. **Deliver the answer.** Output the DAX or guidance. Let the user react.

3. **Escalation trigger.** Track failure signals in-session (counter resets on `/clear`). Escalation fires ONLY after the user signals failure **twice**:
   - Negative signals: "that's wrong", "not what I meant", "still broken", "doesn't work", "incorrect", "nope", "try again", "that's not right"
   - Normal follow-ups ("can you also...", "what about...", "and then...") are NOT failure signals — handle them as new requests.
   - Refinement requests ("make it a percentage", "add a filter for...") are NOT failure signals — just refine the answer.
   - **Counter is in-session only.** Do NOT write it to disk — it resets on `/clear`.

3.5. **On FIRST failure signal — retry silently.** Increment the counter to 1. Do NOT ask any questions. Attempt a different approach or interpretation immediately — no announcement, just a revised solution. Wait for the user's reaction.

4. **On SECOND failure signal — diagnose the gap.** Increment the counter to 2 and escalate. Read the user's failure description to determine which context is missing:
   - "Calculating the wrong thing" / "not what I asked for" → missing **business question** clarity
   - "Wrong columns" / "table doesn't exist" / "relationship issue" → missing **data model state**
   - "We already have that" / "duplicates an existing measure" → missing **existing measures** knowledge
   - "Filter is wrong" / "wrong numbers in visual" → missing **visual/model context**

5. **Ask ONE targeted question.** Based on the diagnosed gap, ask exactly one question:
   - Business question gap: "What business question should this measure answer? (e.g., 'monthly revenue growth compared to prior year')"
   - Data model gap: "Can you describe the relevant tables and how they relate? (e.g., 'Sales fact table linked to Date and Product dimensions')"
   - Existing measures gap: "What existing measures are in play? (paste names or describe what's already built)"
   - Visual/model context gap: "Where will this measure be used — which visual, and what slicers or filters are active?"

   Prefix with a brief acknowledgment: "Let me get more context." Then the question. Nothing else.

6. **Write escalation state.** After asking the question, update `.pbi-context.md`:
   - Read the file with Read tool.
   - Add or update `## Escalation State` section with the question asked and "awaiting: [gap type]".
   - Write back with Write tool.

7. **On user's answer — retry automatically.** When the user answers the escalation question:
   - Incorporate the new context into the solution.
   - Retry immediately — do NOT ask "shall I try again?" or prompt for re-submission.
   - Update `## Escalation State` in `.pbi-context.md`: replace "awaiting" with the gathered answer summary.

8. **Re-escalation.** If the user signals failure AGAIN after an escalation retry:
   - Diagnose the NEXT unresolved gap (skip gaps already answered in Escalation State).
   - Ask one more targeted question about the remaining gap.
   - Same flow: acknowledge, ask, write state, retry on answer.

9. **Session context update.** After each solve attempt (initial or retry), update `.pbi-context.md`:
   - `## Last Command`: Command = `catch-all`, Request summary, Outcome
   - `## Command History`: append row, keep 20 max
   - Do NOT modify `## Analyst-Reported Failures`

## Post-Command Epilogue (runs after every subcommand)

After any subcommand completes (including the Solve-First Default handler):

1. **Auto-stage** (if PBIP_MODE=file AND GIT=yes AND the command wrote files to `$PBIP_DIR/`):
   ```bash
   git add "$PBIP_DIR/" 2>/dev/null
   ```
   Output: `Staged locally | Context updated`

2. **Skip conditions**: If PBIP_MODE=paste, or GIT=no, or the command did not write any files (e.g., explain in paste mode, help, diff), skip the auto-stage step (but still run context tracking below).
3. **Auto-committing commands**: Commands that auto-commit (comment, new, edit, error, audit, comment-batch) already run `git add` + `git commit`. The epilogue's `git add` is a harmless no-op in those cases — skip the "Staged locally" output if the command already output an "Auto-committed" message.

4. **Context tracking** — After every command completes, estimate context window usage and output a status line:
   - Count the total rows in `## Command History` in `.pbi-context.md` (N).
   - Estimate = min(5 + (N × 5), 100).
   - Build a 10-block progress bar: filled blocks (█) for used portion, empty blocks (░) for remaining.
   - Output: `Context: [██████░░░░] ~[estimate]%`
   - If estimate >= 70: append ` — consider /clear to free up context`
   - If estimate >= 90: append ` — /clear recommended before continuing`
   - This line appears after all other command output, as the very last line.

## Shared Rules

- **PYTHON-FIRST FILE OPERATIONS (CRITICAL):** All file read/write and text search operations MUST use Python with `encoding='utf-8'` to correctly handle accented characters (French: é, è, ê, ç, à, ù, etc.). Do NOT use `grep`, `cat`, `sed`, `awk`, or shell redirects for reading/writing model files. For measure name search, use `python ".claude/skills/pbi/scripts/detect.py" search "MeasureName" "$PBIP_DIR"` instead of `grep -rlF`. Shell/bash is allowed ONLY for: git CLI commands and Python script invocation.
- **PBIP folder naming:** Always use the `PBIP_DIR` value from detection (e.g., `Sales.SemanticModel`) — never hardcode `.SemanticModel`. Same for Report: use `PBIR_DIR` (e.g., `Sales.Report`).
- All bash paths must be double-quoted (e.g., `"$VAR"`, `"$SM_DIR/"`)
- Session context: Read-then-Write `.pbi-context.md`, 20 row max Command History, never touch Analyst-Reported Failures
- TMDL: tabs only for indentation
- TMSL expression format: preserve original form (string vs array); use array if expression has line breaks
- Escalation state: `## Escalation State` in `.pbi-context.md` tracks gathered context during escalation. Read before solving (use existing context), write after asking escalation questions. Clear at session start if stale.
- **LOCAL-FIRST GIT POLICY (CRITICAL):** The local copy of all files is ALWAYS the source of truth. The skill MUST NEVER run `git pull`, `git fetch`, `git merge`, `git rebase`, or any command that downloads or overwrites local files with remote content. The skill MUST NEVER suggest or run `git push`, and MUST NEVER create pull requests. Allowed git operations: `git init`, `git add`, `git commit`, `git diff`, `git log`, `git status`, `git revert`, `git rev-parse`. If the user manually asks to push or pull, they do it themselves outside the skill. This policy exists because pulling has previously overwritten local PBIP changes and broken relationships.
- **Auto-Resume:** Every `/pbi` invocation loads project context automatically (see Auto-Resume section above). Individual commands should skip their "Model Context Check" (Step 0.5) if Auto-Resume already loaded context.

## Troubleshooting

### PBIP project not detected
**Symptom:** PBIP_MODE=paste even though a .pbip project exists in the directory.
**Cause:** The `.SemanticModel` or `*.SemanticModel` folder is missing, renamed, or nested in a subdirectory.
**Solution:**
- Verify the folder exists: `ls -d *.SemanticModel .SemanticModel 2>/dev/null`
- Ensure CWD is the project root (the folder containing the `.SemanticModel` directory)
- If in a subfolder, run `cd ..` to the project root and retry

### Git not initialized
**Symptom:** GIT=no — commands like diff, commit, undo, and changelog are unavailable.
**Cause:** The project directory has no git repository.
**Solution:** Run `/pbi commit` — it will auto-initialize a git repo and create the first commit.

### Context file stale or corrupted
**Symptom:** Auto-resume shows outdated tables/measures, or commands reference entities that no longer exist.
**Cause:** `.pbi-context.md` is out of sync with the actual model files.
**Solution:** Run `/pbi load` to rebuild context from scratch. This overwrites the existing context file.

### TMDL indentation broken after edit
**Symptom:** Power BI Desktop shows parse errors after a skill edit.
**Cause:** Spaces were used instead of tabs in TMDL files.
**Solution:** The skill enforces tab indentation, but if an external edit introduced spaces, fix with: `sed -i 's/^    /\t/g' <file>.tmdl` (replace 4-space runs with tabs). Then run `/pbi diff` to verify.

### Measure name not found
**Symptom:** A command says a measure doesn't exist, but it does.
**Cause:** Measure name contains accented characters (French) or special characters, and the search failed due to encoding issues.
**Solution:** The skill uses Python-based search (`detect.py search`) with UTF-8 encoding. If you still see this error, verify the file encoding: `python -c "open('file.tmdl','r',encoding='utf-8').read()"` — if this fails, the file may have non-UTF-8 encoding.
