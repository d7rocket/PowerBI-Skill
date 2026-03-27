---
name: pbi:help
description: "Show command reference with version check. Use when user says 'help', 'commands', 'what can you do', or 'list commands'."
model: sonnet
allowed-tools: Read, Write, Bash, Agent
disable-model-invocation: true
metadata:
  author: d7rocket
  version: 4.4.0
  category: data-analytics
  tags: [power-bi, dax, pbip, semantic-model]
---

# /pbi:help


## Instructions

### Step 1 — Version check

Run the following bash command to read the local version and check the remote for updates:

```bash
SKILL_FILE=$(find . -path "*/.claude/skills/pbi/SKILL.md" -print -quit 2>/dev/null)
if [ -z "$SKILL_FILE" ]; then SKILL_FILE=$(find "$HOME" -maxdepth 5 -path "*/.claude/skills/pbi/SKILL.md" -print -quit 2>/dev/null); fi
python .claude/skills/pbi/scripts/detect.py version-check "$SKILL_FILE" 2>/dev/null || echo "LOCAL=unknown"

# Fetch latest remote tag (timeout 5s to avoid blocking on no network)
REMOTE_VER=$(git ls-remote --tags --sort=-v:refname origin 2>/dev/null | head -1 | sed 's/.*refs\/tags\///' | sed 's/\^{}//')
if [ -z "$REMOTE_VER" ]; then
  echo "REMOTE=unavailable"
else
  echo "REMOTE=$REMOTE_VER"
fi
```

Parse the output:
- `LOCAL` = installed version (e.g., `4.0.0`)
- `REMOTE` = latest git tag (e.g., `v4.1.0`) or `unavailable`

Build the version line for the header:

- If REMOTE is `unavailable`: `**Version:** LOCAL (could not check for updates)`
- If LOCAL matches REMOTE (strip leading `v`): `**Version:** LOCAL ✓ up to date`
- If LOCAL is behind REMOTE: `**Version:** LOCAL → **Update available: REMOTE** — download the latest release manually from the repository`

### Step 2 — Output help reference

Output the following, inserting the version line from Step 1:

---

```
# /pbi — Power BI DAX Co-Pilot
[version line from Step 1]

## DAX Commands (paste-in — work anywhere)

| Command | Description | Model |
|---------|-------------|-------|
| `/pbi:explain` | Break down a DAX measure into plain English | Sonnet |
| `/pbi:format` | Reformat DAX for readability (uses DAX Formatter API) | Sonnet |
| `/pbi:optimise` | Analyse DAX for performance and suggest improvements | Sonnet |
| `/pbi:comment` | Add inline comments to a DAX measure | Sonnet |
| `/pbi:error` | Diagnose a DAX error and suggest fixes | Sonnet |
| `/pbi:new` | Scaffold a new measure from a plain-English description | Sonnet |

## PBIP Commands (require `*.SemanticModel/` directory)

| Command | Description | Model |
|---------|-------------|-------|
| `/pbi:load` | Read project structure into session context | Haiku |
| `/pbi:audit` | Full model health check with auto-fix for critical issues | Sonnet |
| `/pbi:edit` | Modify model entities from plain-English instructions | Sonnet |
| `/pbi:comment-batch` | Add descriptions to all undocumented measures | Sonnet |
| `/pbi:extract` | Export a structured summary of your PBIP project | Varies |
| `/pbi:diff` | Summarise uncommitted model changes | Haiku |
| `/pbi:commit` | Stage and commit model changes with a generated message | Haiku |
| `/pbi:undo` | Revert the last auto-commit | Haiku |
| `/pbi:changelog` | Generate release notes from recent commits | Haiku |

## Workflow Commands

| Command | Description | Model |
|---------|-------------|-------|
| `/pbi:deep` | Guided multi-phase workflow: intake → model review → DAX dev → verification | Sonnet |
| `/pbi:help` | Show this reference with version check | — |

## Quick Start

1. **No project?** Paste DAX directly: `/pbi:explain <your DAX>`
2. **Have a PBIP project?** Run `/pbi:load` first, then any command uses model context automatically.
3. **Full guided session?** Use `/pbi:deep` for complex multi-measure work.
4. **Project summary?** Use `/pbi:extract [overview|standard|deep-dive]` to generate a model overview.

## Tips

- All commands read `.pbi-context.md` for session state — run `/pbi:load` once to prime it.
- `/pbi:audit` can auto-fix critical issues (bidirectional filters, unhidden key columns).
- Free-text works too — just type `/pbi <your question>` and it will be solved directly.
- Model selection is automatic: Haiku for file/git ops, Sonnet for DAX reasoning, Opus for deep extraction.
```

---

Stop. Do not output anything else.

### Anti-Patterns
- NEVER suggest git pull or git push
- NEVER output anything after the help reference — stop immediately
