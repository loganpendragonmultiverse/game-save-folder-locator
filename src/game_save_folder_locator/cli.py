from __future__ import annotations

import argparse
import json
import sys
from importlib.resources import files
from pathlib import Path

from .core import OPERATING_SYSTEMS, PATH_TYPES, load_catalog, render_markdown, search


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search sourced game-save path templates.")
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--game")
    parser.add_argument("--os", choices=sorted(OPERATING_SYSTEMS))
    parser.add_argument("--platform")
    parser.add_argument("--path-type", choices=sorted(PATH_TYPES))
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        catalog_path = args.catalog or Path(
            str(files("game_save_folder_locator").joinpath("catalog.json"))
        )
        report = search(
            load_catalog(catalog_path), args.game, args.os, args.platform, args.path_type
        )
        rendered = (
            json.dumps(report, indent=2, ensure_ascii=False) + "\n"
            if args.format == "json"
            else render_markdown(report)
        )
        if args.output:
            if args.output.exists():
                raise ValueError(f"output already exists: {args.output}")
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
