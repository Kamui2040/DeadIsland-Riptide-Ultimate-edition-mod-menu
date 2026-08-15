"""Compact read-only native recoil audit for FOV reconstruction."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

from .errors import ValidationError
from .game import validate_game_root
from .research import INVENTORY_GEN, _read_text, firearm_items

FOV_RECOIL_ITEMS = (
    "Firearm_ShotgunShortGen",
    "Firearm_ShotgunGen",
    "Firearm_Shotgun_BGen",
    "Firearm_Shotgun_CGen",
    "Firearm_Shotgun_DGen",
    "Firearm_Shotgun_EGen",
    "Firearm_Shotgun_FGen",
    "Firearm_leg_CrowdPleaser",
    "Firearm_ColtGen",
    "Firearm_MagnumGen",
    "Firearm_M9Gen",
    "Firearm_DesertEagleGen",
    "Firearm_leg_Mccall9Mm",
)


def recoil_sequences(text: str) -> dict[str, list[str]]:
    """Return the five active ShootVertRecoil values for each FOV target item."""
    items = firearm_items(text)
    result: dict[str, list[str]] = {}
    for item in FOV_RECOIL_ITEMS:
        key = f"Item:{item}"
        entries = items.get(key)
        if entries is None:
            raise ValidationError(f"missing FOV recoil item {item}")
        values = [
            str(entry["arguments"])
            for entry in entries
            if entry["call"] == "ShootVertRecoil"
        ]
        if len(values) != 5:
            raise ValidationError(
                f"{item}: expected 5 active ShootVertRecoil calls, found {len(values)}"
            )
        result[item] = values
    return result


def audit_fov_recoil(root: Path) -> dict[str, object]:
    """Read only the native inventory member needed to finish FOV recoil parity."""
    game = validate_game_root(root)
    with ZipFile(game.data0, "r") as archive:
        inventory_gen = _read_text(archive, INVENTORY_GEN)
    return {
        "archive_sha256": game.archive.sha256,
        "member": INVENTORY_GEN,
        "items": recoil_sequences(inventory_gen),
    }
