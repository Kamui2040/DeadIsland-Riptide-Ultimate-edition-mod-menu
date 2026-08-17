"""Deterministic command-line validation surface for the Linux port."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from .archive import (
    ensure_pristine_backup,
    install_candidate,
    restore_backup,
    validate_archive,
)
from .audit import audit_native_game
from .catalog import READY_PATCHES
from .engine import build_candidate
from .errors import DirueError
from .fov_audit import audit_fov_recoil
from .game import validate_game_root
from .preset_audit import audit_presets
from .research import audit_native_research
from .source_map import audit_source_map
from .unresolved_audit import audit_unresolved_presets
from .unresolved_detail import audit_unresolved_details


def _archive_payload(info) -> dict[str, object]:
    return {
        "path": str(info.path),
        "size": info.size,
        "sha256": info.sha256,
        "entry_count": info.entry_count,
    }


def _sha256_arg(value: str) -> str:
    normalized = value.lower()
    if re.fullmatch(r"[0-9a-f]{64}", normalized) is None:
        raise argparse.ArgumentTypeError("expected a 64-character SHA-256 hex digest")
    return normalized


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

    unresolved_parser = subparsers.add_parser(
        "audit-unresolved-presets",
        help="collect sanitized evidence for unresolved hard/spawn/weather parity",
    )
    unresolved_parser.add_argument("root", type=Path)
    unresolved_parser.add_argument(
        "--preset-dir", type=Path, default=Path("Required_files_and_scripts")
    )

    detail_parser = subparsers.add_parser(
        "audit-unresolved-details",
        help="collect whitelisted weather constants and exact native spawn donors",
    )
    detail_parser.add_argument("root", type=Path)
    detail_parser.add_argument(
        "--preset-dir", type=Path, default=Path("Required_files_and_scripts")
    )

    research_parser = subparsers.add_parser(
        "audit-research", help="inspect unresolved native block identities read-only"
    )
    research_parser.add_argument("root", type=Path)

    recoil_parser = subparsers.add_parser(
        "audit-fov-recoil",
        help="collect only native firearm recoil priors needed for FOV parity",
    )
    recoil_parser.add_argument("root", type=Path)

    source_map_parser = subparsers.add_parser(
        "audit-source-map",
        help="correlate released firearm line hints to native semantic context read-only",
    )
    source_map_parser.add_argument("root", type=Path)
    source_map_parser.add_argument("--source", type=Path, default=Path("DIRUE.ahk"))

    candidate_parser = subparsers.add_parser(
        "build-candidate", help="build a disposable validated candidate archive"
    )
    candidate_parser.add_argument("source", type=Path)
    candidate_parser.add_argument("destination", type=Path)
    candidate_parser.add_argument(
        "options",
        nargs="+",
        choices=sorted(READY_PATCHES),
        help="ready semantic options to apply from the source baseline",
    )

    backup_parser = subparsers.add_parser(
        "backup-pristine",
        help="create a validated pristine backup without overwriting an existing one",
    )
    backup_parser.add_argument("live", type=Path)
    backup_parser.add_argument("backup", type=Path)
    backup_parser.add_argument("--expected-live-sha256", type=_sha256_arg)

    install_parser = subparsers.add_parser(
        "install-candidate",
        help="atomically install a validated candidate over its verified source archive",
    )
    install_parser.add_argument("candidate", type=Path)
    install_parser.add_argument("live", type=Path)
    install_parser.add_argument("backup", type=Path)
    install_parser.add_argument(
        "--expected-live-sha256",
        required=True,
        type=_sha256_arg,
    )
    install_parser.add_argument(
        "--expected-candidate-sha256",
        required=True,
        type=_sha256_arg,
    )

    restore_parser = subparsers.add_parser(
        "restore-backup",
        help="atomically restore a validated pristine backup",
    )
    restore_parser.add_argument("backup", type=Path)
    restore_parser.add_argument("live", type=Path)
    restore_parser.add_argument(
        "--expected-backup-sha256",
        required=True,
        type=_sha256_arg,
    )
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
        elif args.command == "audit-unresolved-presets":
            payload = {
                "unresolved_presets": audit_unresolved_presets(
                    args.root,
                    args.preset_dir,
                )
            }
        elif args.command == "audit-unresolved-details":
            payload = {
                "unresolved_details": audit_unresolved_details(
                    args.root,
                    args.preset_dir,
                )
            }
        elif args.command == "audit-research":
            payload = {"research": audit_native_research(args.root)}
        elif args.command == "audit-fov-recoil":
            payload = {"fov_recoil": audit_fov_recoil(args.root)}
        elif args.command == "audit-source-map":
            payload = {"source_map": audit_source_map(args.root, args.source)}
        elif args.command == "build-candidate":
            result = build_candidate(args.source, args.destination, args.options)
            payload = {
                "candidate": {
                    "source_sha256": result.source_sha256,
                    "candidate_sha256": result.candidate_sha256,
                    "entry_count": result.entry_count,
                    "selected_options": list(result.selected_options),
                    "changed_members": list(result.changed_members),
                }
            }
        elif args.command == "backup-pristine":
            payload = {
                "backup": _archive_payload(
                    ensure_pristine_backup(
                        args.live,
                        args.backup,
                        expected_live_sha256=args.expected_live_sha256,
                    )
                )
            }
        elif args.command == "install-candidate":
            payload = {
                "installed": _archive_payload(
                    install_candidate(
                        args.candidate,
                        args.live,
                        args.backup,
                        expected_live_sha256=args.expected_live_sha256,
                        expected_candidate_sha256=args.expected_candidate_sha256,
                    )
                )
            }
        else:
            payload = {
                "restored": _archive_payload(
                    restore_backup(
                        args.backup,
                        args.live,
                        expected_backup_sha256=args.expected_backup_sha256,
                    )
                )
            }
    except DirueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps({"ok": True, **payload}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
