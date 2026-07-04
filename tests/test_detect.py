#!/usr/bin/env python3
"""Tests for .claude/skills/pbi/scripts/detect.py.

Runnable two ways:
    pytest tests/test_detect.py
    python tests/test_detect.py

Each test invokes detect.py as a subprocess (python detect.py <sub>) with
cwd set to a temporary project directory, mirroring how the skill calls it.
UTF-8 everywhere.
"""
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    '.claude', 'skills', 'pbi', 'scripts', 'detect.py',
)


def run_detect(args, cwd):
    """Run detect.py with the given args in the given directory."""
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        cwd=cwd, capture_output=True, text=True, encoding='utf-8', timeout=30,
    )


def test_html_parse_unescapes_entities():
    """Formatted DAX containing < > && must not be written back HTML-escaped."""
    with tempfile.TemporaryDirectory() as tmp:
        resp = os.path.join(tmp, 'response.html')
        with open(resp, 'w', encoding='utf-8') as f:
            f.write(
                '<div class="formatted" >Flag&nbsp;=<br>'
                '<span class="Keyword">IF</span>&nbsp;(&nbsp;[A]&nbsp;&gt;&nbsp;0'
                '&nbsp;&amp;&amp;&nbsp;[B]&nbsp;&lt;&nbsp;5,&nbsp;1,&nbsp;0&nbsp;)'
                '</div>'
            )
        result = run_detect(['html-parse', resp], cwd=tmp)
        assert result.returncode == 0, result.stderr
        out = result.stdout
        assert '[A] > 0' in out, f'expected unescaped >, got: {out!r}'
        assert '&&' in out, f'expected unescaped &&, got: {out!r}'
        assert '[B] < 5' in out, f'expected unescaped <, got: {out!r}'
        assert '&gt;' not in out and '&lt;' not in out and '&amp;' not in out
        assert '\xa0' not in out, 'non-breaking space leaked into output'


def test_detect_pbip_unknown_format_fallback():
    """SemanticModel dir with neither model.bim nor definition/tables/ => unknown."""
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, 'Sales.SemanticModel'))
        result = run_detect(['pbip'], cwd=tmp)
        assert result.returncode == 0, result.stderr
        assert 'PBIP_FORMAT=unknown' in result.stdout, result.stdout
        assert 'PBIP_DIR=Sales.SemanticModel' in result.stdout


def test_detect_pbip_multiple_dirs_warning():
    """Two SemanticModel folders => PBIP_WARN line naming the chosen one."""
    with tempfile.TemporaryDirectory() as tmp:
        for name in ('A.SemanticModel', 'B.SemanticModel'):
            os.makedirs(os.path.join(tmp, name, 'definition', 'tables'))
        result = run_detect(['pbip'], cwd=tmp)
        assert result.returncode == 0, result.stderr
        assert 'PBIP_WARN=multiple SemanticModel folders found, using' in result.stdout
        assert 'PBIP_MODE=file' in result.stdout


def test_gitignore_check_appends_newline_first():
    """Existing .gitignore without trailing newline must not glue entries."""
    with tempfile.TemporaryDirectory() as tmp:
        gi = os.path.join(tmp, '.gitignore')
        with open(gi, 'w', encoding='utf-8') as f:
            f.write('node_modules')  # no trailing newline
        result = run_detect(['gitignore-check'], cwd=tmp)
        assert result.returncode == 0, result.stderr
        assert 'GITIGNORE_OK' in result.stdout
        with open(gi, encoding='utf-8') as f:
            lines = [line.rstrip('\n') for line in f]
        assert 'node_modules' in lines, f'last line was glued: {lines}'
        assert '*.abf' in lines
        assert not any('node_modules*' in line for line in lines)


