import copy
import json
from pathlib import Path

import pytest

from game_save_folder_locator.cli import main
from game_save_folder_locator.comparison import compare_catalogs
from game_save_folder_locator.core import validate_catalog
from game_save_folder_locator.inspection import inspect_record


def catalog():
    return {
        "version": 1,
        "records": [
            {
                "id": "synthetic",
                "game": "Fictional",
                "os": "linux",
                "platform": "manual",
                "path_type": "local",
                "path": "$HOME/saves",
                "source": "https://example.org/docs",
                "verified_on": "2026-10-16",
            }
        ],
    }


@pytest.mark.parametrize("version", [True, 1.0, "1"])
def test_version_is_integer(version):
    data = catalog()
    data["version"] = version
    with pytest.raises(ValueError, match="version 1"):
        validate_catalog(data)


@pytest.mark.parametrize("date", ["20261016", "2026-W42-5", "2026-02-30"])
def test_catalog_dates_are_consistent(date):
    data = catalog()
    data["records"][0]["verified_on"] = date
    with pytest.raises(ValueError, match="ISO date"):
        validate_catalog(data)


@pytest.mark.parametrize(
    "url",
    [
        "http://@/docs",
        "https://reader:example@example.org/docs",
        "https://example.org:bad/docs",
        "https://example.org:0/docs",
    ],
)
def test_sources_have_usable_host_and_no_embedded_credentials(url):
    data = catalog()
    data["records"][0]["source"] = url
    with pytest.raises(ValueError):
        validate_catalog(data)


def test_confidence_requires_text():
    data = catalog()
    data["records"][0]["confidence"] = True
    with pytest.raises(TypeError, match="confidence"):
        validate_catalog(data)


@pytest.mark.parametrize("template", ["$HOME2/saves", "$HOMEcustom/saves", "%HOMEcustom%/saves"])
def test_variable_names_are_not_partially_expanded(tmp_path, template):
    row = {**catalog()["records"][0], "path": template}
    with pytest.raises(ValueError, match="unavailable"):
        inspect_record(row, confirmed=False, as_of="2026-10-20", variables={"HOME": str(tmp_path)})


def test_preview_remains_unchecked_and_confirmed_permission_is_error(tmp_path, monkeypatch):
    row = catalog()["records"][0]
    original = Path.stat
    target = tmp_path / "saves"

    def denied(path, *args, **kwargs):
        if path == target:
            raise PermissionError("synthetic")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", denied)
    variables = {"HOME": str(tmp_path)}
    assert (
        inspect_record(row, confirmed=False, as_of="2026-10-20", variables=variables)[
            "directory_exists"
        ]
        is None
    )
    with pytest.raises(PermissionError):
        inspect_record(row, confirmed=True, as_of="2026-10-20", variables=variables)
    with pytest.raises(TypeError, match="boolean"):
        inspect_record(row, confirmed="false", as_of="2026-10-20", variables=variables)


def test_absent_selected_directory_and_date_preview(tmp_path):
    row = catalog()["records"][0]
    variables = {"HOME": str(tmp_path)}
    assert not inspect_record(row, confirmed=True, as_of="2026-10-20", variables=variables)[
        "directory_exists"
    ]
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        inspect_record(row, confirmed=False, as_of="20261020", variables=variables)
    with pytest.raises(ValueError, match="predates"):
        inspect_record(row, confirmed=False, as_of="2020-01-01", variables=variables)


def test_nested_json_type_changes_are_not_lost():
    before = catalog()
    before["records"][0]["extension"] = {"values": [True, {"version": 1}]}
    after = copy.deepcopy(before)
    after["records"][0]["extension"]["values"][0] = 1
    report = compare_catalogs(before, after)
    assert report["changed"][0]["fields"] == ["extension"]
    assert report["unchanged_ids"] == []
    assert before["records"][0]["extension"]["values"][0] is True


def test_report_race_and_dangling_link_preserve_destinations(tmp_path, monkeypatch):
    source = tmp_path / "catalog.json"
    source.write_text(json.dumps(catalog()))
    output = tmp_path / "report.json"
    original = Path.open

    def raced(path, mode="r", *args, **kwargs):
        if path == output and mode == "x":
            with original(path, "w") as stream:
                stream.write("keep")
        return original(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", raced)
    assert main(["--catalog", str(source), "--output", str(output)]) == 2
    assert output.read_text() == "keep"
    link = tmp_path / "link.json"
    missing = tmp_path / "missing"
    try:
        link.symlink_to(missing)
    except OSError:
        pytest.skip("symlinks unavailable")
    assert main(["--catalog", str(source), "--output", str(link)]) == 2
    assert link.is_symlink() and not missing.exists()
