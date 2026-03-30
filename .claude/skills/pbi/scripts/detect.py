#!/usr/bin/env python3
"""Detection and search utilities for /pbi skill. UTF-8 safe.

Usage:
    python detect.py pbip      — Detect PBIP SemanticModel folder and format
    python detect.py files     — List all TMDL files or model.bim path
    python detect.py pbir      — Detect PBIR Report folder and list visual JSONs
    python detect.py git       — Check git state (repo exists, has commits)
    python detect.py context   — Read last 80 lines of .pbi-context.md
    python detect.py nearby    — Check parent directories for a PBIP project
    python detect.py search <name> <pbip_dir>  — Find files containing measure name
    python detect.py html-parse <tmpfile>  — Strip DAX Formatter HTML to clean DAX text
    python detect.py version-check <skill_file>  — Read version from SKILL.md frontmatter
    python detect.py gitignore-check  — Ensure .gitignore contains all noise-file entries
    python detect.py session-check  — Check if model was loaded this session (2h window)
"""
import sys
import os
import glob
import subprocess

# Force UTF-8 output (Windows defaults to cp1252 which breaks French accents)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def detect_pbip():
    """Detect PBIP SemanticModel folder and format."""
    dirs = glob.glob('*.SemanticModel') + glob.glob('.SemanticModel')
    if dirs:
        sm = dirs[0]
        if os.path.isfile(os.path.join(sm, 'model.bim')):
            print('PBIP_MODE=file PBIP_FORMAT=tmsl PBIP_DIR=' + sm)
        elif os.path.isdir(os.path.join(sm, 'definition', 'tables')):
            print('PBIP_MODE=file PBIP_FORMAT=tmdl PBIP_DIR=' + sm)
        else:
            print('PBIP_MODE=file PBIP_FORMAT=tmdl PBIP_DIR=' + sm)
    else:
        print('PBIP_MODE=paste')


def detect_files():
    """List all TMDL files or model.bim path."""
    dirs = glob.glob('*.SemanticModel') + glob.glob('.SemanticModel')
    if not dirs:
        return
    sm = dirs[0]
    tbl = os.path.join(sm, 'definition', 'tables')
    bim = os.path.join(sm, 'model.bim')
    if os.path.isdir(tbl):
        for f in sorted(glob.glob(os.path.join(tbl, '**', '*.tmdl'), recursive=True)):
            print(f)
    elif os.path.isfile(bim):
        print('tmsl:' + bim)


def detect_pbir():
    """Detect PBIR Report folder and list visual JSON files."""
    dirs = glob.glob('*.Report') + glob.glob('.Report')
    if dirs:
        rpt = dirs[0]
        count = 0
        for root, _, files in os.walk(rpt):
            for f in sorted(files):
                if f.endswith('.json') and f not in ('item.config.json', 'item.metadata.json'):
                    if count < 20:
                        print(os.path.join(root, f))
                    count += 1
        print('PBIR=yes PBIR_DIR=' + rpt)
    else:
        print('PBIR=no')


def detect_git():
    """Check git state: repo exists and has commits."""
    try:
        subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True, check=True, timeout=5
        )
        print('GIT=yes')
        try:
            subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, check=True, timeout=5
            )
            print('HAS_COMMITS=yes')
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print('HAS_COMMITS=no')
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        print('GIT=no')
        print('HAS_COMMITS=no')


def detect_context():
    """Read last 80 lines of .pbi-context.md (UTF-8 safe)."""
    try:
        with open('.pbi-context.md', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-80:]:
                print(line, end='')
    except FileNotFoundError:
        print('No prior context found.')


def detect_nearby():
    """Check parent directories for a PBIP project."""
    for d in ['..', os.path.join('..', '..'), os.path.join('..', '..', '..')]:
        sm = glob.glob(os.path.join(d, '*.SemanticModel')) + \
             glob.glob(os.path.join(d, '.SemanticModel'))
        if sm:
            print('NEARBY_PBIP=' + os.path.abspath(d))
            return
    print('NEARBY_PBIP=')


def search_measure(name, pbip_dir):
    """Fixed-string search for measure name in model files. UTF-8 safe.

    Replaces grep -rlF for correct handling of accented characters
    (French: e with accent, c cedilla, etc.) and regex metacharacters in names.
    """
    tbl = os.path.join(pbip_dir, 'definition', 'tables')
    if os.path.isdir(tbl):
        for f in glob.glob(os.path.join(tbl, '**', '*.tmdl'), recursive=True):
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    if name in fh.read():
                        print(f)
            except (UnicodeDecodeError, OSError):
                pass
    bim = os.path.join(pbip_dir, 'model.bim')
    if os.path.isfile(bim):
        try:
            with open(bim, 'r', encoding='utf-8') as fh:
                if name in fh.read():
                    print(bim)
        except (UnicodeDecodeError, OSError):
            pass


