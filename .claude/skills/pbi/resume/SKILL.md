---
name: pbi:resume
description: "Restore session context and continue from where you left off. Reads .pbi-context.md to reconstruct model state, command history, in-progress workflows, and git state. Use when starting a new session, after /clear, or when resuming interrupted work."
model: haiku
allowed-tools: Read, Write, Bash, Agent
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 6.0.0
  category: data-analytics
  tags: [power-bi, dax, pbip, semantic-model]
---

<purpose>
Claude Code sessions are ephemeral — /clear or a new terminal loses all accumulated context. Resume bridges that gap by reading the persisted .pbi-context.md file and reconstructing the working state, so the analyst can continue where they left off without re-running /pbi:load or re-explaining the project.
</purpose>

<core_principle>
Restore, don't re-run. Read the cached context file to understand what was done — don't re-execute commands or re-read model files unless the context is stale or missing. Show a clear summary of restored state so the analyst knows exactly where they stand.
</core_principle>

## Detection (run once)

**Folder naming:** Real PBIP projects use `<ProjectName>.SemanticModel` and `<ReportName>.Report`. Detection globs for both patterns.

### PBIP Detection
!`python ".claude/skills/pbi/scripts/detect.py" pbip 2>/dev/null || echo "PBIP_MODE=paste"`

Save the `PBIP_DIR` value from the output.

### Git State
!`python ".claude/skills/pbi/scripts/detect.py" git 2>/dev/null || (echo "GIT=no" && echo "HAS_COMMITS=no")`

### Session Context
!`python ".claude/skills/pbi/scripts/detect.py" context 2>/dev/null || echo "No prior context found."`

---

# /pbi:resume


## Instructions

### Step 1 — Check for context file

Check if `.pbi-context.md` exists and has content beyond the template headers.

- **No file or empty:** Output the following and stop:
  > No session context found. Run `/pbi:load` to initialize the project, or use any `/pbi:` command — context is created automatically on first use.

- **File exists with content:** Proceed to Step 2.

---

### Step 2 — Parse context file

Read `.pbi-context.md` with the Read tool. Extract the following sections if present:

1. **Last Command** — Command name, timestamp, measure, and outcome
2. **Model Context** — Count tables, total measures across all tables, total relationships
3. **Command History** — Extract the last 5 rows from the history table
4. **Business Question** — If present (set by `/pbi:deep` intake phase)
5. **Escalation State** — If present (set by free-text solving escalation)
6. **Analyst-Reported Failures** — If present and has data rows

---

### Step 3 — Check git state

If GIT=yes and HAS_COMMITS=yes, run:
```bash
git log --oneline -5 2>/dev/null
```

Extract the last 5 commits for display.

If GIT=no: note "No git repository initialized."

---

### Step 4 — Determine context freshness

Parse the timestamp from `## Last Command`.

- **Less than 1 hour old:** Label as `Current`
- **1–24 hours old:** Label as `Recent`
- **More than 24 hours old:** Label as `Stale — consider running /pbi:load to refresh`
- **No timestamp found:** Label as `Unknown`

---

### Step 5 — Output resume summary

Output the following, filling in values from Steps 2–4:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PBI ► SESSION RESUMED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Context:** [Current | Recent | Stale] — last activity [relative time, e.g., "2 hours ago"]

### Model
| Tables | Measures | Relationships |
|--------|----------|---------------|
| [N]    | [N]      | [N]           |

### Last Command
`[command name]` — [outcome] ([timestamp])

### Recent History
| Time | Command | Measure | Result |
|------|---------|---------|--------|
[last 5 rows from Command History]
```

**Conditional sections** — include only if the data exists in the context file:

If `## Business Question` is present:
```
### Active Workflow
**Business question:** [question text]
**Status:** [infer from context — "Intake complete" if model review exists, "In development" if DAX was written, etc.]
```

If `## Escalation State` contains "awaiting":
```
### Pending Escalation
**Awaiting:** [gap type]
**Question asked:** [the escalation question]
```

If `## Analyst-Reported Failures` has data rows:
```
### Known Failures
[N] reported failure(s) on file — these measures will use alternative approaches when re-attempted.
```

Git state section:
```
### Git State
[If GIT=yes: show last 5 commits from Step 3]
[If GIT=no: "No git repository — run /pbi:commit to initialize one."]
```

Close with:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ready to continue. Type any /pbi: command or describe what you need.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Step 6 — Update session context

Read `.pbi-context.md` with Read tool and update:

- `## Last Command`: Set Command = `/pbi:resume`, Timestamp = current ISO 8601, Measure = `—`, Outcome = `Session resumed — [N] tables, context [freshness]`
- `## Command History`: Prepend row `| [timestamp] | /pbi:resume | — | Session resumed |`
- Trim Command History to 20 rows max
- Do NOT modify `## Model Context`, `## Analyst-Reported Failures`, or any other sections

Write back with Write tool.

### Anti-Patterns
- NEVER re-read model files during resume — use the cached context only
- NEVER modify the Model Context section — resume is read-only for model data
- NEVER suggest git pull or git push
- NEVER skip the freshness check — always inform the analyst about context age
- NEVER output partial state — if a section exists in context, display it fully
- NEVER run /pbi:load automatically — only suggest it if context is stale

## Post-Command Footer

After ALL steps above are complete, output the context usage bar as the final line:

```bash
python ".claude/skills/pbi/scripts/detect.py" context-bar 2>/dev/null
```

Print the output of this command as the very last line shown to the user.

## Shared Rules

- **PYTHON-FIRST FILE OPERATIONS (CRITICAL):** All file read/write and text search operations MUST use Python with `encoding='utf-8'` to correctly handle accented characters (French: é, è, ê, ç, à, ù, etc.). Do NOT use `grep`, `cat`, `sed`, `awk`, or shell redirects for reading/writing model files. For measure name search, use `python ".claude/skills/pbi/scripts/detect.py" search "MeasureName" "$PBIP_DIR"` instead of `grep -rlF`. Shell/bash is allowed ONLY for: git CLI commands and Python script invocation.
- **PBIP folder naming:** Always use the `PBIP_DIR` value from detection (e.g., `Sales.SemanticModel`) — never hardcode `.SemanticModel`. Same for Report: use `PBIR_DIR` (e.g., `Sales.Report`).
- All bash paths must be double-quoted (e.g., `"$VAR"`, `"$SM_DIR/"`)
- Session context: Read-then-Write `.pbi-context.md`, 20 row max Command History, never touch Analyst-Reported Failures
- TMDL: tabs only for indentation
- TMSL expression format: preserve original form (string vs array); use array if expression has line breaks
- Escalation state: `## Escalation State` in `.pbi-context.md` tracks gathered context during escalation.
- **LOCAL-FIRST GIT POLICY (CRITICAL):** NEVER `git pull`, `git fetch`, `git merge`, `git rebase`, `git push`, or create PRs. Allowed: `git init`, `git add`, `git commit`, `git diff`, `git log`, `git status`, `git revert`, `git rev-parse`.
- **Post-write staging:** After any command writes files to `$PBIP_DIR/` (and PBIP_MODE=file, GIT=yes), auto-stage: `git add "$PBIP_DIR/" 2>/dev/null`. Skip if the command already auto-committed.
