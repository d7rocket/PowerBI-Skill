#!/usr/bin/env bash
set -e

TARGET="${1:-.}"
VERSION="5.0.0"
BASE="https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main"
SKILL_DIR="$TARGET/.claude/skills/pbi"

IS_UPDATE=false
[ -d "$SKILL_DIR" ] && IS_UPDATE=true

# ── Colors ──────────────────────────────────────────────────────────
YELLOW='\033[1;33m'
DIM='\033[0;33m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
GRAY='\033[0;90m'
RESET='\033[0m'

# ── Banner ──────────────────────────────────────────────────────────
echo ""
echo -e "${DIM}  ╔═════════════════════════════════════════════════════════╗${RESET}"
echo -e "${DIM}  ║                                                         ║${RESET}"
echo -e "${YELLOW}  ║   ██████╗ ██████╗ ██╗                                   ${DIM}║${RESET}"
echo -e "${YELLOW}  ║   ██╔══██╗██╔══██╗██║                                   ${DIM}║${RESET}"
echo -e "${YELLOW}  ║   ██████╔╝██████╔╝██║     ${DIM}Power BI DAX Co-pilot         ║${RESET}"
echo -e "${YELLOW}  ║   ██╔═══╝ ██╔══██╗██║     ${DIM}for Claude Code               ║${RESET}"
echo -e "${YELLOW}  ║   ██║     ██████╔╝██║                                   ${DIM}║${RESET}"
echo -e "${DIM}  ║   ╚═╝     ╚═════╝ ╚═╝                        v${VERSION}  ║${RESET}"
echo -e "${DIM}  ║                                                         ║${RESET}"
echo -e "${DIM}  ╚═════════════════════════════════════════════════════════╝${RESET}"
echo ""

if $IS_UPDATE; then
    echo -e "${GRAY}  Updating existing installation...${RESET}"
else
    echo -e "${GRAY}  Fresh install — setting up skill directory...${RESET}"
fi
echo ""

# ── Pre-flight ──────────────────────────────────────────────────────
if ! command -v curl &>/dev/null; then
    echo -e "${RED}  Error: curl is required but not found. Install curl and try again.${RESET}"
    exit 1
fi

if ! curl -s --head --connect-timeout 5 "https://raw.githubusercontent.com" >/dev/null 2>&1; then
    echo -e "${RED}  Error: Cannot reach GitHub. Check your internet connection.${RESET}"
    exit 1
fi

mkdir -p "$SKILL_DIR/scripts" "$SKILL_DIR/shared"

# ── Clean up old commands/ directory if upgrading from v4 ──────────
if [ -d "$SKILL_DIR/commands" ]; then
    echo -e "${GRAY}  Removing old commands/ directory (v4 → v5 migration)...${RESET}"
    rm -rf "$SKILL_DIR/commands"
fi

# ── Download base skill ────────────────────────────────────────────
echo -e "${CYAN}  [1/5] Base skill${RESET}"
if curl -sL "$BASE/.claude/skills/pbi/SKILL.md" -o "$SKILL_DIR/SKILL.md" 2>/dev/null; then
    echo -e "${GRAY}        SKILL.md${RESET}"
else
    echo -e "${RED}        SKILL.md — FAILED${RESET}"
    echo -e "${RED}  Cannot continue without the base skill. Check your network.${RESET}"
    exit 1
fi

