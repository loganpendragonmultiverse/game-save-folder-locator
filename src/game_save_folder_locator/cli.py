from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path

from .comparison import compare_catalogs, render_comparison_markdown
from .core import OPERATING_SYSTEMS, PATH_TYPES, load_catalog, render_markdown, search
from .inspection import inspect_record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search sourced game-save path templates.")
    parser.add_argument("--catalog", type=Path)
    parser.add_argument(
        "--compare-catalog",
        type=Path,
        help="Compare supplied catalog against --catalog by stable ID",
    )
    parser.add_argument("--game")
    parser.add_argument("--os", choices=sorted(OPERATING_SYSTEMS))
    parser.add_argument("--platform")
    parser.add_argument("--path-type", choices=sorted(PATH_TYPES))
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--inspect-id", help="Expand one explicitly selected record")
    parser.add_argument(
        "--confirm-path-check", action="store_true", help="Check only that directory's existence"
    )
    parser.add_argument("--as-of", default=datetime.now(timezone.utc).date().isoformat())
    args = parser.parse_args(argv)
    try:
        catalog_path = args.catalog or Path(
            str(files("game_save_folder_locator").joinpath("catalog.json"))
        )
        if args.compare_catalog:
            if not args.catalog:
                raise ValueError("--compare-catalog requires an explicit --catalog baseline")
            if any(
                (
                    args.game,
                    args.os,
                    args.platform,
                    args.path_type,
                    args.inspect_id,
                    args.confirm_path_check,
                )
            ):
                raise ValueError(
                    "catalog comparison cannot combine with search or inspection flags"
                )
            report = compare_catalogs(
                load_catalog(catalog_path), load_catalog(args.compare_catalog)
            )
        else:
            report = search(
                load_catalog(catalog_path), args.game, args.os, args.platform, args.path_type
            )
        if args.confirm_path_check and not args.inspect_id:
            raise ValueError("--confirm-path-check requires --inspect-id")
        if args.inspect_id:
            matching = [record for record in report["records"] if record["id"] == args.inspect_id]
            if len(matching) != 1:
                raise ValueError(
                    "inspect-id must identify one record within the selected catalog filters"
                )
            local_os = {"win32": "windows", "darwin": "macos", "linux": "linux"}.get(sys.platform)
            if matching[0]["os"] != local_os:
                raise ValueError("Path inspection requires a record for this operating system")
            report["inspection"] = inspect_record(
                matching[0], confirmed=args.confirm_path_check, as_of=args.as_of
            )
        rendered = (
            json.dumps(report, indent=2, ensure_ascii=False) + "\n"
            if args.format == "json"
            else (
                render_comparison_markdown(report)
                if args.compare_catalog
                else render_markdown(report)
            )
        )
        if args.format == "markdown" and "inspection" in report:
            rendered += (
                "\n## Selected path inspection\n\n```json\n"
                + json.dumps(report["inspection"], indent=2)
                + "\n```\n"
            )
        if args.output:
            if args.output.exists() or args.output.is_symlink():
                raise ValueError(f"output already exists: {args.output}")
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(rendered)
        else:
            sys.stdout.write(rendered)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
