# Game Save Folder Locator Database

[![CI](https://github.com/loganpendragonmultiverse/game-save-folder-locator/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/game-save-folder-locator/actions/workflows/ci.yml)

Game Save Folder Locator Database provides a validated, community-editable format and local search tool for game-save path templates. Records are separated by game, operating system, platform or store, path type, source URL, and verification date so conflicting installations remain visible instead of being collapsed into one guess.

## Three-minute start

```bash
python -m pip install .
save-folder-locator --catalog examples/catalog.json --game "North Road"
save-folder-locator --catalog examples/catalog.json --os windows --format json
```

The packaged catalog intentionally starts empty rather than publishing unverified paths. `examples/catalog.json` demonstrates the contribution format with an explicitly fictional game. Useful growth depends on reviewed contributions with reproducible sources; see [docs/CONTRIBUTING_RECORDS.md](docs/CONTRIBUTING_RECORDS.md).

The tool does not scan a computer, expand environment variables, access cloud saves, or claim that every installation follows a documented default. Paths may change with game versions, stores, portable installations, compatibility layers, or user configuration. Requires Python 3.10 or newer.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## Version 1.1.0: reviewed improvements

Ship nine sourced save-folder records for Factorio, Stardew Valley and OpenTTD, with explicit path inspection and confidence labels.

```bash
save-folder-locator --game Factorio --os windows --format json
```

The catalog contains Windows, macOS and Linux documented defaults for three games, with source URLs, verification dates, configuration/store notes and version scope. Documentation was reviewed on 2026-09-07; no specific installed game build was tested. Portable/custom configurations may differ. `--inspect-id ID` previews one selected host-OS path; add `--confirm-path-check` to check only that directory's existence. Expansion permits known home/application-data variables and rejects unknown variables, traversal and network paths. Confidence remains documented-default/local-unverified until inspection, and evidence older than 180 days receives a stale label. No save contents are read or uploaded and no broad disk scan is performed.
