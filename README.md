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
