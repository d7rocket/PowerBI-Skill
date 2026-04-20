---
name: pbi:resume
description: "Restore session context and continue from where you left off"
allowed-tools:
  - Read
  - Write
  - Bash
  - Agent
  - Glob
  - Grep
---

## Detection

Run ALL of the following detection commands using the Bash tool before proceeding. Save the output.

Ensure .pbi/ directory exists and migrate legacy root-level files.
```bash
python ".claude/skills/pbi/scripts/detect.py" ensure-dir 2>/dev/null
python ".claude/skills/pbi/scripts/detect.py" migrate 2>/dev/null
```

```bash
python ".claude/skills/pbi/scripts/detect.py" pbip 2>/dev/null || echo "PBIP_MODE=paste"
```

Save the `PBIP_DIR` value from the output.

```bash
python ".claude/skills/pbi/scripts/detect.py" git 2>/dev/null || (echo "GIT=no" && echo "HAS_COMMITS=no")
```

```bash
python ".claude/skills/pbi/scripts/detect.py" context 2>/dev/null || echo "No prior context found."
```

Save the PBI_CONFIRM value — use it to decide whether to ask before writing files.
```bash
python ".claude/skills/pbi/scripts/detect.py" settings 2>/dev/null || echo "PBI_CONFIRM=true"
```

### Auto-Resume (session-aware)

After detection, apply the following before executing the command:

1. **PBIP_MODE=file — session load check**:
   Run:
   ```bash
   python ".claude/skills/pbi/scripts/detect.py" session-check 2>/dev/null
   ```
   - If output is `SESSION=active` — context was already loaded this session: proceed directly to the command instructions.
   - If output is `SESSION=new` — first command this session: write `**Session-Start:** [current UTC time in ISO 8601]` to `.pbi/context.md` if a PBIP project is active. Proceed to the command instructions (resume reads the cached context file, not model files).

2. **PBIP_MODE=paste — nearby folder check**: skip silently for resume command.

After auto-resume completes, proceed to the command instructions below.

---

# /pbi-resume

<purpose>
Claude Code sessions are ephemeral — /clear or a new terminal loses all accumulated context. Resume bridges that gap by reading the persisted .pbi/context.md file and reconstructing the working state, so the analyst can continue where they left off without re-running /pbi-load or re-explaining the project.
</purpose>

<core_principle>
Restore, don't re-run. Read the cached context file to understand what was done — don't re-execute commands or re-read model files unless the context is stale or missing. Show a clear summary of restored state so the analyst knows exactly where they stand.
</core_principle>

## Instructions

### Step 1 — Check for context file

Check if `.pbi/context.md` exists and has content beyond the template headers.

- **No file or empty:** Output and stop:
  > No session context found. Run `/pbi-load` to initialize the project, or use any `/pbi-` command — context is created automatically on first use.

- **File exists with content:** Proceed to Step 2.

---

### Step 2 — Parse context file

Read `.pbi/context.md` with the Read tool. Extract:

1. **Last Command** — Command name, timestamp, measure, and outcome
2. **Model Context** — Count tables, total measures, total relationships
3. **Command History** — Last 5 rows from the history table
4. **Business Question** — If present (from /pbi-deep)
5. **Escalation State** — If present (from free-text solving)
6. **Analyst-Reported Failures** — If present and non-empty

---

### Step 3 — Check git state

If GIT=yes and HAS_COMMITS=yes, run:
```bash
git log --oneline -5 2>/dev/null
```

If GIT=no: note "No git repository initialized."

---

### Step 4 — Determine context freshness

Parse the timestamp from `## Last Command`.

- Less than 1 hour old: `Current`
- 1–24 hours old: `Recent`
- More than 24 hours old: `Stale — consider running /pbi-load to refresh`
- No timestamp: `Unknown`

---

### Step 5 — Output resume summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PBI ► SESSION RESUMED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Context:** [freshness] — last activity [relative time]

### Model
| Tables | Measures | Relationships |
|--------|----------|---------------|
| [N]    | [N]      | [N]           |

### Last Command
`[command]` — [outcome] ([timestamp])

### Recent History
| Time | Command | Measure | Result |
|------|---------|---------|--------|
[last 5 rows]

[conditional: ### Active Workflow, ### Pending Escalation, ### Known Failures]

### Git State
[last 5 commits or "No git repository"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ready to continue. Type any /pbi- command or describe what you need.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Step 6 — Update session context

Read-then-Write `.pbi/context.md`:
- `## Last Command`: Command = `/pbi-resume`, Outcome = `Session resumed — [N] tables, context [freshness]`
- Prepend row to `## Command History`; trim to 20 rows max
- Do NOT modify `## Model Context` or `## Analyst-Reported Failures`

### Anti-Patterns
- NEVER re-read model files during resume — use cached context only
- NEVER modify the Model Context section
- NEVER suggest git pull or git push
- NEVER skip freshness check
- NEVER run /pbi-load automatically — only suggest it if context is stale
