"""Deterministic command-line validation surface for the Linux port."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .archive import validate_archive
from .audit import audit_native_game
from .errors import DirueError
from .game import validate_game_root
from .preset_audit import audit_presets
from .research import audit_native_research


def _archive_payload(info) -> dict[str, object]:
    return {
        "path": str(info.path),
        "size": info.size,
        "sha256": info.sha256,
        "entry_count": info.entry_count,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dirue")
    subparsers = parser.add_subparsers(dest="command", required=True)

    archive_parser = subparsers.add_parser(
        "validate-archive", help="validate a ZIP-compatible Data0 archive"
    )
    archive_parser.add_argument("path", type=Path)

    game_parser = subparsers.add_parser(
        "validate-game", help="validate a native Linux DIRDE game root"
    )
    game_parser.add_argument("root", type=Path)

    audit_parser = subparsers.add_parser(
        "audit-native", help="run a read-only native Data0 parity audit"
    )
    audit_parser.add_argument("root", type=Path)

    preset_parser = subparsers.add_parser(
        "audit-presets", help="compare released preset ZIPs to native Data0 read-only"
    )
    preset_parser.add_argument("root", type=Path)
    preset_parser.add_argument(
        "--preset-dir", type=Path, default=Path("Required_files_and_scripts")
    )

    research_parser = subparsers.add_parser(
        "audit-research", help="inspect unresolved native block identities read-only"
    )
    research_parser.add_argument("root", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate-archive":
            payload = _archive_payload(validate_archive(args.path))
        elif args.command == "validate-game":
            game = validate_game_root(args.root)
            payload = {
                "root": str(game.root),
                "executable": str(game.executable),
                "data0": _archive_payload(game.archive),
            }
        elif args.command == "audit-native":
            payload = {"audit": audit_native_game(args.root)}
        elif args.command == "audit-presets":
            payload = {"presets": audit_presets(args.root, args.preset_dir)}
        else:
            payload = {"research": audit_native_research(args.root)}
    except DirueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps({"ok": True, **payload}, sort_keys=True))
    return 0
