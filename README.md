<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-Skill-blueviolet?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMiAxNWwtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPjwvc3ZnPg==" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/version-7.0-blue?style=for-the-badge" alt="Version 7.0">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Power_BI-DAX-F2C811?style=for-the-badge&logo=powerbi&logoColor=black" alt="Power BI DAX">
</p>

<div align="center">

```
  ╔═══════════════════════════════════════════════════════╗
  ║                                                       ║
  ║   ██████╗ ██████╗ ██╗  · Power BI DAX Co-pilot        ║
  ║   ██╔══██╗██╔══██╗██║  · for Claude Code              ║
  ║   ██████╔╝██████╔╝██║  ·                              ║
  ║   ██╔═══╝ ██╔══██╗██║  · 22 commands  ·  PBIP-native  ║
  ║   ██║     ██████╔╝██║  · UTF-8 safe   ·  local-first  ║
  ║   ╚═╝     ╚═════╝ ╚═╝                        v7.0    ║
  ║                                                       ║
  ╚═══════════════════════════════════════════════════════╝
```

**Explain, format, optimise, audit, and edit DAX measures — directly from your terminal.**
Works with pasted DAX *and* with Power BI Project (PBIP) files on disk.

</div>

---

## Quick Start

```powershell
# Install (Windows) — one command, all projects
irm https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main/install.ps1 | iex

# Then open Claude Code and type:
/pbi:help
```

```bash
# Install (macOS / Linux / WSL)
curl -sL https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main/install.sh | bash
```

---

## What's New in v7.0

| Feature | Details |
|:--------|:--------|
| **`/pbi:format-batch`** | Format every measure in the model in one pass — SQLBI-standard structure, no API dependency, auto-commits. |
| **`/pbi:settings`** | Dedicated settings command — toggle auto mode (silent writes) vs confirm mode (preview before every write). |
| **22 independent commands** | Every command is its own `/pbi:<cmd>` skill with full detection, auto-resume, and session awareness. |
| **`.pbi/` context directory** | All runtime files (context, settings, audit reports, docs) live in `.pbi/` — auto-migrated from legacy root paths. |

---

## Commands

### Paste-in — *work anywhere, just paste your DAX*

| Command | What it does |
|:--------|:------------|
| `/pbi:explain` | Structured plain-English breakdown with filter context, row context, and performance notes |
| `/pbi:format` | Reformat DAX for readability via DAX Formatter API |
| `/pbi:optimise` | 13-rule performance scan with severity-graded findings and before/after diffs |
| `/pbi:comment` | Add inline `//` comments and description property for Power BI tooltips |
| `/pbi:error` | Diagnose errors across 7 categories with root cause analysis and auto-fix |
| `/pbi:new` | Generate a complete measure from plain English with format string and display folder |

### PBIP Project — *auto-detected when `*.SemanticModel/` exists*

| Command | What it does |
|:--------|:------------|
| `/pbi:audit` | 19-rule health check across 8 domains with severity grading and auto-fix |
| `/pbi:edit` | Modify measures, columns, and tables using plain-English instructions |
| `/pbi:docs` | Generate polished, stakeholder-ready project documentation |
| `/pbi:extract` | Export model summary at three detail levels (overview, standard, deep-dive) |
| `/pbi:format-batch` | Apply SQLBI-standard formatting to every measure in the model — no API dependency |
| `/pbi:diff` | Human-readable change summary grouped by entity type |
| `/pbi:commit` | Auto-generated business-language commits (local only) |
| `/pbi:undo` | Safely revert the last auto-commit using git revert |
| `/pbi:changelog` | Generate CHANGELOG.md from git history in Keep a Changelog format |
| `/pbi:comment-batch` | Add descriptions to every undocumented measure in the model |

### Workflow & Utility

| Command | What it does |
|:--------|:------------|
| `/pbi:deep` | Four-phase guided workflow with hard gates: intake, model review, DAX dev, verification |
| `/pbi:resume` | Restore session context and continue from where you left off |
| `/pbi:settings` | Toggle auto mode (silent writes) vs confirm mode (preview before every write) |
| `/pbi:version` | Display installed version and full changelog history |
| `/pbi:help` | Complete command reference with remote update check |
| `/pbi` | Interactive menu, backward-compatible router, and free-text DAX solver |

---

## How It Works

```
             ┌───────────────────────────────┐
             │  /pbi:explain  /pbi:audit ... │  ← direct invocation
             └──────────────┬────────────────┘
                            │
             ┌──────────────▼────────────────┐
             │  Each sub-skill runs its own   │
             │  5 detection blocks + resume   │
             └──────────────┬────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌─────────▼─────────┐
│   Paste-in     │  │    PBIP     │  │    Workflow        │
│ explain format │  │ audit edit  │  │ deep extract       │
│ optimise new   │  │ diff commit │  │ docs version       │
│ comment error  │  │ undo load   │  │ help settings      │
│                │  │ changelog   │  │                    │
│   Sonnet       │  │ Haiku/Son.  │  │   Sonnet/Opus      │
└────────────────┘  └─────────────┘  └────────────────────┘
```

