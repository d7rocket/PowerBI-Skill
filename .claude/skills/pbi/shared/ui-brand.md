# PBI Skill — Visual Output Standards

Reference for consistent visual output across all `/pbi:` commands.

## Stage Banners

Use at the start of major command outputs (resume, audit report, deep mode phases):

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PBI ► {STAGE NAME}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

- Width: 62 characters
- Prefix: `PBI ►`
- Stage name: UPPERCASE
- Borders: `━` (box drawing heavy horizontal, U+2501)

## Status Symbols

Use ONLY these symbols in command output:

| Symbol | Meaning | Usage |
|--------|---------|-------|
| ✓ | Success / complete | After successful operations |
| ✗ | Failed / error | After failed operations |
| ◆ | Active / in-progress | Current step in multi-step output |
| ○ | Pending / not started | Upcoming steps |
| ⚠ | Warning | Non-critical issues |

**Do NOT use** random emoji (🚀, ✨, 💫, 🎯, 💡, etc.) anywhere in output.

## Severity Tags

For audit findings, error diagnosis, and model checks:

| Tag | Usage |
|-----|-------|
| `CRITICAL` | Must fix — breaks model correctness or query results |
| `WARN` | Should fix — degrades quality, UX, or performance |
| `INFO` | Advisory — awareness only, no action required |

## Next Steps Block

Every command output ends with a `Next steps` line showing 3–5 contextually relevant commands:

```
**Next steps:** `/pbi:format` · `/pbi:optimise` · `/pbi:comment`
```

- Separator: ` · ` (space-middle-dot-space)
- Commands as inline code backticks
- Choose commands relevant to the current output (don't repeat the command just run)

## Progress Display

For batch operations (comment-batch, audit parallel agents):

```
Processing: ████████████░░░░░░░░ 60%  (6/10 tables)
```

- Bar width: 20 characters
- Filled: `█` (U+2588), Empty: `░` (U+2591)
- Show percentage AND count


## Anti-Patterns

- Varying banner widths (always 62 chars)
- Mixing banner border styles (`===`, `---`, `***` — always use `━`)
- Skipping `PBI ►` prefix in banners
- Random emoji anywhere in output
- Missing Next Steps block after command completion
- Using status symbols not in the approved set above
- Inconsistent separator styles (mixing ` · ` with `, ` or ` | `)