def html_parse(tmpfile):
    """Strip DAX Formatter HTML response to clean DAX text.

    Replicates the grep/sed pipeline from format.md:
      grep -o '<div class="formatted"[^>]*>.*</div>'
      sed strip div tags, <br>->newline, strip spans, &nbsp;->space
    UTF-8 safe — handles accented DAX identifiers.
    """
    import re
    try:
        with open(tmpfile, 'r', encoding='utf-8') as f:
            html = f.read()
    except (OSError, IOError):
        return  # Silent — format.md API_FAIL branch handles empty output

    # Extract content inside <div class="formatted"...>...</div>
    m = re.search(r'<div class="formatted"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not m:
        return  # Silent empty — triggers API_FAIL fallback in format.md

    text = m.group(1)
    # Replace <br> with newlines
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    # Strip all span tags (opening and closing)
    text = re.sub(r'<span[^>]*>', '', text)
    text = re.sub(r'</span>', '', text)
    # Convert &nbsp; to regular space
    text = text.replace('&nbsp;', ' ')
    # Strip the outer div tags (already extracted via group(1), but clean residual tags)
    text = re.sub(r'<[^>]+>', '', text)
    # Print each line stripped of trailing whitespace
    for line in text.split('\n'):
        print(line.rstrip())


def version_check(skill_file):
    """Read version from SKILL.md YAML frontmatter.

    Replaces: grep -m1 '^version:' "$SKILL_FILE" | sed 's/version: *//'
    Handles both top-level 'version:' and indented 'version:' (e.g., under metadata:).
    Prints: LOCAL=<version>
    """
    try:
        with open(skill_file, 'r', encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith('version:'):
                    ver = stripped[len('version:'):].strip()
                    print('LOCAL=' + ver)
                    return
    except (OSError, IOError):
        pass
    print('LOCAL=unknown')



def session_check():
    """Check if model context was loaded this session.

    Reads ## Session Start from .pbi-context.md, compares timestamp
    to current time. If within 2 hours, outputs SESSION=active.
    Otherwise outputs SESSION=new.
    """
    from datetime import datetime, timezone, timedelta
    try:
        with open('.pbi-context.md', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('**Session-Start:**'):
                    ts_str = line.strip().split('**Session-Start:**')[1].strip()
                    try:
                        loaded = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                        now = datetime.now(timezone.utc)
                        if now - loaded < timedelta(hours=2):
                            print('SESSION=active')
                            return
                    except (ValueError, IndexError):
                        pass
    except FileNotFoundError:
        pass
    print('SESSION=new')


def gitignore_check():
    """Ensure four noise-file entries exist in .gitignore.

    Replaces grep/append pipeline in diff.md Step 1.
    Entries required: *.abf, localSettings.json, .pbi-context.md, SecurityBindings
    Prints GITIGNORE_OK when done.
    """
    required = ['*.abf', 'localSettings.json', '.pbi-context.md', 'SecurityBindings']
    existing_lines = []
    try:
        with open('.gitignore', 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()
    except FileNotFoundError:
        pass  # Will create below

    existing_text = ''.join(existing_lines)
    to_add = []
    for entry in required:
        # Match *.abf also catches cache.abf since we add *.abf
        if entry not in existing_text:
            to_add.append(entry)

    if to_add:
        with open('.gitignore', 'a', encoding='utf-8') as f:
            for entry in to_add:
                f.write(entry + '\n')

    print('GITIGNORE_OK')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: detect.py [pbip|files|pbir|git|context|nearby|search]', file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == 'pbip':
        detect_pbip()
    elif cmd == 'files':
        detect_files()
    elif cmd == 'pbir':
        detect_pbir()
    elif cmd == 'git':
        detect_git()
    elif cmd == 'context':
        detect_context()
    elif cmd == 'nearby':
        detect_nearby()
    elif cmd == 'search' and len(sys.argv) >= 4:
        search_measure(sys.argv[2], sys.argv[3])
    elif cmd == 'html-parse' and len(sys.argv) >= 3:
        html_parse(sys.argv[2])
    elif cmd == 'version-check' and len(sys.argv) >= 3:
        version_check(sys.argv[2])
    elif cmd == 'session-check':
        session_check()
    elif cmd == 'gitignore-check':
        gitignore_check()
    else:
        print('Unknown command: ' + cmd, file=sys.stderr)
        sys.exit(1)
