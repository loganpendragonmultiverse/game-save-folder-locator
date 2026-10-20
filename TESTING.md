# Testing

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. CI also audits dependencies and runs the supported OS/Python matrix.

## 1.1.0 regression acceptance

Run the complete existing suite plus the new regression fixtures. Confirm the documented command produces the selected output, malformed input remains actionable, and source files remain unchanged. Ship nine sourced save-folder records for Factorio, Stardew Valley and OpenTTD, with explicit path inspection and confidence labels.

Catalog comparison tests cover stable IDs, changed templates/OS/store/source/version
scope/dates, added and removed rows, duplicate IDs and conflicting defaults.
Tests deny path inspection and source fetching and assert input immutability.

The 1.2.1 regressions cover boolean versions, compact-date rejection on every
Python version, complete variable names, permission errors in explicit metadata
checks, nested JSON type changes and exclusive-output races/dangling symlinks.
Install each tag-built wheel/source distribution in a fresh environment outside
the checkout, verify site-packages imports and run the full tests with
`pytest -o addopts='' /path/to/tests`; retain the separate 90% source coverage
gate. Confirm the installed default catalog still contains nine sourced records.
