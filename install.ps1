param(
    [ValidateSet("project","user")]
    [string]$Scope = "user"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

if ($Scope -eq "user") {
    $skillBase = Join-Path ($env:USERPROFILE ?? $HOME) ".claude\skills\pbi"
} else {
    $skillBase = Join-Path (Get-Location) ".claude\skills\pbi"
}
$cmdsDir    = Join-Path $skillBase "commands"
$scriptsDir = Join-Path $skillBase "scripts"
$sharedDir  = Join-Path $skillBase "shared"

$base = "https://raw.githubusercontent.com/d7rocket/PBI-SKILL/main"
$isUpdate = Test-Path $skillBase

# ── Banner ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ╔═════════════════════════════════════════════════════════╗" -ForegroundColor DarkYellow
Write-Host "  ║                                                         ║" -ForegroundColor DarkYellow
Write-Host "  ║   ██████╗ ██████╗ ██╗                                   ║" -ForegroundColor Yellow
Write-Host "  ║   ██╔══██╗██╔══██╗██║                                   ║" -ForegroundColor Yellow
Write-Host "  ║   ██████╔╝██████╔╝██║     Power BI DAX Co-pilot         ║" -ForegroundColor Yellow
Write-Host "  ║   ██╔═══╝ ██╔══██╗██║     for Claude Code               ║" -ForegroundColor Yellow
Write-Host "  ║   ██║     ██████╔╝██║                                   ║" -ForegroundColor Yellow
Write-Host "  ║   ╚═╝     ╚═════╝ ╚═╝                                  ║" -ForegroundColor DarkYellow
Write-Host "  ║                                                         ║" -ForegroundColor DarkYellow
Write-Host "  ╚═════════════════════════════════════════════════════════╝" -ForegroundColor DarkYellow
Write-Host ""

if ($isUpdate) {
    Write-Host "  Updating existing installation..." -ForegroundColor DarkGray
} else {
    Write-Host "  Fresh install — setting up skill directory..." -ForegroundColor DarkGray
}
Write-Host ""

# ── Pre-flight ──────────────────────────────────────────────────────
try {
    $null = Invoke-WebRequest -Uri "https://raw.githubusercontent.com" -UseBasicParsing -TimeoutSec 5 -Method Head
} catch {
    Write-Host "  Error: Cannot reach GitHub. Check your internet connection." -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Force -Path $cmdsDir    | Out-Null
New-Item -ItemType Directory -Force -Path $scriptsDir | Out-Null
New-Item -ItemType Directory -Force -Path $sharedDir  | Out-Null

# ── Download router ─────────────────────────────────────────────────
Write-Host "  [1/4] Skill router" -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "$base/.claude/skills/pbi/SKILL.md" -OutFile (Join-Path $skillBase "SKILL.md") -UseBasicParsing
    Write-Host "        SKILL.md" -ForegroundColor DarkGray
} catch {
    Write-Host "        SKILL.md — FAILED" -ForegroundColor Red
    Write-Host "  Cannot continue without the router. Check your network." -ForegroundColor Red
    exit 1
}

# Read version from downloaded SKILL.md (parses "  version: X.Y.Z" under metadata:)
$versionLine = Get-Content (Join-Path $skillBase "SKILL.md") | Where-Object { $_ -match '^\s+version:' } | Select-Object -First 1
$version = if ($versionLine) { ($versionLine -split ':\s+')[1].Trim() } else { "unknown" }

# ── Download commands ───────────────────────────────────────────────
Write-Host "  [2/4] Commands" -ForegroundColor Cyan
$commands = @(
    "explain","format","optimise","comment","error","new",
    "load","audit","diff","commit","edit","undo",
    "comment-batch","changelog","extract","deep","help","docs"
)
$total = $commands.Count
$i = 0
$failed = @()
foreach ($cmd in $commands) {
    $i++
    $pct = [math]::Round(($i / $total) * 100)
    $filled = [math]::Floor($pct / 5)
    $bar = ([string][char]9608) * $filled + ([string][char]9617) * (20 - $filled)
    Write-Host "`r        $bar $pct%%  " -NoNewline
    try {
        Invoke-WebRequest -Uri "$base/.claude/skills/pbi/commands/$cmd.md" -OutFile (Join-Path $cmdsDir "$cmd.md") -UseBasicParsing
    } catch {
        $failed += $cmd
    }
}
Write-Host "`r        $($([string][char]9608) * 20) done — $total commands     "

# ── Download scripts ────────────────────────────────────────────────
Write-Host "  [3/4] Scripts" -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "$base/.claude/skills/pbi/scripts/detect.py" -OutFile (Join-Path $scriptsDir "detect.py") -UseBasicParsing
    Write-Host "        detect.py" -ForegroundColor DarkGray
} catch {
    Write-Host "        detect.py — FAILED" -ForegroundColor Red
    Write-Host "  Cannot continue without detect.py. Check your network." -ForegroundColor Red
    exit 1
}

# ── Download shared ─────────────────────────────────────────────────
Write-Host "  [4/4] Shared resources" -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "$base/.claude/skills/pbi/shared/api-notes.md" -OutFile (Join-Path $sharedDir "api-notes.md") -UseBasicParsing
    Write-Host "        api-notes.md" -ForegroundColor DarkGray
} catch {
    Write-Host "        api-notes.md — skipped (non-critical)" -ForegroundColor Yellow
}

# ── Verify ──────────────────────────────────────────────────────────
$fileCount = (Get-ChildItem -Path $skillBase -Recurse -File).Count
$resolved = (Resolve-Path $skillBase).Path

Write-Host ""
if ($failed.Count -gt 0) {
    Write-Host "  Warning: Failed to download: $($failed -join ', ')" -ForegroundColor Yellow
    Write-Host "  Re-run the installer to retry." -ForegroundColor Yellow
    Write-Host ""
}

# ── Summary ─────────────────────────────────────────────────────────
Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Green
if ($isUpdate) {
    Write-Host "  ║  Update complete                         ║" -ForegroundColor Green
} else {
    Write-Host "  ║  Installation complete                    ║" -ForegroundColor Green
}
Write-Host "  ║                                          ║" -ForegroundColor Green
Write-Host "  ║  $fileCount files installed                       ║" -ForegroundColor Green
Write-Host "  ║  Version $version                          ║" -ForegroundColor Green
Write-Host "  ║  Scope: $Scope                             ║" -ForegroundColor Green
Write-Host "  ║                                          ║" -ForegroundColor Green
Write-Host "  ║  Open Claude Code and type /pbi           ║" -ForegroundColor Green
Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Installed to: $resolved" -ForegroundColor DarkGray
Write-Host ""
