param(
    [ValidateSet("project","user")]
    [string]$Scope = "user"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

if ($Scope -eq "user") {
    $userHome = $env:USERPROFILE
    if (-not $userHome) { $userHome = $HOME }
    $skillBase = Join-Path $userHome ".claude\skills\pbi"
} else {
    $skillBase = Join-Path (Get-Location) ".claude\skills\pbi"
}
$scriptsDir = Join-Path $skillBase "scripts"
$sharedDir  = Join-Path $skillBase "shared"

# Commands directory — always user-level for discoverability
$userHome2 = $env:USERPROFILE
if (-not $userHome2) { $userHome2 = $HOME }
$cmdsDir = Join-Path $userHome2 ".claude\commands\pbi"

$base = "https://raw.githubusercontent.com/d7rocket/PowerBI-Skill/main"
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

New-Item -ItemType Directory -Force -Path $scriptsDir | Out-Null
New-Item -ItemType Directory -Force -Path $sharedDir  | Out-Null

# ── Clean up old commands/ directory if upgrading from v4 ──────────
$oldCmdsDir = Join-Path $skillBase "commands"
if (Test-Path $oldCmdsDir) {
    Write-Host "  Removing old commands/ directory (v4 -> v5 migration)..." -ForegroundColor DarkGray
    Remove-Item -Recurse -Force $oldCmdsDir
}

# ── Download base skill ────────────────────────────────────────────
Write-Host "  [1/5] Base skill" -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "$base/.claude/skills/pbi/SKILL.md" -OutFile (Join-Path $skillBase "SKILL.md") -UseBasicParsing
    Write-Host "        SKILL.md" -ForegroundColor DarkGray
} catch {
    Write-Host "        SKILL.md — FAILED" -ForegroundColor Red
    Write-Host "  Cannot continue without the base skill. Check your network." -ForegroundColor Red
    exit 1
}

# Read version from downloaded SKILL.md (parses "  version: X.Y.Z" under metadata:)
$versionLine = Get-Content (Join-Path $skillBase "SKILL.md") | Where-Object { $_ -match '^\s+version:' } | Select-Object -First 1
$version = "unknown"
if ($versionLine) { $version = ($versionLine -split ':\s+')[1].Trim() }

# ── Download sub-skills ────────────────────────────────────────────
Write-Host "  [2/5] Sub-skills" -ForegroundColor Cyan
$commands = @(
    "explain","format","optimise","comment","error","new",
    "load","audit","diff","commit","edit","undo",
    "comment-batch","changelog","extract","deep","docs","help","version","resume"
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
    $cmdDir = Join-Path $skillBase $cmd
    New-Item -ItemType Directory -Force -Path $cmdDir | Out-Null
    try {
        Invoke-WebRequest -Uri "$base/.claude/skills/pbi/$cmd/SKILL.md" -OutFile (Join-Path $cmdDir "SKILL.md") -UseBasicParsing
    } catch {
        $failed += $cmd
    }
}
Write-Host "`r        $($([string][char]9608) * 20) done — $total sub-skills     "

# ── Download scripts ───────────────────────────────────────────────
Write-Host "  [3/5] Scripts" -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "$base/.claude/skills/pbi/scripts/detect.py" -OutFile (Join-Path $scriptsDir "detect.py") -UseBasicParsing
    Write-Host "        detect.py" -ForegroundColor DarkGray
} catch {
    Write-Host "        detect.py — FAILED" -ForegroundColor Red
    Write-Host "  Cannot continue without detect.py. Check your network." -ForegroundColor Red
    exit 1
}

# ── Download commands (for /pbi:cmd discovery) ────────────────────
Write-Host "  [4/5] Commands" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $cmdsDir | Out-Null
$i2 = 0
$failed2 = @()
foreach ($cmd in $commands) {
    $i2++
    $pct2 = [math]::Round(($i2 / $total) * 100)
    $filled2 = [math]::Floor($pct2 / 5)
    $bar2 = ([string][char]9608) * $filled2 + ([string][char]9617) * (20 - $filled2)
    Write-Host "`r        $bar2 $pct2%%  " -NoNewline
    try {
        Invoke-WebRequest -Uri "$base/.claude/commands/pbi/$cmd.md" -OutFile (Join-Path $cmdsDir "$cmd.md") -UseBasicParsing
    } catch {
        $failed2 += $cmd
    }
}
Write-Host "`r        $($([string][char]9608) * 20) done — $total commands     "
if ($failed2.Count -gt 0) { $failed += $failed2 }

# ── Download shared ────────────────────────────────────────────────
Write-Host "  [5/5] Shared resources" -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri "$base/.claude/skills/pbi/shared/api-notes.md" -OutFile (Join-Path $sharedDir "api-notes.md") -UseBasicParsing
    Write-Host "        api-notes.md" -ForegroundColor DarkGray
} catch {
    Write-Host "        api-notes.md — skipped (non-critical)" -ForegroundColor Yellow
}
try {
    Invoke-WebRequest -Uri "$base/.claude/skills/pbi/shared/CHANGELOG.md" -OutFile (Join-Path $sharedDir "CHANGELOG.md") -UseBasicParsing
    Write-Host "        CHANGELOG.md" -ForegroundColor DarkGray
} catch {
    Write-Host "        CHANGELOG.md — skipped (non-critical)" -ForegroundColor Yellow
}
try {
    Invoke-WebRequest -Uri "$base/.claude/skills/pbi/shared/ui-brand.md" -OutFile (Join-Path $sharedDir "ui-brand.md") -UseBasicParsing
    Write-Host "        ui-brand.md" -ForegroundColor DarkGray
} catch {
    Write-Host "        ui-brand.md — skipped (non-critical)" -ForegroundColor Yellow
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
Write-Host "  ║  Open Claude Code and type /pbi:help      ║" -ForegroundColor Green
Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Installed to: $resolved" -ForegroundColor DarkGray
Write-Host ""