# ── Download sub-skills ────────────────────────────────────────────
echo -e "${CYAN}  [2/5] Sub-skills${RESET}"
commands=(explain format optimise comment error new load audit diff commit edit undo comment-batch changelog extract deep docs help version)
total=${#commands[@]}
i=0
failed=()
for cmd in "${commands[@]}"; do
    i=$((i + 1))
    pct=$((i * 100 / total))
    filled=$((pct / 5))
    bar=""
    for ((f=0; f<filled; f++)); do bar="${bar}█"; done
    for ((e=0; e<20-filled; e++)); do bar="${bar}░"; done
    printf "\r        %s %d%%  " "$bar" "$pct"
    mkdir -p "$SKILL_DIR/$cmd"
    if ! curl -sL "$BASE/.claude/skills/pbi/$cmd/SKILL.md" -o "$SKILL_DIR/$cmd/SKILL.md" 2>/dev/null; then
        failed+=("$cmd")
    fi
done
printf "\r        ████████████████████ done — %d sub-skills     \n" "$total"

# ── Download commands (for /pbi:cmd discovery) ────────────────────
echo -e "${CYAN}  [3/5] Commands${RESET}"
CMDS_DIR="$HOME/.claude/commands/pbi"
mkdir -p "$CMDS_DIR"
i=0
for cmd in "${commands[@]}"; do
    i=$((i + 1))
    pct=$((i * 100 / total))
    filled=$((pct / 5))
    bar=""
    for ((f=0; f<filled; f++)); do bar="${bar}█"; done
    for ((e=0; e<20-filled; e++)); do bar="${bar}░"; done
    printf "\r        %s %d%%  " "$bar" "$pct"
    if ! curl -sL "$BASE/.claude/commands/pbi/$cmd.md" -o "$CMDS_DIR/$cmd.md" 2>/dev/null; then
        failed+=("$cmd")
    fi
done
printf "\r        ████████████████████ done — %d commands     \n" "$total"

# ── Download scripts ───────────────────────────────────────────────
echo -e "${CYAN}  [4/5] Scripts${RESET}"
if curl -sL "$BASE/.claude/skills/pbi/scripts/detect.py" -o "$SKILL_DIR/scripts/detect.py" 2>/dev/null; then
    echo -e "${GRAY}        detect.py${RESET}"
else
    echo -e "${RED}        detect.py — FAILED${RESET}"
    echo -e "${RED}  Cannot continue without detect.py. Check your network.${RESET}"
    exit 1
fi

# ── Download shared ────────────────────────────────────────────────
echo -e "${CYAN}  [5/5] Shared resources${RESET}"
if curl -sL "$BASE/.claude/skills/pbi/shared/api-notes.md" -o "$SKILL_DIR/shared/api-notes.md" 2>/dev/null; then
    echo -e "${GRAY}        api-notes.md${RESET}"
else
    echo -e "${YELLOW}        api-notes.md — skipped (non-critical)${RESET}"
fi
if curl -sL "$BASE/.claude/skills/pbi/shared/CHANGELOG.md" -o "$SKILL_DIR/shared/CHANGELOG.md" 2>/dev/null; then
    echo -e "${GRAY}        CHANGELOG.md${RESET}"
else
    echo -e "${YELLOW}        CHANGELOG.md — skipped (non-critical)${RESET}"
fi

# ── Verify ──────────────────────────────────────────────────────────
file_count=$(find "$SKILL_DIR" -type f | wc -l | tr -d ' ')
resolved=$(cd "$SKILL_DIR" && pwd)

echo ""
if [ ${#failed[@]} -gt 0 ]; then
    echo -e "${YELLOW}  Warning: Failed to download: ${failed[*]}${RESET}"
    echo -e "${YELLOW}  Re-run the installer to retry.${RESET}"
    echo ""
fi

# ── Summary ─────────────────────────────────────────────────────────
echo -e "${GREEN}  ╔══════════════════════════════════════════╗${RESET}"
if $IS_UPDATE; then
    echo -e "${GREEN}  ║  Update complete                         ║${RESET}"
else
    echo -e "${GREEN}  ║  Installation complete                    ║${RESET}"
fi
echo -e "${GREEN}  ║                                          ║${RESET}"
echo -e "${GREEN}  ║  ${file_count} files installed                       ║${RESET}"
echo -e "${GREEN}  ║  Version ${VERSION}                          ║${RESET}"
echo -e "${GREEN}  ║                                          ║${RESET}"
echo -e "${GREEN}  ║  Open Claude Code and type /pbi:help      ║${RESET}"
echo -e "${GREEN}  ╚══════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${GRAY}  Installed to: $resolved${RESET}"
echo ""
