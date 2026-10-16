# Development

Use the Python package in src and the pytest regression suite. CI must pass before release.

## 1.1.0 improvement session

Ship nine sourced save-folder records for Factorio, Stardew Valley and OpenTTD, with explicit path inspection and confidence labels.

The catalog contains Windows, macOS and Linux documented defaults for three games, with source URLs, verification dates, configuration/store notes and version scope. Documentation was reviewed on 2026-09-07; no specific installed game build was tested. Portable/custom configurations may differ. `--inspect-id ID` previews one selected host-OS path; add `--confirm-path-check` to check only that directory's existence. Expansion permits known home/application-data variables and rejects unknown variables, traversal and network paths. Confidence remains documented-default/local-unverified until inspection, and evidence older than 180 days receives a stale label. No save contents are read or uploaded and no broad disk scan is performed.

Local formatting, lint, strict types and regression tests pass. Public release completion requires the protected CI/CodeQL matrix, tagged artifacts and matching Forge catalog/detail deployment.

## Compare contributions by record ID

```bash
save-folder-locator --catalog examples/catalog.json --compare-catalog examples/catalog.json --format json
```

Version 1.2.0 compares two explicitly supplied catalogs. Stable IDs identify added,
removed, changed and unchanged records. Changed entries retain both complete
records and list changed fields, including OS, platform/store, template, source,
verification date and version scope. Duplicate IDs in either catalog fail validation.
The comparison cannot combine with search or path-inspection flags.

Different templates for the same game, OS, store and path type are listed as
potential default conflicts on each side, including their dates and version scopes.
They may describe distinct configurations: the report keeps both claims visible
and never picks a winner. Source dates remain contributor claims. Comparison does
not expand templates, check directories, read saves, fetch URLs or modify catalogs.
