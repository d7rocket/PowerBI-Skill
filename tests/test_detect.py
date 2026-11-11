#!/usr/bin/env python3
"""Tests for plugins/pbi/scripts/detect.py and validate-edit.py.

Runnable two ways:
    pytest tests/test_detect.py
    python tests/test_detect.py

Each test invokes the script as a subprocess with cwd set to a temporary
project directory, mirroring how the plugin calls it. UTF-8 everywhere.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, 'plugins', 'pbi')
SCRIPT = os.path.join(PLUGIN, 'scripts', 'detect.py')
HOOK = os.path.join(PLUGIN, 'scripts', 'validate-edit.py')
FIXTURES = os.path.join(ROOT, 'tests', 'fixtures')


def run_detect(args, cwd):
    """Run detect.py with the given args in the given directory."""
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        cwd=cwd, capture_output=True, text=True, encoding='utf-8', timeout=60,
    )


def git(args, cwd):
    return subprocess.run(
        ['git', '-c', 'user.name=test', '-c', 'user.email=test@example.com',
         '-c', 'commit.gpgsign=false'] + list(args),
        cwd=cwd, capture_output=True, text=True, encoding='utf-8', timeout=60,
    )


def make_project(tmp, name='Ventes'):
    """A small TMDL project with French names, quoted names and a relationship."""
    defn = os.path.join(tmp, name + '.SemanticModel', 'definition')
    os.makedirs(os.path.join(defn, 'tables'))
    with open(os.path.join(defn, 'tables', 'Ventes.tmdl'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(
            "table Ventes\n\n"
            "\tcolumn Montant\n\t\tdataType: decimal\n\n"
            "\tcolumn 'Clé Date'\n\t\tdataType: int64\n\t\tisHidden\n\n"
            "\t/// Chiffre d'affaires réalisé.\n"
            "\tmeasure 'CA Réalisé' =\n"
            "\t\t\tSUM(Ventes[Montant])\n"
            "\t\tformatString: #,##0\n"
            "\t\tdisplayFolder: \"Base\"\n\n"
            "\tmeasure 'CA d''Été' = CALCULATE([CA Réalisé], 'Date'[Saison] = \"Été\")\n"
            "\t\tformatString: #,##0\n\n"
            "\tpartition Ventes = m\n\t\tmode: import\n"
        )
    with open(os.path.join(defn, 'tables', 'Date.tmdl'), 'w', encoding='utf-8', newline='\n') as f:
        f.write("table Date\n\tdataCategory: Time\n\n\tcolumn Date\n\t\tdataType: dateTime\n")
    with open(os.path.join(defn, 'relationships.tmdl'), 'w', encoding='utf-8', newline='\n') as f:
        f.write("relationship r1\n\tfromColumn: Ventes.'Clé Date'\n\ttoColumn: Date.Date\n"
                "\tcrossFilteringBehavior: bothDirections\n")
    return name + '.SemanticModel'


# ── preflight ───────────────────────────────────────────────────────

def test_preflight_paste_mode_creates_nothing():
    """No project => paste mode, core rules printed, no .pbi folder littered."""
    with tempfile.TemporaryDirectory() as tmp:
        result = run_detect(['preflight'], cwd=tmp)
        assert result.returncode == 0, result.stderr
        assert 'PBIP_MODE=paste' in result.stdout
        assert '# /pbi core rules' in result.stdout
        assert not os.path.exists(os.path.join(tmp, '.pbi'))


def test_preflight_project_index_with_accents():
    """Model index lists tables, quoted French measure names and the relationship."""
    with tempfile.TemporaryDirectory() as tmp:
        sm = make_project(tmp)
        result = run_detect(['preflight'], cwd=tmp)
        assert result.returncode == 0, result.stderr
        out = result.stdout
        assert 'PBIP_MODE=file PBIP_FORMAT=tmdl PBIP_DIR=' + sm in out
        assert '(2 tables, 2 measures, 1 relationships)' in out, out
        assert "CA Réalisé | CA d'Été" in out, out
        assert "Ventes[Clé Date] -> Date[Date]" in out, out
        assert 'BIDIRECTIONAL' in out
        assert '| Ventes | 2 | 2 |' in out


def test_preflight_expands_plugin_root_in_rules():
    """Core rules are injected with a real script path, not the placeholder."""
    with tempfile.TemporaryDirectory() as tmp:
        result = run_detect(['preflight'], cwd=tmp)
        assert '${CLAUDE_PLUGIN_ROOT}' not in result.stdout
        assert 'scripts/detect.py' in result.stdout


def test_preflight_unknown_format_and_multiple_models():
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, 'A.SemanticModel'))
        os.makedirs(os.path.join(tmp, 'B.SemanticModel', 'definition', 'tables'))
        out = run_detect(['preflight'], cwd=tmp).stdout
        assert 'PBIP_WARN=multiple SemanticModel folders found, using A.SemanticModel' in out
        assert 'PBIP_FORMAT=unknown' in out


def test_preflight_tmsl_fixture():
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(os.path.join(FIXTURES, 'pbip-tmsl', '.SemanticModel'),
                        os.path.join(tmp, '.SemanticModel'))
        out = run_detect(['preflight'], cwd=tmp).stdout
        assert 'PBIP_FORMAT=tmsl' in out
        assert 'Revenue YTD | Revenue' in out, out
        assert 'Sales[Date] -> Date[Date]' in out


def test_preflight_migrates_legacy_files():
    with tempfile.TemporaryDirectory() as tmp:
        make_project(tmp)
        with open(os.path.join(tmp, 'project-extract.md'), 'w', encoding='utf-8') as f:
            f.write('extract')
        os.makedirs(os.path.join(tmp, '.pbi'))
        with open(os.path.join(tmp, 'project-docs.md'), 'w', encoding='utf-8') as f:
            f.write('legacy')
        with open(os.path.join(tmp, '.pbi', 'project-docs.md'), 'w', encoding='utf-8') as f:
            f.write('current')
        out = run_detect(['preflight'], cwd=tmp).stdout
        assert 'MIGRATED: project-extract.md' in out
        assert 'MIGRATE_SKIPPED project-docs.md (destination exists)' in out
        with open(os.path.join(tmp, '.pbi', 'project-docs.md'), encoding='utf-8') as f:
            assert f.read() == 'current'


# ── measure / search ────────────────────────────────────────────────

def test_measure_returns_block_with_description_and_escaped_quote():
    with tempfile.TemporaryDirectory() as tmp:
        make_project(tmp)
        result = run_detect(['measure', 'CA Réalisé'], cwd=tmp)
        out = result.stdout
        assert 'MEASURE_MATCHES=1' in out, out
        assert "/// Chiffre d'affaires réalisé." in out
        assert 'displayFolder: "Base"' in out
        assert "CA d''Été" not in out, 'block leaked into the next measure'
        # a doubled quote inside a quoted TMDL name is one apostrophe
        out2 = run_detect(['measure', "[CA d'Été]"], cwd=tmp).stdout
        assert 'MEASURE_MATCHES=1' in out2, out2
        assert 'partition' not in out2, 'measure block must stop before the partition'


def test_measure_ambiguous_across_tables():
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(os.path.join(FIXTURES, 'pbip-tmdl', '.SemanticModel'),
                        os.path.join(tmp, '.SemanticModel'))
        assert 'MEASURE_MATCHES=2' in run_detect(['measure', 'Revenue'], cwd=tmp).stdout
        scoped = run_detect(['measure', 'Revenue', 'Sales'], cwd=tmp).stdout
        assert 'MEASURE_MATCHES=1' in scoped and 'SUM(Sales[Amount])' in scoped


def test_search_fixed_string_with_accent():
    with tempfile.TemporaryDirectory() as tmp:
        make_project(tmp)
        out = run_detect(['search', 'Réalisé'], cwd=tmp).stdout
        assert 'Ventes.tmdl' in out and 'Date.tmdl' not in out
        # regex metacharacters are literal
        assert run_detect(['search', 'Ventes[Montant]'], cwd=tmp).stdout.strip().endswith('Ventes.tmdl')


# ── session log ─────────────────────────────────────────────────────

def test_log_trims_history_to_20_and_keeps_failures():
    with tempfile.TemporaryDirectory() as tmp:
        make_project(tmp)
        os.makedirs(os.path.join(tmp, '.pbi'))
        shutil.copy(os.path.join(FIXTURES, 'context-20-rows.md'), os.path.join(tmp, '.pbi', 'context.md'))
        with open(os.path.join(tmp, '.pbi', 'context.md'), encoding='utf-8') as f:
            before = f.read()
        result = run_detect(['log', '/pbi:explain', 'CA | Réalisé', 'Explained'], cwd=tmp)
        assert 'LOGGED' in result.stdout, result.stdout + result.stderr
        with open(os.path.join(tmp, '.pbi', 'context.md'), encoding='utf-8') as f:
            after = f.read()
        history = after.split('## Command History')[1].split('## ')[0]
        rows = [l for l in history.splitlines() if l.startswith('|')][2:]
        assert len(rows) == 20, len(rows)
        assert rows[-1].endswith('| /pbi:explain | CA / Réalisé | Explained |'), rows[-1]
        assert '- Command: /pbi:explain' in after
        fail_before = before.split('## Analyst-Reported Failures')[1].strip()
        fail_after = after.split('## Analyst-Reported Failures')[1].split('\n## ')[0].strip()
        assert fail_before.split('\n## ')[0].strip() == fail_after


def test_log_drops_v7_model_snapshot_and_note_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        make_project(tmp)
        os.makedirs(os.path.join(tmp, '.pbi'))
        with open(os.path.join(tmp, '.pbi', 'context.md'), 'w', encoding='utf-8') as f:
            f.write('# PBI Context\n\n## Model Context\n**Session-Start:** 2026-01-01T00:00:00Z\n| stale |\n\n'
                    '## Command History\n| Timestamp | Command | Measure Name | Outcome |\n|---|---|---|---|\n')
        assert 'NOTED' in run_detect(['note', 'Business Question', 'Pourquoi le CA baisse ?'], cwd=tmp).stdout
        run_detect(['log', '/pbi:new', 'Marge', 'Created'], cwd=tmp)
        with open(os.path.join(tmp, '.pbi', 'context.md'), encoding='utf-8') as f:
            text = f.read()
        assert 'Session-Start' not in text and 'stale' not in text
        out = run_detect(['preflight'], cwd=tmp).stdout
        assert 'Pourquoi le CA baisse ?' in out
        assert '| /pbi:new | Marge | Created |' in out
        # managed sections cannot be overwritten through notes
        assert 'NOTE_ERROR' in run_detect(['note', 'Analyst-Reported Failures', 'x'], cwd=tmp).stdout


def test_log_skipped_outside_project():
    with tempfile.TemporaryDirectory() as tmp:
        assert 'LOG_SKIPPED' in run_detect(['log', '/pbi:explain', 'x', 'y'], cwd=tmp).stdout
        assert not os.path.exists(os.path.join(tmp, '.pbi'))


# ── journal and snapshot ────────────────────────────────────────────

def write_change(tmp, **fields):
    os.makedirs(os.path.join(tmp, '.pbi'), exist_ok=True)
    path = os.path.join(tmp, '.pbi', 'change.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(fields, f, ensure_ascii=False)
    return path


def test_record_last_undone():
    with tempfile.TemporaryDirectory() as tmp:
        make_project(tmp)
        assert 'JOURNAL=empty' in run_detect(['journal-last'], cwd=tmp).stdout
        write_change(tmp, command='/pbi:edit', tier='file', action='update', kind='measure',
                     table='Ventes', name='CA Réalisé', before='a', after='b', message='chore: one')
        assert 'RECORDED' in run_detect(['record', '.pbi/change.json'], cwd=tmp).stdout
        assert not os.path.exists(os.path.join(tmp, '.pbi', 'change.json'))
        write_change(tmp, command='/pbi:new', tier='file', action='create', kind='measure',
                     table='Ventes', name='Marge', before=None, after='c', message='feat: two')
        run_detect(['record', '.pbi/change.json'], cwd=tmp)
        last = json.loads(run_detect(['journal-last'], cwd=tmp).stdout)
        assert last['message'] == 'feat: two' and last['name'] == 'Marge'
        assert 'UNDONE' in run_detect(['journal-undone'], cwd=tmp).stdout
        last = json.loads(run_detect(['journal-last'], cwd=tmp).stdout)
        assert last['message'] == 'chore: one' and last['name'] == 'CA Réalisé'


def test_record_file_tier_commits_model_folder_only():
    """record = commit + journal in one step; the journal holds the commit it made."""
    with tempfile.TemporaryDirectory() as tmp:
        sm = make_project(tmp)
        git(['init', '-q'], tmp)
        git(['config', 'user.name', 'test'], tmp)
        git(['config', 'user.email', 'test@example.com'], tmp)
        git(['config', 'commit.gpgsign', 'false'], tmp)
        git(['add', '-A'], tmp)
        git(['commit', '-q', '-m', 'chore: initial'], tmp)
        with open(os.path.join(tmp, sm, 'definition', 'tables', 'Date.tmdl'), 'a',
                  encoding='utf-8', newline='\n') as f:
            f.write("\n\tcolumn Saison\n\t\tdataType: string\n")
        with open(os.path.join(tmp, 'notes.txt'), 'w', encoding='utf-8') as f:
            f.write('unrelated work in progress')
        git(['add', 'notes.txt'], tmp)
        write_change(tmp, command='/pbi:edit', tier='file', action='create', kind='column',
                     table='Date', name='Saison', before=None, after='column Saison',
                     message='feat: add Saison to Date')
        out = run_detect(['record', '.pbi/change.json'], cwd=tmp).stdout
        assert 'commit=ok' in out, out
        head = git(['log', '-1', '--format=%h|%B'], tmp).stdout.strip()
        sha, body = head.split('|', 1)
        assert body.strip() == 'feat: add Saison to Date', 'message must be exactly one line: %r' % body
        files = git(['show', '--name-only', '--format=', 'HEAD'], tmp).stdout.split()
        assert files == [sm + '/definition/tables/Date.tmdl'], files
        assert 'notes.txt' in git(['status', '--porcelain'], tmp).stdout, 'unrelated staged file must stay staged'
        last = json.loads(run_detect(['journal-last'], cwd=tmp).stdout)
        assert last['commit'] == sha and last['committed'] is True
        # nothing changed on disk => journaled, but no empty commit
        write_change(tmp, command='/pbi:edit', tier='file', action='update', kind='column',
                     table='Date', name='Saison', before='a', after='a', message='chore: noop')
        assert 'commit=nothing-to-commit' in run_detect(['record', '.pbi/change.json'], cwd=tmp).stdout
        # a bad record is rejected, not journaled
        write_change(tmp, command='/pbi:edit', action='update')
        assert 'RECORD_ERROR' in run_detect(['record', '.pbi/change.json'], cwd=tmp).stdout


def test_snapshot_commits_desktop_save_with_journal_message():
    """A live change is committed only once the files change (Desktop save)."""
    with tempfile.TemporaryDirectory() as tmp:
        sm = make_project(tmp)
        assert git(['init', '-q'], tmp).returncode == 0
        git(['add', '-A'], tmp)
        assert git(['commit', '-q', '-m', 'chore: initial'], tmp).returncode == 0
        env_git = {'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@example.com',
                   'GIT_COMMITTER_NAME': 't', 'GIT_COMMITTER_EMAIL': 't@example.com'}
        os.environ.update(env_git)
        try:
            assert 'SNAPSHOT=none' in run_detect(['snapshot'], cwd=tmp).stdout
            write_change(tmp, command='/pbi:new', tier='live', action='create', kind='measure',
                         table='Ventes', name='Marge', before=None, after='x',
                         message='feat: add Marge measure to Ventes')
            run_detect(['record', '.pbi/change.json'], cwd=tmp)
            assert 'PENDING_LIVE_CHANGES=1' in run_detect(['preflight'], cwd=tmp).stdout
            last = json.loads(run_detect(['journal-last'], cwd=tmp).stdout)
            assert last['committed'] is False
            assert 'SNAPSHOT=waiting' in run_detect(['snapshot'], cwd=tmp).stdout
            # the analyst presses Ctrl+S in Desktop: the TMDL file changes
            with open(os.path.join(tmp, sm, 'definition', 'tables', 'Ventes.tmdl'), 'a',
                      encoding='utf-8', newline='\n') as f:
                f.write("\n\tmeasure Marge = [CA Réalisé] * 0.3\n")
            out = run_detect(['snapshot'], cwd=tmp).stdout
            assert 'SNAPSHOT_COMMITTED=' in out and 'feat: add Marge measure to Ventes' in out, out
            log = git(['log', '--oneline', '-1'], tmp).stdout
            assert 'feat: add Marge measure to Ventes' in log, log
            last = json.loads(run_detect(['journal-last'], cwd=tmp).stdout)
            assert last['committed'] is True and last['commit']
            assert 'PENDING_LIVE_CHANGES' not in run_detect(['preflight'], cwd=tmp).stdout
            assert 'SNAPSHOT=none' in run_detect(['snapshot'], cwd=tmp).stdout
        finally:
            for k in env_git:
                os.environ.pop(k, None)


# ── misc subcommands ────────────────────────────────────────────────

def test_version_matches_manifest_and_changelog():
    """plugin.json is the single source of truth; the changelog top entry must match."""
    with open(os.path.join(PLUGIN, '.claude-plugin', 'plugin.json'), encoding='utf-8') as f:
        version = json.load(f)['version']
    with tempfile.TemporaryDirectory() as tmp:
        assert run_detect(['version'], cwd=tmp).stdout.strip() == 'LOCAL=' + version
    with open(os.path.join(PLUGIN, 'shared', 'CHANGELOG.md'), encoding='utf-8') as f:
        for line in f:
            if line.startswith('## '):
                assert version in line, 'top changelog entry %r does not match %s' % (line, version)
                break


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
        out = run_detect(['html-parse', resp], cwd=tmp).stdout
        assert '[A] > 0' in out and '&&' in out and '[B] < 5' in out, out
        assert '&gt;' not in out and '&lt;' not in out and '&amp;' not in out
        assert '\xa0' not in out, 'non-breaking space leaked into output'


def test_gitignore_check_appends_newline_first():
    """Existing .gitignore without trailing newline must not glue entries."""
    with tempfile.TemporaryDirectory() as tmp:
        gi = os.path.join(tmp, '.gitignore')
        with open(gi, 'w', encoding='utf-8') as f:
            f.write('node_modules')  # no trailing newline
        assert 'GITIGNORE_OK' in run_detect(['gitignore-check'], cwd=tmp).stdout
        with open(gi, encoding='utf-8') as f:
            lines = [line.rstrip('\n') for line in f]
        assert 'node_modules' in lines, 'last line was glued: %s' % lines
        assert '*.abf' in lines and '.pbi/journal.jsonl' in lines


def test_env_reports_all_keys():
    with tempfile.TemporaryDirectory() as tmp:
        out = run_detect(['env'], cwd=tmp).stdout
        for key in ('PLATFORM=', 'PYTHON=', 'NODE=', 'NPX=', 'CLAUDE=', 'DESKTOP=', 'LIVE_MCP_CONFIG='):
            assert key in out, 'missing %s in %r' % (key, out)


# ── edit-validation hook ────────────────────────────────────────────

def run_hook(file_path):
    payload = json.dumps({'tool_input': {'file_path': file_path}})
    return subprocess.run([sys.executable, HOOK], input=payload, capture_output=True,
                          text=True, encoding='utf-8', timeout=30)


def test_hook_tmdl_rules_and_ignores_other_files():
    with tempfile.TemporaryDirectory() as tmp:
        good = os.path.join(tmp, 'good.tmdl')
        with open(good, 'w', encoding='utf-8', newline='\n') as f:
            f.write("table T\n\tmeasure 'Été' = 1\n")
        assert run_hook(good).returncode == 0
        spaces = os.path.join(tmp, 'spaces.tmdl')
        with open(spaces, 'w', encoding='utf-8', newline='\n') as f:
            f.write("table T\n    measure M = 1\n")
        assert run_hook(spaces).returncode == 1
        ctrl = os.path.join(tmp, 'ctrl.tmdl')
        with open(ctrl, 'w', encoding='utf-8', newline='\n') as f:
            f.write("table T\n\tmeasure M = 1\x07\n")
        assert run_hook(ctrl).returncode == 2
        # the plugin is enabled everywhere: broken Python in another project is not our business
        py = os.path.join(tmp, 'broken.py')
        with open(py, 'w', encoding='utf-8') as f:
            f.write('def (:\n')
        assert run_hook(py).returncode == 0


# ── plugin integrity ────────────────────────────────────────────────

def test_every_skill_is_wired_and_clean():
    """No v7 leftovers, every referenced shared file exists, names match folders."""
    skills = os.path.join(PLUGIN, 'skills')
    names = sorted(os.listdir(skills))
    assert len(names) == 22, names
    stale = ('PBI_CONFIRM', '.claude/skills', 'comment-batch', 'format-batch', 'audit-fix',
             'pbi:settings', 'session-check', 'Session Context', 'File Index', '@@PREFLIGHT@@')
    for name in names:
        with open(os.path.join(skills, name, 'SKILL.md'), encoding='utf-8') as f:
            text = f.read()
        assert text.startswith('---\nname: %s\n' % name), name
        for token in stale:
            assert token not in text, '%s still mentions %s' % (name, token)
        assert '— Log' not in text
        import re
        for ref in re.findall(r'\$\{CLAUDE_PLUGIN_ROOT\}/((?:shared|scripts)/[\w.-]+)', text):
            assert os.path.isfile(os.path.join(PLUGIN, ref)), '%s references missing %s' % (name, ref)
        for cmd in re.findall(r'/pbi:([a-z]+)', text):
            assert cmd in names, '%s references unknown command /pbi:%s' % (name, cmd)


ALL_TESTS = [v for k, v in sorted(globals().items()) if k.startswith('test_') and callable(v)]


if __name__ == '__main__':
    failed = 0
    for test in ALL_TESTS:
        try:
            test()
            print('PASS  ' + test.__name__)
        except AssertionError as e:
            failed += 1
            print('FAIL  %s: %s' % (test.__name__, e))
    print('\n%d/%d tests passed' % (len(ALL_TESTS) - failed, len(ALL_TESTS)))
    sys.exit(1 if failed else 0)
