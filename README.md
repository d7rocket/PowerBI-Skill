<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-Skill-blueviolet?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMiAxNWwtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPjwvc3ZnPg==" alt="Claude Code Skill">
  <img src="https://img.shields.io/badge/version-4.1-blue?style=for-the-badge" alt="Version 4.1">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Power_BI-DAX-F2C811?style=for-the-badge&logo=powerbi&logoColor=black" alt="Power BI DAX">
</p>

<div align="center">

```
  ██████╗ ██████╗ ██╗
  ██╔══██╗██╔══██╗██║
  ██████╔╝██████╔╝██║   Power BI DAX Co-pilot
  ██╔═══╝ ██╔══██╗██║   for Claude Code
  ██║     ██████╔╝██║
  ╚═╝     ╚═════╝ ╚═╝   v4.1
```

</div>

<p align="center">
  <strong>Explain, format, optimise, audit, and edit DAX measures — directly from your terminal.</strong><br>
  Works with pasted DAX <em>and</em> with Power BI Project (PBIP) files on disk.
</p>

---

## What's New in v4.1

- **Auto-resume** — context loads automatically on every `/pbi` invocation. No more running `/pbi load` first.
- **Local-first git** — all commits stay local. The skill will never pull, push, or create PRs. Your files are always the source of truth.
- **13 optimisation rules** — added SUMMARIZE deprecation, FILTER(RELATEDTABLE) detection, and semi-additive pattern opportunities.
- **Expanded audit** — new rules for calculation groups, field parameters, aggregation tables, and high-cardinality columns. Bidirectional fix now asks which direction to keep.
- **BLANK propagation diagnosis** — `/pbi error` now catches implicit BLANK propagation issues.
- **Anti-patterns on every command** — all 17 commands now have explicit anti-pattern guards.
- **Input validation** — empty paste guards on all paste-in commands, malformed file guards on load/audit.

---

## What can it do?

<table>
<tr>
<td width="50%" valign="top">

### Paste-in Commands
*Work anywhere — just paste your DAX*

| Command | Description |
|:--------|:------------|
| `/pbi explain` | Plain-English breakdown of any DAX measure |
| `/pbi format` | Auto-format via DAX Formatter API |
| `/pbi optimise` | 13-rule performance scan with side-by-side diff |
| `/pbi comment` | Add inline `//` comments + description field |
| `/pbi error` | Diagnose Power BI error messages (7 categories) |
| `/pbi new` | Scaffold a measure from plain English |

</td>
<td width="50%" valign="top">

### PBIP Project Commands
*Auto-detected when `*.SemanticModel/` exists*

| Command | Description |
|:--------|:------------|
| `/pbi load` | Index your model (tables, measures, columns) |
| `/pbi audit` | Full model health scan with auto-fix (19 rules) |
| `/pbi edit` | Change your model with plain language |
| `/pbi diff` | Human-readable change summary |
| `/pbi commit` | Auto-generated business-language commits |
| `/pbi undo` | Revert the last auto-commit |
| `/pbi comment-batch` | Comment every measure in a table |
| `/pbi changelog` | Generate CHANGELOG from git history |
| `/pbi extract` | Export project documentation (3 tiers) |

</td>
</tr>
</table>

### Workflow Commands

| Command | Description |
|:--------|:------------|
| `/pbi deep` | Guided multi-phase workflow: intake → model review → DAX development → verification |
| `/pbi help` | Command reference with version check |

---

## Installation

Pick whichever method works for you. All four get you the same result: the `/pbi` skill ready to use in Claude Code.

### Option 1 — One-liner install (macOS / Linux / WSL)

```bash
curl -sL https://raw.githubusercontent.com/deveshd7/PowerBI-Skill/main/install.sh | bash
```

To install into a specific project folder:

```bash
curl -sL https://raw.githubusercontent.com/deveshd7/PowerBI-Skill/main/install.sh | bash -s -- /path/to/your/project
```

### Option 2 — PowerShell install (Windows)

```powershell
irm https://raw.githubusercontent.com/deveshd7/PowerBI-Skill/main/install.ps1 | iex
```

To install into a specific project folder:

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/deveshd7/PowerBI-Skill/main/install.ps1))) -Target "C:\path\to\your\project"
```

### Option 3 — Manual download (any OS)

1. Go to the [**Releases page**](https://github.com/deveshd7/PowerBI-Skill/releases) or click **Code > Download ZIP** on the repo
2. Extract the ZIP
3. Copy the `.claude` folder into your project root:

```
your-project/
  .claude/
    skills/
      pbi/
        SKILL.md
        commands/
        shared/
  ... your other files
