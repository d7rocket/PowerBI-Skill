# Phase 2: Context-Aware DAX - Context

**Gathered:** 2026-03-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Make DAX output grounded in the user's actual model: real table/column names, duplication prevention, and filter context warnings before generating filter-sensitive patterns. Applies to all DAX subcommands (explain, format, optimise, comment, error, new) on both the fast path and deep mode. Visual recommendations, phase gates beyond the measures gate, and business question verification flows are out of scope for this phase.

</domain>

<decisions>
## Implementation Decisions

### Context intake on fast path
- When any DAX command runs and `.pbi-context.md` has no model context, ask: "Which table, and which columns are relevant to this measure?" — targeted ask, not a full schema dump
- Applies to ALL DAX subcommands (explain, format, optimise, comment, error, new), not just `/pbi new`
- Answer is stored in `.pbi-context.md` and reused for subsequent measures in the same session (no re-asking)
- If context is already present from a prior `/pbi load` or previous session, skip the ask

### Duplication check
- Every `/pbi new` asks "Does a similar measure already exist in the model?" before generating — always-on, not conditional on context state
- Simple yes/no question format
- If user answers yes: ask "What's the existing measure?" then generate a new measure that extends or wraps the existing one (e.g., `CALCULATE([ExistingMeasure], filter)`) rather than duplicating the logic

### Filter-sensitive DAX trigger
- Trigger pattern list: time intelligence (DATEYTD, SAMEPERIODLASTYEAR, TOTALYTD, DATESYTD) + ratio/rank (DIVIDE, RANKX, TOPN, PERCENTILEX)
- When a filter-sensitive pattern is detected, ask BEFORE generating: "Where will this be placed and what date/filter slicers are active?"
- Generate DAX only after the user answers — output is informed by visual context from the start
- Visual placement context (visual type + active slicers) is saved to `.pbi-context.md` and reused for subsequent filter-sensitive measures in the session

### Measures gate in deep mode
- Triggered at the end of a deep mode session (Phase 2 scope: measures = end of session; visuals/polish are Phase 3 territory)
- Gate shows a summary of all measures generated in the session (measure names + target tables)
- Gate asks two things before closing:
  1. Restates the business question from `.pbi-context.md` and asks: "Do these measures answer it?"
  2. "All measures complete — confirm to close the deep mode session"
- Full business question verification flow (VERF-02) is Phase 3; this is a lightweight check only

### Claude's Discretion
- Exact phrasing of the context intake question per subcommand (explain vs new have different natural phrasing)
- How to detect the filter-sensitive pattern from the user's request text (keyword matching on function names vs intent reading)
- Whether to surface the "visual context saved" acknowledgment or silently store it

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `new.md` Step 1 — already asks "Which table?" if not in arguments; extend to also ask for relevant columns
- `new.md` Step 2 — already reads `.pbi-context.md` Model Context and uses it; extend this logic to all DAX command files
- `new.md` Step 6 (Update Session Context) — established Read-then-Write pattern; extend to write column context and visual placement context
- `.pbi-context.md` schema — has `## Model Context` section; add `## Visual Context` section for slicer/placement storage

### Established Patterns
- Context is read at command start, written at command end (not mid-execution)
- `.pbi-context.md` sections: `## Last Command`, `## Command History`, `## Analyst-Reported Failures`, `## Model Context`
- Attempt counter is in-session memory only (not written to `.pbi-context.md`)
- All DAX subcommands are self-contained `.md` files in `commands/` — each must implement its own context intake step

### Integration Points
- All 6 DAX command files need a new "Context intake" step (likely Step 0.5 or prepended to Step 1): check `.pbi-context.md` for model context, ask if absent
- `commands/new.md` needs two additional steps: duplication check (after collecting requirements, before generating) and filter-sensitive pattern detection (after understanding business intent, before generating)
- `commands/deep.md` needs a measures gate step appended to its session flow
- `.pbi-context.md` needs a `## Visual Context` section for storing visual type and active slicers

</code_context>

<specifics>
## Specific Ideas

- The context intake ask should feel lightweight — single question, not a form. "Which table and which columns are relevant?" is the target phrasing for `/pbi new`; other commands may adapt naturally (e.g., for `/pbi explain`: "Which table does this measure belong to?" may suffice since columns are visible in the DAX)
- The duplication check is a one-liner before generation — not a separate step. Fits naturally between "collect requirements" and "generate" in `new.md`
- "Does a similar measure already exist?" — if yes, the follow-up is 'paste it or name it', then the skill wraps it

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-context-aware-dax*
*Context gathered: 2026-03-13*
