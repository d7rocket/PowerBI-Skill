---
name: pbi
description: Power BI skill suite entry point. Routes to the appropriate /pbi subcommand based on analyst intent. Use when an analyst types /pbi with or without a description of what they need.
version: 2.0.0
disable-model-invocation: true
model: sonnet
allowed-tools: Read
---

## Routing Logic

If `$ARGUMENTS` is non-empty (analyst typed `/pbi [some intent]`):

Read the inline text as analyst intent. Map to the most relevant subcommand using this keyword table:
- "explain" / "what does" / "understand" / "how does" → /pbi:explain
- "format" / "clean up" / "prettify" / "style" → /pbi:format
- "optimise" / "optimize" / "performance" / "speed up" / "slow" → /pbi:optimise
- "comment" / "annotate" / "document" / "describe" → /pbi:comment
- "audit" / "health check" / "review model" / "find issues" → /pbi:audit
- "diff" / "what changed" / "changes" / "show changes" → /pbi:diff
- "commit" / "save" / "snapshot" / "git" → /pbi:commit
- "error" / "fix" / "diagnose" / "broken" / "failing" → /pbi:error
- "edit" / "rename" / "update" / "change" / "modify" → /pbi:edit
- "new" / "create" / "add measure" / "scaffold" → /pbi:new
- "undo" / "revert" / "undo last" / "go back" → /pbi:undo
- "load" / "context" / "model context" / "load project" → /pbi:load
- "comment all" / "batch comment" / "document all" / "comment batch" → /pbi:comment-batch
- "branch" / "feature branch" / "new branch" / "merge" → /pbi:branch
- "changelog" / "release notes" / "history" / "what shipped" → /pbi:changelog

Output: "Routing to /pbi:[subcommand] — [one-line description of what it does]."
Then immediately behave as if the analyst had invoked /pbi:[subcommand] directly (carry through any inline arguments that follow the intent keyword as if they were passed to the subcommand).

If intent is ambiguous between two commands: pick the most specific match and note it — "Routing to /pbi:edit (you can also use /pbi:comment if you only need to add comments)."

## Category Menu (bare /pbi)

If `$ARGUMENTS` is empty or absent:

Output the following category menu exactly:

---
What would you like to do?

**A — Work on a DAX measure**
  explain · format · optimise · comment · new

**B — Audit the model**
  audit (includes hidden column hygiene, auto-fix, and PBIR visual audit)

**C — See, commit, or undo changes**
  diff · commit · undo · branch · changelog

**D — Edit a model file**
  edit · comment-batch

Type A, B, C, or D — or describe what you need and I'll route you directly.

---

On analyst response:

- "A": Ask — "Which DAX command? **explain** · **format** · **optimise** · **comment** · **new**" — then on selection route to the chosen /pbi:DAX subcommand.
- "B": Route directly to /pbi:audit. Output "Routing to /pbi:audit — running a full model health check." then proceed as /pbi:audit.
- "C": Ask — "Which command? **diff** — see what changed · **commit** — save a snapshot · **undo** — revert the last commit · **branch** — manage feature branches · **changelog** — generate release notes" — then on selection route to the chosen subcommand.
- "D": Ask — "Which command? **edit** — change a specific entity · **comment-batch** — comment all measures at once" — then on selection route to the chosen subcommand.
- Free-text response: Apply the intent mapping from the Routing Logic section above and route directly.
- Any response that does not match A/B/C/D or a recognisable intent keyword: Output "I didn't catch that — type A, B, C, or D, or describe what you need."
