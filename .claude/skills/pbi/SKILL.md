---
name: pbi
description: Power BI DAX co-pilot. /pbi [subcommand] routes to the appropriate handler.
version: 4.0.0
disable-model-invocation: true
model: sonnet
allowed-tools: Read, Write, Bash, Agent
argument-hint: "[explain|format|optimise|comment|error|new|load|audit|diff|commit|edit|undo|comment-batch|changelog|deep|extract|help]"
---

## Detection Blocks (run once, shared by all subcommands)

**Folder naming:** Real PBIP projects use `<ProjectName>.SemanticModel` and `<ReportName>.Report` (e.g., `Sales.SemanticModel`, `Sales.Report`). Test fixtures may use `.SemanticModel`. Detection globs for both patterns.

### PBIP Detection
!`SM_DIR=$(ls -d *.SemanticModel .SemanticModel 2>/dev/null | head -1); if [ -n "$SM_DIR" ]; then if [ -f "$SM_DIR/model.bim" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmsl PBIP_DIR=$SM_DIR"; elif [ -d "$SM_DIR/definition/tables" ]; then echo "PBIP_MODE=file PBIP_FORMAT=tmdl PBIP_DIR=$SM_DIR"; else echo "PBIP_MODE=file PBIP_FORMAT=tmdl PBIP_DIR=$SM_DIR"; fi; else echo "PBIP_MODE=paste"; fi`

Save the `PBIP_DIR` value from the output — all subsequent commands must use it instead of a hardcoded `.SemanticModel`.

### File Index
!`SM_DIR=$(ls -d *.SemanticModel .SemanticModel 2>/dev/null | head -1); if [ -d "$SM_DIR/definition/tables" ]; then find "$SM_DIR/definition/tables/" -name "*.tmdl" 2>/dev/null; elif [ -f "$SM_DIR/model.bim" ]; then echo "tmsl:$SM_DIR/model.bim"; fi`

### PBIR Detection
!`RPT_DIR=$(ls -d *.Report .Report 2>/dev/null | head -1); if [ -n "$RPT_DIR" ]; then find "$RPT_DIR/" -name "*.json" -not -name "item.config.json" -not -name "item.metadata.json" 2>/dev/null | head -20 && echo "PBIR=yes PBIR_DIR=$RPT_DIR"; else echo "PBIR=no"; fi`

### Git State
!`git rev-parse --is-inside-work-tree 2>/dev/null && echo "GIT=yes" || echo "GIT=no"; git rev-parse HEAD 2>/dev/null && echo "HAS_COMMITS=yes" || echo "HAS_COMMITS=no"`

### Session Context
!`cat ".pbi-context.md" 2>/dev/null | tail -80 || echo "No prior context found."`

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
| audit, "health check", "review model", "find issues" | commands/audit.md | sonnet direct |
| load, context, "model context", "load project" | commands/load.md | haiku Agent |
| diff, "what changed", changes, "show changes" | commands/diff.md | haiku Agent |
| commit, save, snapshot, git | commands/commit.md | haiku Agent |
| undo, revert, "go back" | commands/undo.md | haiku Agent |
| changelog, "release notes", history, "what shipped" | commands/changelog.md | haiku Agent |
| deep | commands/deep.md | sonnet direct |
| extract, "project summary", "model summary", "export model" | commands/extract.md | sonnet direct |
| help, commands, "what can you do", "list commands" | commands/help.md | sonnet direct |
| (no keyword match — free-text) | Solve-first handler (inline below) | sonnet direct |

If intent is ambiguous between two commands: pick the most specific match and note it — "Routing to /pbi edit (you can also use /pbi comment if you only need to add comments)."

### Execution

**For sonnet subcommands** (explain, format, optimise, comment, error, new, edit, comment-batch, audit, deep, extract, help):
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

**? — Help**
  List all commands

Type A, B, C, D, E, F, or ? — or describe what you need and I'll route you directly.

---

On analyst response:

- "A": Ask — "Which DAX command? **explain** · **format** · **optimise** · **comment** · **new**" — then route.
- "B": Route directly to audit. Output "Routing to /pbi audit — running a full model health check." then proceed.
- "C": Ask — "Which command? **diff** — see what changed · **commit** — save a snapshot · **undo** — revert the last commit · **changelog** — generate release notes" — then route.
- "D": Ask — "Which command? **edit** — change a specific entity · **comment-batch** — comment all measures at once" — then route.
- "E": Route to `/pbi deep`.
- "F": Route to `/pbi extract`.
- "?": Route to `/pbi help`.
- Free-text response: Apply the keyword matching from the Routing table above. If no keyword matches, route to **Solve-First Default** handler and treat the text as the request.
- Any response that does not match A/B/C/D/E/F/? or a recognisable keyword: Output "I didn't catch that — type A, B, C, D, E, F, or ? — or describe what you need."

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

## Shared Rules

- All bash paths must be double-quoted (e.g., `"$VAR"`, `"$SM_DIR/"`)
- **PBIP folder naming:** Always use the `PBIP_DIR` value from detection (e.g., `Sales.SemanticModel`) — never hardcode `.SemanticModel`. Same for Report: use `PBIR_DIR` (e.g., `Sales.Report`).
- Session context: Read-then-Write `.pbi-context.md`, 20 row max Command History, never touch Analyst-Reported Failures
- TMDL: tabs only for indentation, use `grep -rlF` for measure names (fixed-string matching)
- DAX in shell: single-quoted heredoc delimiter to prevent `$` and backtick expansion
- TMSL expression format: preserve original form (string vs array); use array if expression has line breaks
- Escalation state: `## Escalation State` in `.pbi-context.md` tracks gathered context during escalation. Read before solving (use existing context), write after asking escalation questions. Clear at session start if stale.