def test_migrate_skip_message_when_destination_exists():
    """Legacy file skipped because destination exists => explicit MIGRATE_SKIPPED."""
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, '.pbi'))
        with open(os.path.join(tmp, 'project-docs.md'), 'w', encoding='utf-8') as f:
            f.write('legacy')
        with open(os.path.join(tmp, '.pbi', 'project-docs.md'), 'w', encoding='utf-8') as f:
            f.write('current')
        result = run_detect(['migrate'], cwd=tmp)
        assert result.returncode == 0, result.stderr
        assert 'MIGRATE_SKIPPED project-docs.md (destination exists)' in result.stdout
        assert 'MIGRATE_OK' not in result.stdout
        # Destination untouched, legacy file left in place
        with open(os.path.join(tmp, '.pbi', 'project-docs.md'), encoding='utf-8') as f:
            assert f.read() == 'current'


def test_migrate_moves_project_extract():
    """project-extract.md is part of the migration map."""
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, 'project-extract.md'), 'w', encoding='utf-8') as f:
            f.write('extract')
        result = run_detect(['migrate'], cwd=tmp)
        assert result.returncode == 0, result.stderr
        assert 'MIGRATED: project-extract.md' in result.stdout
        assert os.path.isfile(os.path.join(tmp, '.pbi', 'project-extract.md'))


def test_session_check_naive_timestamp():
    """A naive (no timezone) Session-Start timestamp must not crash and counts as UTC."""
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, '.pbi'))
        naive_now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
        with open(os.path.join(tmp, '.pbi', 'context.md'), 'w', encoding='utf-8') as f:
            f.write('## Model Context\n**Session-Start:** ' + naive_now + '\n')
        result = run_detect(['session-check'], cwd=tmp)
        assert result.returncode == 0, result.stderr
        assert 'SESSION=active' in result.stdout, result.stdout


def test_session_check_stale_naive_timestamp():
    """A naive timestamp older than 2h => SESSION=new (no TypeError crash)."""
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, '.pbi'))
        with open(os.path.join(tmp, '.pbi', 'context.md'), 'w', encoding='utf-8') as f:
            f.write('## Model Context\n**Session-Start:** 2020-01-01T00:00:00\n')
        result = run_detect(['session-check'], cwd=tmp)
        assert result.returncode == 0, result.stderr
        assert 'SESSION=new' in result.stdout, result.stdout


def test_detect_files_includes_relationships():
    """File Index must list definition/relationships.tmdl (and model/expressions)."""
    with tempfile.TemporaryDirectory() as tmp:
        defn = os.path.join(tmp, 'Ventes.SemanticModel', 'definition')
        os.makedirs(os.path.join(defn, 'tables'))
        with open(os.path.join(defn, 'tables', 'Ventes.tmdl'), 'w', encoding='utf-8') as f:
            f.write("table Ventes\n\tmeasure 'CA Total' = SUM(Ventes[Montant])\n")
        with open(os.path.join(defn, 'relationships.tmdl'), 'w', encoding='utf-8') as f:
            f.write('relationship r1\n\tfromColumn: Ventes.DateKey\n')
        with open(os.path.join(defn, 'model.tmdl'), 'w', encoding='utf-8') as f:
            f.write('model Model\n\tculture: fr-FR\n')
        result = run_detect(['files'], cwd=tmp)
        assert result.returncode == 0, result.stderr
        out = result.stdout
        assert 'Ventes.tmdl' in out
        assert 'relationships.tmdl' in out, f'relationships.tmdl missing: {out!r}'
        assert 'model.tmdl' in out
        # expressions.tmdl does not exist => must not be listed
        assert 'expressions.tmdl' not in out


ALL_TESTS = [
    test_html_parse_unescapes_entities,
    test_detect_pbip_unknown_format_fallback,
    test_detect_pbip_multiple_dirs_warning,
    test_gitignore_check_appends_newline_first,
    test_migrate_skip_message_when_destination_exists,
    test_migrate_moves_project_extract,
    test_session_check_naive_timestamp,
    test_session_check_stale_naive_timestamp,
    test_detect_files_includes_relationships,
]


if __name__ == '__main__':
    failed = 0
    for test in ALL_TESTS:
        try:
            test()
            print(f'PASS  {test.__name__}')
        except AssertionError as e:
            failed += 1
            print(f'FAIL  {test.__name__}: {e}')
    print(f'\n{len(ALL_TESTS) - failed}/{len(ALL_TESTS)} tests passed')
    sys.exit(1 if failed else 0)
