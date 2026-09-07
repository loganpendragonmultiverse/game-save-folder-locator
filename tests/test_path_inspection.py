import json
import sys
from importlib.resources import files

import pytest

from game_save_folder_locator.cli import main
from game_save_folder_locator.core import load_catalog
from game_save_folder_locator.inspection import inspect_record


def test_bundled_catalog_has_sources_and_version_scope() -> None:
    from pathlib import Path

    data = load_catalog(Path(str(files("game_save_folder_locator").joinpath("catalog.json"))))
    assert len(data["records"]) == 9
    assert len({record["game"] for record in data["records"]}) == 3
    assert all(record["version_scope"] and record["confidence"] for record in data["records"])


def test_preview_does_not_stat_target_until_confirmed(tmp_path, monkeypatch) -> None:
    from pathlib import Path

    record = {"id": "fixture", "path": "~/saves", "verified_on": "2026-09-07"}
    variables = {"HOME": str(tmp_path)}
    original = Path.is_dir

    def forbidden(_):
        raise AssertionError("Unconfirmed preview must not inspect the target")

    monkeypatch.setattr(Path, "is_dir", forbidden)
    result = inspect_record(record, confirmed=False, as_of="2026-09-07", variables=variables)
    assert result["directory_exists"] is None
    monkeypatch.setattr(Path, "is_dir", original)
    (tmp_path / "saves").mkdir()
    result = inspect_record(record, confirmed=True, as_of="2027-09-07", variables=variables)
    assert result["directory_exists"] and result["source_review"] == "stale"
    assert not list((tmp_path / "saves").iterdir())


@pytest.mark.parametrize(
    "template", ["%MISSING%/saves", "relative/path", "~/../other", "//server/share", "~/save*"]
)
def test_unsupported_templates_fail_closed(tmp_path, template) -> None:
    with pytest.raises(ValueError):
        inspect_record(
            {"id": "x", "path": template, "verified_on": "2026-09-07"},
            confirmed=True,
            as_of="2026-09-07",
            variables={"HOME": str(tmp_path)},
        )


def test_cli_selected_record_only(tmp_path, monkeypatch, capsys) -> None:
    os_name = {"win32": "windows", "linux": "linux", "darwin": "macos"}[sys.platform]
    monkeypatch.setenv("APPDATA", str(tmp_path))
    key = f"factorio-{os_name}"
    assert main(["--inspect-id", key, "--as-of", "2026-09-07", "--format", "json"]) == 0
    assert not json.loads(capsys.readouterr().out)["inspection"]["checked"]
    assert main(["--confirm-path-check"]) == 2
    assert main(["--inspect-id", "missing"]) == 2
    foreign = "linux" if os_name == "windows" else "windows"
    assert main(["--inspect-id", f"factorio-{foreign}"]) == 2
