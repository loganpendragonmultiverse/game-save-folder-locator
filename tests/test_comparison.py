import copy
import json
from pathlib import Path

import pytest

from game_save_folder_locator.cli import main
from game_save_folder_locator.comparison import compare_catalogs, render_comparison_markdown


def record(record_id="synthetic"):
    return {
        "id": record_id,
        "game": "Fictional",
        "os": "linux",
        "platform": "manual",
        "path_type": "local",
        "path": "$HOME/synthetic",
        "source": "https://example.org/docs",
        "verified_on": "2026-10-16",
        "version_scope": "1.x",
    }


def catalog(*records):
    return {"version": 1, "records": list(records)}


@pytest.mark.parametrize(
    "field,value",
    [
        ("os", "windows"),
        ("platform", "store"),
        ("path", "%APPDATA%/fiction"),
        ("source", "https://example.org/other"),
        ("verified_on", "2026-10-15"),
        ("version_scope", "2.x"),
        ("notes", "configuration"),
    ],
)
def test_changed_fields(field, value, monkeypatch):
    before = catalog(record())
    after = copy.deepcopy(before)
    after["records"][0][field] = value
    originals = copy.deepcopy((before, after))

    def forbidden(*args, **kwargs):
        raise AssertionError("comparison touched a save path")

    monkeypatch.setattr(Path, "stat", forbidden)
    monkeypatch.setattr(Path, "resolve", forbidden)
    report = compare_catalogs(before, after)
    assert report["changed"][0]["fields"] == [field]
    assert report["changed"][0]["before"] == before["records"][0]
    assert report["changed"][0]["after"] == after["records"][0]
    assert (before, after) == originals
    report["changed"][0]["after"]["path"] = "edited output"
    assert (before, after) == originals


def test_added_removed_order_and_unchanged():
    report = compare_catalogs(
        catalog(record("gone"), record("same")), catalog(record("new"), record("same"))
    )
    assert [r["id"] for r in report["added"]] == ["new"]
    assert [r["id"] for r in report["removed"]] == ["gone"]
    assert report["unchanged_ids"] == ["same"]
    assert compare_catalogs(catalog(), catalog())["changed"] == []


@pytest.mark.parametrize("side", ["before", "after"])
def test_duplicates_and_dates(side):
    valid = catalog(record())
    duplicate = catalog(record(), record())
    with pytest.raises(ValueError, match="duplicate"):
        compare_catalogs(
            duplicate if side == "before" else valid, duplicate if side == "after" else valid
        )
    invalid = record()
    invalid["verified_on"] = "not-a-date"
    with pytest.raises(ValueError, match="ISO date"):
        compare_catalogs(valid, catalog(invalid))
    invalid = record()
    invalid["version_scope"] = 2
    with pytest.raises(TypeError, match="version_scope"):
        compare_catalogs(valid, catalog(invalid))


def test_conflicting_defaults_remain_visible():
    first, second = record("one"), record("two")
    second.update(path="$HOME/other", version_scope="2.x", verified_on="2020-01-01")
    report = compare_catalogs(catalog(first, second), catalog(first, second))
    assert [c["catalog"] for c in report["potential_default_conflicts"]] == ["before", "after"]
    assert report["potential_default_conflicts"][0]["records"] == [first, second]
    assert "2020-01-01" in render_comparison_markdown(report)
    assert "contributor claims" in report["interpretation"]


def test_cli(tmp_path, capsys):
    before, after = tmp_path / "before.json", tmp_path / "after.json"
    before.write_text(json.dumps(catalog(record())))
    after.write_text(json.dumps(catalog()))
    args = ["--catalog", str(before), "--compare-catalog", str(after)]
    assert main(args + ["--format", "json"]) == 0
    assert len(json.loads(capsys.readouterr().out)["removed"]) == 1
    assert main(args) == 0
    assert "Catalog comparison" in capsys.readouterr().out
    assert main(args + ["--inspect-id", "synthetic"]) == 2
    assert main(args + ["--game", "Fictional"]) == 2
    assert main(["--compare-catalog", str(after)]) == 2
