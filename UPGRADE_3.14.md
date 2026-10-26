# Upgrading to Python 3.14

Notes from moving this fork from Python 3.10 to 3.14 (October 2026).
Commits: `128bf56f` (upgrade) and `8f8d00d2` (invalid escape sequences).

## Why 3.14 and not 3.15

- Python 3.10 reaches end-of-life in October 2026 (no more security fixes).
- 3.15.0 was only weeks old at the time. 3.14 has had a year of bug-fix
  releases, and every dependency ships wheels for it.
- Revisit 3.15 after 3.15.1–3.15.2. See [Checklist for the next upgrade](#checklist-for-the-next-upgrade).

## What changed

| Area | Change |
|---|---|
| `pyproject.toml` | `python = "^3.11"`; `sphinx` and `pytest` changed from `^7` to `>=` (the caret pins blocked versions that support 3.13+) |
| `poetry.lock` | Regenerated. Old pins (e.g. matplotlib 3.7.2, numpy 1.25) have no 3.14 wheels |
| `configuration.py` | `locale.getdefaultlocale()` (deprecated in 3.11, slated for removal) replaced by `system_locale()`, which does the same lookup |
| `database_logger.py` | `datetime.utcfromtimestamp()` (deprecated in 3.12) replaced |
| `upgrade1.py` | Removed a dead `getdefaultlocale()` block (`locale` was never imported) |
| 11 files | Invalid escapes such as `"\d"` fixed (SyntaxWarning since 3.12) |

Main resolved versions: PyQt6 6.11, matplotlib 3.11, numpy 2.5,
CherryPy 18.10, Sphinx 9, pytest 9.

**The database format does not change.** It is a plain SQLite file, the schema
is defined by Mnemosyne, and stored values use `repr()`/`eval()`. Pickles are
only read (1.x imports), never written. Back up `default.db` and `config.db`
anyway before the first launch on a new Python.

## Recreating the virtualenv

Poetry manages `.venv`, and the `mnemosyne` shell function runs
`source .venv/bin/activate`. The environment **must** live in the project's
`.venv`.

`virtualenvs.in-project` is not set globally. Poetry only reused `.venv`
because it already existed. If you delete or move `.venv` without setting it,
Poetry creates the environment under `~/Library/Caches/pypoetry/virtualenvs/`
and the shell function breaks.

```sh
cd ~/GitHub/mnemosyne

# One-time, persistent (writes poetry.toml in the project):
poetry config virtualenvs.in-project true --local
# ...or per-command only:
export POETRY_VIRTUALENVS_IN_PROJECT=true

mv .venv .venv-old                         # keep for rollback
poetry env use /opt/homebrew/bin/python3.14
poetry lock --regenerate                   # only when changing Python version
poetry install
.venv/bin/python --version                 # confirm it landed in .venv
```

Roll back:

```sh
rm -rf .venv && mv .venv-old .venv
```

Notes:

- In Poetry 2, plain `poetry lock` **keeps** the existing pinned versions. When
  moving to a new Python, use `poetry lock --regenerate`. Otherwise
  `poetry install` tries to build old packages from source and fails
  (matplotlib 3.7.2 did).
- `poetry install` runs `poetry-build.py`, which runs `make build` (the Qt UI
  files).
- Before switching `.venv`, try the new Python in a throwaway environment to
  check that every dependency installs:
  `uv venv -p python3.14 /tmp/v && uv pip install --python /tmp/v/bin/python <deps>`.

## Running the tests

```sh
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests -q -ra \
    --timeout=120 --ignore=tests/test_sync.py      # takes a few seconds
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_sync.py -q \
    --timeout=60 --timeout-method=thread           # run separately
```

Baseline on both 3.10 and 3.14: **391 passed, 15 failed** (non-sync). The 15
failures already existed and are identical on both versions. The LaTeX ones
fail because `latex`/`dvipng` are not installed. Always compare *failure lists*
against the old Python, not just counts.

## Lessons learnt

1. **Never run two test suites at the same time in this repo.**
   `tests/test_sync.py` binds a fixed port (9923), and tests write to
   `dot_test/` in the current directory. Two runs at once collide. One sync
   failure then cascades, and a later test can hang forever. Run suites one
   after another, or in separate copies of the tree with sync excluded.
2. **Sync tests can hang instead of failing.** `_wait_for_server_shutdown`
   waits with no timeout for the server thread to set `passed_tests`. If that
   thread dies, the main thread blocks forever, and the default
   `pytest-timeout` method did not interrupt it. Use
   `--timeout-method=thread`, which dumps every thread's stack and exits.
3. **`test_sync.py` stalls at `test_latex` without LaTeX installed.** This is
   environmental, not a Python-version issue.
4. **Get a baseline on the old Python first**, with the same commands, and
   diff the failure lists. Without that, existing failures look like
   regressions.
5. **Grep for both spellings of a deprecated API.** The first search found
   `locale.getdefaultlocale` but missed `from locale import getdefaultlocale`.
   Running the tests with `-W default::DeprecationWarning` revealed it.
6. **Find all invalid escapes by compiling with warnings recorded**, not with
   `compileall -W error`, which stops at the first one in each file. Then fix
   them so values are preserved:
   - use a raw string only when the literal contains *no* valid escapes;
   - otherwise double only the invalid backslashes (`"\times"` contains a real
     `\t` tab, and `"a\nb"` a real newline);
   - check that `ast.dump(ast.parse(old)) == ast.dump(ast.parse(new))` for each
     file. This caught two script bugs before anything was written.
7. **Several files use CRLF line endings.** Scripted rewrites must open files
   with `newline=''` (reading and writing). Otherwise whole files get
   converted. Also count a backslash followed by `\r\n` as a valid line
   continuation.
8. **A leftover `default.db-journal` is normal.** Mnemosyne uses
   `journal_mode = persist`, so the journal stays after each save with a
   zeroed header. A non-zero header means an unfinished save. In that case,
   back up the journal together with `default.db`.

## Checklist for the next upgrade

- [ ] Python 3.15:
  - re-check `locale` APIs, since `getdefaultlocale` itself is gone;
  - run the tests with `-W error::DeprecationWarning` to surface anything
    else removed.
- [ ] Check that wheels exist on PyPI for PyQt6, PyQt6-WebEngine, matplotlib,
      numpy and argon2-cffi-bindings (PyQt6 ships `abi3` wheels that cover new
      versions).
- [ ] Baseline the tests on the current Python, upgrade, and diff the failure
      lists.
- [ ] Back up `default.db` and `config.db`, then launch with a throwaway data
      dir before the real one:
      `python mnemosyne/pyqt_ui/mnemosyne -d /tmp/mnemo-test`.
- [ ] Remaining known issues:
  - `is` comparisons with string literals in
    `tests/test_cuecard_wcu_import.py:51` and
    `tests/test_smconv_import.py:51`;
  - `science_server/cgiupload.py` is Python 2 code.
