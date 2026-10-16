# Contributing catalog records

Submit one installation-specific record per operating system, platform or store, and path type. Use placeholders such as `{HOME}`, `{APPDATA}`, or `{GAME_DIR}` instead of a contributor's username. Every non-example record needs a direct source URL, the date it was last checked, and a concise note when the path depends on portable mode, compatibility software, a game version, or configuration.

Do not copy large third-party databases. Prefer official documentation, upstream source code, or a small independently verified contribution. A path is accepted as evidence for one configuration, not a universal guarantee.

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