| Feature | How |
|:--------|:----|
| **Session Auto-Load** | First command each session refreshes model context automatically |
| **Local-First Git** | Never pulls, pushes, or creates PRs. Your files are the source of truth. |
| **Session Memory** | `.pbi/context.md` persists model context, command history, failure flags |
| **Smart Routing** | Sonnet for DAX reasoning, Haiku for file ops, Opus for deep extraction |
| **UTF-8 Safe** | Python-based search handles French accents (é, è, ê, ç, à, ù) |

---

## Installation Options

### PowerShell (Windows)

User-level (default) — available in all projects:

```powershell
irm https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main/install.ps1 | iex
```

Project-level — installs into current directory only:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main/install.ps1))) -Scope project
```

### Bash (macOS / Linux / WSL)

```bash
curl -sL https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main/install.sh | bash
```

### Manual / Git Clone

```bash
git clone https://github.com/d7rocket/PowerBI-Skill.git
cd PowerBI-Skill && claude
```

Or copy just the skill into an existing project:

```bash
git clone https://github.com/d7rocket/PowerBI-Skill.git /tmp/pbi-skill
cp -r /tmp/pbi-skill/.claude your-project/.claude
```

<details>
<summary>What gets installed</summary>

```
.claude/skills/pbi/
  SKILL.md               Base skill (menu + catch-all + backward-compatible router)
  explain/SKILL.md       22 self-contained sub-skills, each with its own
  format/SKILL.md        detection blocks, auto-resume, and instructions.
  optimise/SKILL.md      Invoked as /pbi:<cmd> (e.g., /pbi:explain).
  comment/SKILL.md
  error/SKILL.md
  new/SKILL.md
  load/SKILL.md
  audit/SKILL.md
  diff/SKILL.md
  commit/SKILL.md
  edit/SKILL.md
  undo/SKILL.md
  comment-batch/SKILL.md
  changelog/SKILL.md
  format-batch/SKILL.md  Bulk-format all measures (no API dependency)
  deep/SKILL.md
  extract/SKILL.md
  docs/SKILL.md
  help/SKILL.md
  version/SKILL.md
  resume/SKILL.md        Session resume and context restoration
  settings/SKILL.md      Write-mode toggle (auto / confirm)
  scripts/detect.py      UTF-8 detection + search (15 subcommands)
  shared/
    api-notes.md         DAX Formatter API reference
    CHANGELOG.md         Version history
    ui-brand.md          Visual output standards reference
```

</details>

---

## Examples

<details>
<summary><strong>Explain a measure</strong></summary>

```
/pbi:explain

> Revenue YTD = CALCULATE([Revenue], DATESYTD('Date'[Date]))
```
Get a structured breakdown — filter context, row context, context transitions, and performance notes.
</details>

<details>
<summary><strong>Scaffold a new measure</strong></summary>

```
/pbi:new
> year-to-date revenue filtered to the selected region, in the Sales table
```
Generates the DAX, format string, display folder, and description — writes to PBIP if detected.
</details>

<details>
<summary><strong>Audit your model</strong></summary>

```
/pbi:audit
```
8 domain passes: relationships, naming, date table, measure quality, hidden columns, report layer, advanced features, performance. Severity-graded report with auto-fix.
</details>

<details>
<summary><strong>Edit with plain language</strong></summary>

```
/pbi:edit
> rename [Total Sales] to [Revenue] in the Sales table
```
Finds the measure, applies the change, auto-commits.
</details>

<details>
<summary><strong>Bulk format all measures</strong></summary>

```
/pbi:format-batch
```
Applies SQLBI-standard formatting (VAR/RETURN blocks, CALCULATE structure, keyword capitalisation) to every measure in the model in a single pass. No DAX Formatter API required. Auto-commits.
</details>

<details>
<summary><strong>Deep mode</strong></summary>

```
/pbi:deep
```
Four-phase guided workflow with hard gates: business context intake, model review, DAX development, final verification.
</details>

<details>
<summary><strong>Version control</strong></summary>

```
/pbi:diff        # what changed since last commit
/pbi:commit      # auto-generated business-language commit
/pbi:undo        # revert the last auto-commit
/pbi:changelog   # generate CHANGELOG.md from history
```
All commits are local only.
</details>

---

## Requirements

- [**Claude Code**](https://docs.anthropic.com/en/claude-code) CLI
- A Claude account (claude.ai or API key)
- For PBIP commands: a project in [PBIP format](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)

---

## Roadmap

- [x] Paste-in DAX commands (explain, format, optimise, comment, error)
- [x] PBIP file I/O (load, audit, diff, commit, edit, undo)
- [x] Measure scaffolding, batch commenting, audit auto-fix, changelog
- [x] Single-skill router, one-liner install, parallel audit agents
- [x] Auto-resume context, local-first git, expanded audit rules
- [x] Deep mode workflow, project extraction (3 tiers)
- [x] Python-first UTF-8, `/pbi:docs`, context tracking
- [x] Installer overhaul, token safety, `/pbi:version`
- [x] Sub-skill architecture — each command is its own `/pbi:<cmd>` skill
- [x] Session resume, visual branding, rich command descriptions
- [x] Session-aware auto-load, `.pbi/` context directory
- [x] `/pbi:settings` write-mode toggle, `/pbi:format-batch` bulk formatter
- [ ] Cross-measure dependency graph
- [ ] Side-by-side measure comparison
- [ ] Calculated column support
- [ ] Power Query error diagnosis

---

## License

MIT

---

<p align="center">
  <sub>Built for Power BI developers who live in the terminal.</sub>
</p>
