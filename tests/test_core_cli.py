import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from game_save_folder_locator.cli import main
from game_save_folder_locator.core import load_catalog, render_markdown, search


def catalog() -> dict[str, Any]:
    return {
        "version": 1,
        "records": [
            {
                "id": "north-win",
                "game": "North Road (fictional example)",
                "os": "windows",
                "platform": "standalone",
                "path_type": "local",
                "path": "{HOME}/North Road",
                "source": "https://github.com/loganpendragonmultiverse/game-save-folder-locator",
                "verified_on": "2026-07-26",
                "notes": "Demonstration only",
            },
            {
                "id": "north-linux",
                "game": "North Road (fictional example)",
                "os": "linux",
                "platform": "standalone",
                "path_type": "configuration-dependent",
                "path": "{HOME}/.north-road",
                "source": "https://github.com/loganpendragonmultiverse/game-save-folder-locator",
                "verified_on": "2026-07-26",
            },
        ],
    }


def write(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def test_search_filters_and_rendering() -> None:
    result = search(catalog(), "north", "windows", "STANDALONE", "local")
    assert result["record_count"] == 1
    assert "Demonstration only" in render_markdown(result)
    assert search(catalog(), "missing")["record_count"] == 0
    with pytest.raises(ValueError, match="unknown operating"):
        search(catalog(), operating_system="plan9")
    with pytest.raises(ValueError, match="unknown path type"):
        search(catalog(), path_type="magic")


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda data: data.update(version=2), "version 1"),
        (lambda data: data.update(records="bad"), "records must"),
        (lambda data: data["records"].append("bad"), "must be an object"),
        (lambda data: data["records"][0].update(game=""), "field: game"),
        (lambda data: data["records"].append(data["records"][0].copy()), "duplicate"),
        (lambda data: data["records"][0].update(os="plan9"), "invalid operating"),
        (lambda data: data["records"][0].update(path_type="magic"), "invalid path type"),
        (lambda data: data["records"][0].update(source="file.txt"), "HTTP source"),
        (lambda data: data["records"][0].update(verified_on="today"), "ISO date"),
        (lambda data: data["records"][0].update(notes=4), "notes must"),
    ],
)
def test_validation(tmp_path: Path, change: Callable[[dict[str, Any]], None], message: str) -> None:
    data = catalog()
    change(data)
    path = tmp_path / "catalog.json"
    write(path, data)
    with pytest.raises((TypeError, ValueError), match=message):
        load_catalog(path)


def test_cli_default_and_safe_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["record_count"] == 0
    path = tmp_path / "catalog.json"
    write(path, catalog())
    output = tmp_path / "report.md"
    assert main(["--catalog", str(path), "--game", "North", "--output", str(output)]) == 0
    assert main(["--catalog", str(path), "--output", str(output)]) == 2
