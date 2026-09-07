from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

OPERATING_SYSTEMS = {"windows", "macos", "linux", "android", "ios", "other"}
PATH_TYPES = {"local", "cloud-cache", "configuration-dependent"}
FIELDS = ("id", "game", "os", "platform", "path_type", "path", "source", "verified_on")


def load_catalog(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("catalog must be a version 1 object")
    records = data.get("records")
    if not isinstance(records, list):
        raise TypeError("records must be a list")
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise TypeError("each record must be an object")
        for field in FIELDS:
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise ValueError(f"each record requires non-empty text field: {field}")
        if record["id"] in seen:
            raise ValueError(f"duplicate record id: {record['id']}")
        seen.add(record["id"])
        if record["os"] not in OPERATING_SYSTEMS:
            raise ValueError(f"record {record['id']} has an invalid operating system")
        if record["path_type"] not in PATH_TYPES:
            raise ValueError(f"record {record['id']} has an invalid path type")
        parsed = urlparse(record["source"])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"record {record['id']} requires an HTTP source URL")
        try:
            date.fromisoformat(record["verified_on"])
        except ValueError as exc:
            raise ValueError(f"record {record['id']} verified_on must be an ISO date") from exc
        if "notes" in record and not isinstance(record["notes"], str):
            raise TypeError(f"record {record['id']} notes must be text")
    return data


def search(
    data: dict[str, Any],
    game: str | None = None,
    operating_system: str | None = None,
    platform: str | None = None,
    path_type: str | None = None,
) -> dict[str, Any]:
    if operating_system is not None and operating_system not in OPERATING_SYSTEMS:
        raise ValueError(f"unknown operating system: {operating_system}")
    if path_type is not None and path_type not in PATH_TYPES:
        raise ValueError(f"unknown path type: {path_type}")
    records = []
    for record in data["records"]:
        if game is not None and game.casefold() not in record["game"].casefold():
            continue
        if operating_system is not None and record["os"] != operating_system:
            continue
        if platform is not None and record["platform"].casefold() != platform.casefold():
            continue
        if path_type is not None and record["path_type"] != path_type:
            continue
        records.append(record)
    return {"version": 1, "record_count": len(records), "records": records}


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Game Save Folder Locations",
        "",
        f"Matching records: **{report['record_count']}**",
        "",
    ]
    for record in report["records"]:
        lines.extend(
            [
                f"## {record['game']}",
                "",
                f"- OS: {record['os']}",
                f"- Platform/store: {record['platform']}",
                f"- Path type: {record['path_type']}",
                f"- Path template: `{record['path']}`",
                f"- Verified on: {record['verified_on']}",
                f"- Source: {record['source']}",
            ]
        )
        if record.get("notes"):
            lines.append(f"- Notes: {record['notes']}")
        if record.get("version_scope"):
            lines.append(f"- Version scope: {record['version_scope']}")
        if record.get("confidence"):
            lines.append(f"- Confidence: {record['confidence']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
