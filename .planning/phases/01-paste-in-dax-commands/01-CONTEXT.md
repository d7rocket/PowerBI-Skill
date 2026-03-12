# Phase 1: Paste-in DAX Commands - Context

**Gathered:** 2026-03-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Four slash commands (`/pbi:explain`, `/pbi:format`, `/pbi:optimise`, `/pbi:comment`) that work purely from pasted DAX — no PBIP project or file access required. Plus a `/pbi:load` command slot (Haiku-based, established as architecture pattern now; full value arrives in Phase 2 when it reads PBIP files). Plus `.pbi-context.md` session tracking.

Creating posts, interactions, and all file-write operations are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Command Invocation UX
- All four commands use the same prompt-then-paste pattern: command runs, responds with "Paste your DAX measure below:", analyst pastes the full measure
- Full DAX assignment expected (`MeasureName = expression`) — commands extract the name themselves
- Invalid or partial DAX: attempt it anyway, flag the syntax issue as part of the output (no rejection/re-prompt)
- Optional `--table TableName` flag accepted by any command to provide table context; not required
- After every command output, always show the full menu of related commands as next steps (not context-selective — always show all)

### Architecture — Haiku/Sonnet Split
- `/pbi:load` is an explicit command the analyst runs before DAX commands when file context is needed; Phase 1 establishes the slot but its full value (reading PBIP model) arrives in Phase 2
- DAX commands in Phase 1 work fine without a prior `/pbi:load` run — paste-in mode needs no prior context load
- Haiku subagents handle all data retrieval and file reading; Sonnet handles all reasoning and output generation
- When Haiku reads model context (Phase 2+), pass only targeted extraction (relevant measure + dependencies), not a full model dump — keeps Sonnet context lean

### Output Structure — /pbi:explain
- Sections with headers: plain English summary at top, then labelled sections: Filter Context, Row Context, Context Transitions, Performance Notes
- Complexity tag shown at top: `_Complexity: Intermediate_` (inferred, not analyst-declared)
- Complex DAX terms used naturally with brief parenthetical: e.g. "triggers a context transition (row context converted to filter context)"

### Output Structure — /pbi:optimise
- Side-by-side layout: Original code block, then Optimised code block, then bulleted list of changes with rationale per change
- Rationale depth scales with complexity: simple rewrites (e.g. swap FILTER for column filter) get brief rationale; complex rewrites (context transitions, iterator restructuring) get full explanation
- Measures containing iterators over measure references: flagged as "requires manual verification — context transition present", not auto-rewritten

### Output Structure — /pbi:comment
- Two labelled blocks: (1) commented DAX code block with inline `//` comments, (2) Description Field value as a plain text block ready to paste into Power BI measure Description property

### Output Structure — /pbi:format
- DAX Formatter API attempted first
- On API failure: quiet note at top of output — `_DAX Formatter API unavailable — formatted inline by Claude_` — then formatted block follows
- No prominent warning, no silent suppression — one line acknowledgement only

### Session Context — .pbi-context.md
- Purpose in Phase 1: track command history (command run, measure pasted, output summary) and analyst-reported failures
- Failures are analyst-reported only — not auto-detected by Claude
- When a prior failure is found on re-run: flagged at top of output before results: "⚠️ Previous attempt at this measure used [approach X] and failed. Using [approach Y] instead."
- File lives in project root, visible and readable/editable by the analyst — not hidden, not tucked in a subdirectory

### Skill Level Adaptation
- Complexity inferred from measure patterns: simple measures (SUM, DIVIDE, basic CALCULATE) → simpler explanation; complex patterns (context transitions, EARLIER, ALLEXCEPT, nested iterators) → technical depth
- No analyst declaration required — no one-time setup, no --level flag
- Same complexity-based approach applies to /pbi:optimise rationale depth

### Claude's Discretion
- Exact DAX Formatter API endpoint and request format (needs empirical verification — STATE.md flags this as medium-confidence)
- Specific section headers within /pbi:explain output (Filter Context, Row Context wording)
- .pbi-context.md schema/structure (as long as it tracks command, measure, output, and failures)
- Follow-up command menu layout and ordering

</decisions>

<specifics>
## Specific Ideas

- Commands should feel immediately useful with zero setup — analyst copies a measure from Power BI Desktop, pastes it, gets value back
- The Haiku/Sonnet split is deliberate: file I/O and model retrieval stay cheap (Haiku), reasoning stays high-quality (Sonnet). This is an architectural principle for the whole skill suite, not just Phase 1
- `/pbi:load` is the explicit gate: "run this first when you want model-aware analysis" — analysts learn one simple rule

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — fresh codebase, no existing components or utilities

### Established Patterns
- No existing patterns — this phase establishes the foundation
- Skill system will live in `.claude/commands/` directory (needs to be created)
- Architecture: Claude skill system files (Markdown with embedded bash/instructions)

### Integration Points
- `.pbi-context.md` in project root — created by Phase 1 commands, read by all subsequent phases
- `/pbi:load` command slot — established here, wired to PBIP file reading in Phase 2

</code_context>

<deferred>
## Deferred Ideas

- `/pbi:load` reading actual PBIP model files — Phase 2 (INFRA-03, INFRA-04, INFRA-05, INFRA-06)
- Error recovery writing fixes back to PBIP files — Phase 2 (ERR-03)
- Comment write-back to PBIP files (`/pbi:comment` in file mode) — Phase 2 (DAX-13)
- Batch commenting across all measures in a table — v2 backlog (DAX-V2-02)

</deferred>

---

*Phase: 01-paste-in-dax-commands*
*Context gathered: 2026-03-12*