```

That's it. Claude Code auto-discovers skills in `.claude/skills/`.

### Option 4 — Git clone

```bash
git clone https://github.com/deveshd7/PowerBI-Skill.git
cd PowerBI-Skill
claude
```

Or clone and copy just the skill into an existing project:

```bash
git clone https://github.com/deveshd7/PowerBI-Skill.git /tmp/pbi-skill
cp -r /tmp/pbi-skill/.claude your-project/.claude
```

---

## Getting Started

**1.** Open Claude Code in your project directory

**2.** Type `/pbi` — you'll see the command menu

**3.** Try it out:

```
/pbi explain

> Revenue YTD = CALCULATE([Revenue], DATESYTD('Date'[Date]))
```

Claude will break down exactly what the measure does — filter context, row context, context transitions, and performance notes.

**4.** If you're in a PBIP project folder, context loads automatically — no setup needed.

---

## How It Works

| Mode | When | What happens |
|:-----|:-----|:-------------|
| **Paste-in** | No PBIP project | Paste DAX into chat, get results back |
| **File mode** | `*.SemanticModel/` detected | Reads/writes TMDL or TMSL files directly, auto-commits changes |

### Auto-Resume

Every `/pbi` invocation automatically loads your project context. If `.pbi-context.md` has model context from a prior session, it's resumed instantly. If not, the skill auto-runs a lightweight load. No explicit `/pbi load` required.

### Local-First Git

All git operations are strictly local. The skill will **never** run `git pull`, `git push`, `git fetch`, or create pull requests. Your local files are always the source of truth. If you want to sync with a remote, you do it yourself outside the skill.

### Session Memory

Every command reads and writes `.pbi-context.md` at your project root. This gives Claude persistent memory across commands:

- **Last command** and its outcome
- **Command history** (rolling 20 entries)
- **Model context** — tables, measures, columns, relationships
- **Analyst-reported failures** — flag approaches that didn't work so Claude avoids repeating them

### Smart Model Routing

DAX reasoning commands run on **Sonnet** for analytical depth. File-heavy commands (load, diff, commit, undo, changelog) dispatch to **Haiku** agents for speed and lower cost. Deep extraction uses **Opus** for comprehensive analysis.

---

## Examples

<details>
<summary><strong>Explain a measure</strong></summary>

```
/pbi explain
```
Paste your DAX and get a structured breakdown — what it calculates, how filter context flows, and any performance considerations.
</details>

<details>
<summary><strong>Scaffold a new measure</strong></summary>

```
/pbi new
> year-to-date revenue filtered to the selected region, in the Sales table
```
Generates the DAX expression, format string, display folder, and description — and writes it to your PBIP files if a project is detected.
</details>

<details>
<summary><strong>Audit your model</strong></summary>

```
/pbi audit
```
Runs 8 domain passes across your model: relationships, naming conventions, date table, measure quality, hidden column hygiene, report layer, advanced features, and performance heuristics. Outputs a severity-graded report and offers to auto-fix issues.
</details>

<details>
<summary><strong>Edit with plain language</strong></summary>

```
/pbi edit
> rename [Total Sales] to [Revenue] in the Sales table
```
Claude finds the measure in your TMDL/TMSL files, applies the change, and auto-commits.
</details>

<details>
<summary><strong>Format + Optimise</strong></summary>

```
/pbi format     # formats via DAX Formatter API
/pbi optimise   # checks 13 performance rules, shows before/after
```
</details>

<details>
<summary><strong>Deep mode</strong></summary>

```
/pbi deep
```
Guided multi-phase workflow: gathers business context, reviews your model for structural issues, then enters DAX development with full context awareness. Phase gates prevent skipping steps.
</details>

<details>
<summary><strong>Version control</strong></summary>

```
/pbi diff        # what changed since last commit
/pbi commit      # auto-generated business-language commit message
/pbi undo        # revert the last auto-commit
/pbi changelog   # generate CHANGELOG.md from git history
```
All commits are local only — the skill never pushes to a remote.
</details>

---

## Requirements

- [**Claude Code**](https://docs.anthropic.com/en/claude-code) CLI installed
- A Claude account (claude.ai or API key)
- For PBIP commands: a Power BI project saved in [PBIP format](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)

---

## Roadmap

- [x] Paste-in DAX commands — explain, format, optimise, comment, error
- [x] PBIP file I/O — load, audit, diff, commit, edit, undo
- [x] New measure scaffolding, batch commenting, audit auto-fix, changelog
- [x] Single-skill architecture, one-liner install, parallel audit agents
- [x] Auto-resume context, local-first git, expanded audit rules
- [x] Deep mode guided workflow, project extraction (3 tiers)
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
