# Phase 5: Direct Editing and Router - Context

**Gathered:** 2026-03-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Two new commands: `/pbi:edit` lets analysts describe any PBIP model change in plain language and have Claude apply it directly to disk; bare `/pbi` orients analysts to the full command suite and routes them to the right subcommand. Phase covers: PBIP file reads and writes, before/after preview with confirmation, pre-write checklist, auto-commit after successful write (GIT-06), and the routing skill.

Creating new commands beyond edit and the router is out of scope.

</domain>

<decisions>
## Implementation Decisions

### Edit input style
- Prompt-then-describe pattern: command responds "Describe the change you want to make:" and waits — consistent with /pbi:explain and /pbi:comment
- Accepts any model change (rename, expression update, format string, display folder, description, relationships, table properties — anything the analyst can describe in plain language)
- If the analyst's change involves updating a measure expression, the command asks them to paste the new DAX — same paste-in pattern as other pbi commands
- PBIP project required: if no `.SemanticModel/` found, output "No PBIP project found. Run /pbi:edit from a directory containing .SemanticModel/." and stop — no paste-in fallback mode

### Ambiguity resolution
- When target matches multiple entities (e.g., [Revenue] in Sales, Products, Finance): show all candidates and ask which one. "Found [Revenue] in: Sales, Products, Finance. Which table?"
- When target doesn't exist: suggest close fuzzy matches. "No measure named [Revnue] found. Did you mean: [Revenue] (Sales), [Revenue YTD] (Sales)?"
- When analyst describes a creation (e.g., "add measure [Revenue YTD] to Sales"): treat creation as a valid edit operation — scaffold the entity in the right table file and proceed through the normal preview/confirm flow

### Change preview format
- Human-readable Before/After in labelled code blocks (not raw `+/-` diff)
- Always show the target file path as a header: `File: .SemanticModel/definition/tables/Sales.tmdl`
- Format:
  ```
  File: .SemanticModel/definition/tables/Sales.tmdl

  **Before**
  [code block with original TMDL snippet]

  **After**
  [code block with modified TMDL snippet]

  Write this change? (y/N)
  ```
- Default is N (capital N) — pressing Enter = cancel. On N: "Change discarded. No files modified." Consistent with pbi-error confirm-before-write pattern

### Pre-write checklist (EDIT-02)
- Desktop-closed confirmation (same guard as pbi-comment/pbi-error)
- `unappliedChanges.json` check: if file exists in `.SemanticModel/`, warn "unappliedChanges.json detected — Desktop may have unsaved changes. Proceed anyway? (y/N)"
- TMDL indentation preservation: when writing TMDL, read the existing file first, match exact indentation style (spaces vs tabs, indent depth) before writing back

### Auto-commit (EDIT-04 / GIT-06)
- After successful write: silent commit + one confirmation line: `Auto-committed: chore: update [MeasureName] in TableName`
- Carries forward Phase 4 established pattern exactly — conventional commit `chore:` prefix for metadata edits, `feat:` for additions
- If no git repo: skip commit, show hint "No git repo — run /pbi:commit to initialise one." File write still succeeds

### Router — bare /pbi
- Free-form routing: if analyst types `/pbi [intent]` (with inline text), Claude reads intent and routes directly to the right subcommand without showing a menu
- Bare `/pbi` with no inline text: show a category-based menu (not individual command list)
- Category menu groups: "Work on a DAX measure", "Audit the model", "See or commit changes", "Edit a model file"
- After category selection: one follow-up question to narrow to exact command (e.g., "Which DAX command: explain, format, optimise, comment?") before launching

### Claude's Discretion
- Exact fuzzy match algorithm for close-match suggestions (edit distance, prefix match, etc.)
- How to parse free-form analyst intent into a target command in the router
- Exact wording of routing follow-up questions

</decisions>

<specifics>
## Specific Ideas

No specific references or "I want it like X" moments — open to standard approaches within the decisions above.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- All existing skills (`pbi-commit`, `pbi-diff`, `pbi-comment`, `pbi-error`): Each uses the same three-block pattern (PBIP Context Detection, Git State Check, Session Context bash injections at the top) — `/pbi:edit` should follow this exact structure
- Desktop-closed guard logic in `pbi-comment/SKILL.md` and `pbi-error/SKILL.md`: copy the tasklist check + fallback pattern directly
- Auto-commit block in `pbi-comment/SKILL.md` and `pbi-error/SKILL.md`: reuse same block structure for EDIT-04

### Established Patterns
- PBIP_MODE / PBIP_FORMAT flag-based branching: every skill branches on `PBIP_MODE=file` vs `PBIP_MODE=paste`; `/pbi:edit` uses the same — stops on `PBIP_MODE=paste`
- Read-then-Write for `.pbi-context.md`: single-pass atomic update (not append) — established in Phase 2
- Confirm-before-write with capital-N default: established in `pbi-error` — copy exactly
- `disable-model-invocation: true` + `model: sonnet` frontmatter: all existing skills use this combination

### Integration Points
- `/pbi` bare command: new skill file at `.claude/skills/pbi/SKILL.md` — routes into existing subcommands by describing them and asking what the analyst needs
- `/pbi:edit`: new skill file at `.claude/skills/pbi-edit/SKILL.md` — integrates with existing TMDL test fixtures in `tests/fixtures/pbip-tmdl` and `tests/fixtures/pbip-tmsl` for verification

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-direct-editing-and-router*
*Context gathered: 2026-03-12*
