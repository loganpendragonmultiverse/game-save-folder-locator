"""Report supplied catalog differences without expanding or checking any path."""

from __future__ import annotations

import copy
import json
from typing import Any

from .core import validate_catalog


def _same_json(left: Any, right: Any) -> bool:
    return json.dumps(left, sort_keys=True, ensure_ascii=False) == json.dumps(
        right, sort_keys=True, ensure_ascii=False
    )


def compare_catalogs(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    old = {record["id"]: record for record in validate_catalog(before)["records"]}
    new = {record["id"]: record for record in validate_catalog(after)["records"]}
    changed = []
    for record_id in sorted(old.keys() & new.keys()):
        fields = sorted(
            key
            for key in old[record_id].keys() | new[record_id].keys()
            if not _same_json(old[record_id].get(key), new[record_id].get(key))
            or (key in old[record_id]) != (key in new[record_id])
        )
        if fields:
            changed.append(
                {
                    "id": record_id,
                    "fields": fields,
                    "before": old[record_id],
                    "after": new[record_id],
                }
            )
    conflicts = []
    for side, records in (("before", old), ("after", new)):
        groups: dict[tuple[str, ...], list[dict[str, Any]]] = {}
        for record in records.values():
            key = (
                record["game"].casefold(),
                record["os"],
                record["platform"].casefold(),
                record["path_type"],
            )
            groups.setdefault(key, []).append(record)
        for group_key in sorted(groups):
            members = sorted(groups[group_key], key=lambda record: record["id"])
            if len({record["path"] for record in members}) > 1:
                conflicts.append({"catalog": side, "records": members})
    return copy.deepcopy(
        {
            "version": 1,
            "operation": "catalog-comparison",
            "added": [new[key] for key in sorted(new.keys() - old.keys())],
            "removed": [old[key] for key in sorted(old.keys() - new.keys())],
            "changed": changed,
            "unchanged_ids": sorted(
                key for key in old.keys() & new.keys() if _same_json(old[key], new[key])
            ),
            "potential_default_conflicts": conflicts,
            "interpretation": "Dates and sources are contributor claims. Conflicting templates "
            "may describe different versions or configurations; review both. "
            "No paths expanded or checked and no sources fetched.",
        }
    )


def render_comparison_markdown(report: dict[str, Any]) -> str:
    lines = ["# Catalog comparison", "", report["interpretation"], ""]
    for label in ("added", "removed", "changed", "potential_default_conflicts"):
        lines.extend(
            [
                f"## {label.replace('_', ' ').title()}",
                "",
                f"Count: {len(report[label])}",
                "",
                "```json",
                json.dumps(report[label], indent=2, ensure_ascii=False),
                "```",
                "",
            ]
        )
    lines.append(f"Unchanged records: {len(report['unchanged_ids'])}")
    return "\n".join(lines) + "\n"
