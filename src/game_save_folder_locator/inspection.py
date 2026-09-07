"""Explicit path expansion and opt-in directory existence checks only."""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path
from typing import Any


def inspect_record(
    record: dict[str, Any], *, confirmed: bool, as_of: str, variables: dict[str, str] | None = None
) -> dict[str, Any]:
    home = str(Path.home())
    values = (
        variables
        if variables is not None
        else {
            "HOME": home,
            "APPDATA": os.environ.get("APPDATA", ""),
            "XDG_CONFIG_HOME": os.environ.get("XDG_CONFIG_HOME") or str(Path(home) / ".config"),
            "XDG_DATA_HOME": os.environ.get("XDG_DATA_HOME") or str(Path(home) / ".local/share"),
        }
    )
    template = record["path"]
    if template.startswith("~/"):
        template = "$HOME/" + template[2:]

    def substitute(match: re.Match[str]) -> str:
        key = match.group(1) or match.group(2)
        if key not in {"HOME", "APPDATA", "XDG_CONFIG_HOME", "XDG_DATA_HOME"} or not values.get(
            key
        ):
            raise ValueError(f"Path variable {key} is unavailable")
        return values[key]

    expanded = re.sub(r"%([A-Z_]+)%|\$([A-Z_]+)", substitute, template)
    if any(char in expanded for char in "*?<>$%") or expanded.startswith(("\\\\", "//")):
        raise ValueError("Only explicit local paths are supported; no wildcards or network paths")
    path = Path(expanded)
    if not path.is_absolute() or ".." in path.parts:
        raise ValueError("Expanded path must be absolute without parent traversal")
    age = (date.fromisoformat(as_of) - date.fromisoformat(record["verified_on"])).days
    if age < 0:
        raise ValueError("as_of predates the source verification")
    return {
        "id": record["id"],
        "expanded_path": str(path),
        "checked": confirmed,
        "directory_exists": path.is_dir() if confirmed else None,
        "source_age_days": age,
        "source_review": "stale" if age > 180 else "recent",
        "confidence": "Directory presence does not prove that the game actively uses this location.",
        "operation": "Directory existence only; no save files read or modified.",
    }
