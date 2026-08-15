"""Read-only block-aware research helpers for unresolved native parity work."""

from __future__ import annotations

from pathlib import Path
import re
from zipfile import ZipFile

from .errors import ValidationError
from .game import validate_game_root

CAR_PHYSICS = "data/odephysics/vehicle/cardi.phx"
OLD_BOAT_PHYSICS = "data/odephysics/vehicle/old_boat_a.phx"
INVENTORY_GEN = "data/inventory_gen.scr"
INVENTORY_SPECIAL = "data/inventory_special.scr"

FIREARM_CALLS = (
    "UpgradeLevel",
    "ShotTime",
    "ReloadTime",
    "ShootVertRecoil",
    "ShootMaxAngle",
    "AimBlurStart",
    "HolderOffset",
    "HandOffset",
    "HandRot",
    "AimFov",
    "SwayMaxAngle",
)


def _safe_header(header: str) -> str:
    clean = header.split("//", 1)[0].strip()
    call = re.search(
        r'(?P<kind>[A-Za-z_][A-Za-z0-9_]*)\s*\(\s*"(?P<name>[^"]+)"',
        clean,
    )
    if call:
        return f'{call.group("kind")}:{call.group("name")}'
    quoted = re.search(r'"(?P<name>[^"]+)"', clean)
    if quoted:
        return quoted.group("name")[:120]
    return clean[:120]


def _brace_paths(lines: list[str]) -> list[tuple[str, ...]]:
    paths: list[tuple[str, ...]] = []
    stack: list[str] = []
    previous = ""
    for line in lines:
        stripped = line.strip()
        code = line.split("//", 1)[0]
        for _ in range(min(code.count("}"), len(stack))):
            stack.pop()
        paths.append(tuple(stack))
        opening = code.count("{")
        if opening:
            before = code.split("{", 1)[0].strip()
            safe = _safe_header(before or previous)
            for _ in range(opening):
                stack.append(safe)
        if stripped and not stripped.startswith("//") and stripped not in {"{", "}"}:
            previous = stripped
    return paths


def call_sites(text: str, call_name: str) -> list[dict[str, object]]:
    """Return active call arguments, line numbers, and block identities."""
    lines = text.splitlines()
    paths = _brace_paths(lines)
    pattern = re.compile(
        rf'^(?!\s*//)\s*{re.escape(call_name)}\(\s*(?P<args>[^)]*?)\s*\)'
    )
    ordinals: dict[tuple[str, ...], int] = {}
    result: list[dict[str, object]] = []
    for index, line in enumerate(lines):
        match = pattern.search(line)
        if not match:
            continue
        path = paths[index]
        ordinals[path] = ordinals.get(path, 0) + 1
        result.append(
            {
                "line_number": index + 1,
                "block_path": list(path),
                "ordinal_in_block": ordinals[path],
                "arguments": match.group("args").strip()[:160],
            }
        )
    return result


def firearm_items(text: str) -> dict[str, list[dict[str, object]]]:
    """Group relevant firearm calls by actual native `Item:` block identity."""
    lines = text.splitlines()
    paths = _brace_paths(lines)
    pattern = re.compile(
        r'^(?!\s*//)\s*(?P<call>[A-Za-z_][A-Za-z0-9_]*)'
        r'\(\s*(?P<args>[^)]*?)\s*\)'
    )
    result: dict[str, list[dict[str, object]]] = {}
    per_call_ordinals: dict[tuple[str, str], int] = {}
    for index, line in enumerate(lines):
        match = pattern.search(line)
        if not match or match.group("call") not in FIREARM_CALLS:
            continue
        item = next(
            (part for part in reversed(paths[index]) if part.startswith("Item:")),
            None,
        )
        if item is None:
            continue
        call_name = match.group("call")
        ordinal_key = (item, call_name)
        per_call_ordinals[ordinal_key] = per_call_ordinals.get(ordinal_key, 0) + 1
        result.setdefault(item, []).append(
            {
                "line_number": index + 1,
                "block_path": list(paths[index]),
                "call": call_name,
                "ordinal_for_call": per_call_ordinals[ordinal_key],
                "arguments": match.group("args").strip()[:160],
            }
        )
    return dict(sorted(result.items()))


def _read_text(archive: ZipFile, member: str) -> str:
    try:
        data = archive.read(member)
    except KeyError as exc:
        raise ValidationError(f"missing required research member {member}") from exc
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"cannot decode required research member {member}") from exc


def audit_native_research(root: Path) -> dict[str, object]:
    """Collect unresolved block identities from native Data0 without modifying it."""
    game = validate_game_root(root)
    with ZipFile(game.data0, "r") as archive:
        car = _read_text(archive, CAR_PHYSICS)
        boat = _read_text(archive, OLD_BOAT_PHYSICS)
        inventory_gen = _read_text(archive, INVENTORY_GEN)
        inventory_special = _read_text(archive, INVENTORY_SPECIAL)
        return {
            "archive_sha256": game.archive.sha256,
            "vehicle_ignore_sites": {
                "car": call_sites(car, "Ignore"),
                "old_boat": call_sites(boat, "Ignore"),
            },
            "firearm_items": {
                "inventory_gen": firearm_items(inventory_gen),
                "inventory_special": firearm_items(inventory_special),
            },
        }
