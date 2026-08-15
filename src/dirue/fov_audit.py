"""Compact read-only native recoil layout audit for FOV reconstruction."""

from __future__ import annotations

from pathlib import Path
import re
from zipfile import ZipFile

from .errors import ValidationError
from .game import validate_game_root
from .research import INVENTORY_GEN, _read_text
from .structured import _matching_brace

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

_TIER_RECOIL_RESEARCH_ITEMS = frozenset(FOV_RECOIL_ITEMS[:8])
_PISTOL_RECOIL_ITEMS = frozenset(FOV_RECOIL_ITEMS[8:])
_EXPECTED_UPGRADE_LEVELS = ("0", "0", "1", "1", "2", "2", "3", "3")
_RELEVANT_CALLS = frozenset(
    {"UpgradeLevel", "ShootVertRecoil", "SwayMaxAngle", "ShootMaxAngle"}
)


def _item_block_spans(text: str, item: str) -> list[tuple[int, int, int]]:
    """Return contiguous repeated native Item blocks for one firearm name."""
    header_pattern = re.compile(
        rf'^[ \t]*Item\(\s*"{re.escape(item)}"\s*'
        rf'(?:,[^\r\n)]*)?\)[ \t]*(?:\r?\n[ \t]*)?\{{',
        re.MULTILINE,
    )
    matches = list(header_pattern.finditer(text))
    if len(matches) != len(_EXPECTED_UPGRADE_LEVELS):
        raise ValidationError(
            f"{item}: expected {len(_EXPECTED_UPGRADE_LEVELS)} repeated Item blocks, "
            f"found {len(matches)}"
        )

    spans: list[tuple[int, int, int]] = []
    for match in matches:
        open_index = text.find("{", match.start(), match.end())
        if open_index < 0:
            raise ValidationError(f"{item}: opening brace not found")
        try:
            close_index = _matching_brace(text, open_index)
        except Exception as exc:
            raise ValidationError(f"{item}: malformed Item block") from exc
        line_number = text.count("\n", 0, match.start()) + 1
        spans.append((match.start(), close_index + 1, line_number))

    any_item_header = re.compile(r'^[ \t]*Item\s*\(', re.MULTILINE)
    for (_, previous_end, _), (next_start, _, _) in zip(spans, spans[1:]):
        if next_start < previous_end:
            raise ValidationError(f"{item}: overlapping repeated Item blocks")
        if any_item_header.search(text[previous_end:next_start]):
            raise ValidationError(f"{item}: repeated Item blocks are not contiguous")

    return spans


def _active_relevant_calls(block: str, header_line: int) -> list[dict[str, object]]:
    pattern = re.compile(
        r'^(?![ \t]*//)[ \t]*(?P<call>[A-Za-z_][A-Za-z0-9_]*)'
        r'\(\s*(?P<args>[^\r\n)]*?)\s*\)\s*;?[ \t]*'
        r'(?://[^\r\n]*)?(?P<cr>\r?)$',
        re.MULTILINE,
    )
    calls: list[dict[str, object]] = []
    for match in pattern.finditer(block):
        call_name = match.group("call")
        if call_name not in _RELEVANT_CALLS:
            continue
        calls.append(
            {
                "call": call_name,
                "arguments": match.group("args").strip()[:160],
                "line_number": header_line + block.count("\n", 0, match.start()),
            }
        )
    return calls


def recoil_layouts(text: str) -> dict[str, dict[str, object]]:
    """Report repeated-block recoil/sway layout without assuming Windows call counts."""
    result: dict[str, dict[str, object]] = {}
    for item in FOV_RECOIL_ITEMS:
        blocks: list[dict[str, object]] = []
        recoil_sites: list[dict[str, object]] = []
        sway_sites: list[dict[str, object]] = []
        shoot_max_angle_sites: list[dict[str, object]] = []

        for ordinal, (start, end, header_line) in enumerate(
            _item_block_spans(text, item), 1
        ):
            block = text[start:end]
            calls = _active_relevant_calls(block, header_line)
            upgrades = [call for call in calls if call["call"] == "UpgradeLevel"]
            if len(upgrades) != 1:
                raise ValidationError(
                    f"{item} block {ordinal}: expected 1 active UpgradeLevel call, "
                    f"found {len(upgrades)}"
                )

            blocks.append(
                {
                    "item_block_ordinal": ordinal,
                    "line_number": header_line,
                    "upgrade_level": upgrades[0]["arguments"],
                }
            )
            for call in calls:
                if call["call"] == "UpgradeLevel":
                    continue
                site = {
                    "item_block_ordinal": ordinal,
                    "line_number": call["line_number"],
                    "arguments": call["arguments"],
                }
                if call["call"] == "ShootVertRecoil":
                    recoil_sites.append(site)
                elif call["call"] == "SwayMaxAngle":
                    sway_sites.append(site)
                elif call["call"] == "ShootMaxAngle":
                    shoot_max_angle_sites.append(site)

        levels = tuple(str(block["upgrade_level"]) for block in blocks)
        if levels != _EXPECTED_UPGRADE_LEVELS:
            raise ValidationError(
                f"{item}: expected UpgradeLevel sequence {_EXPECTED_UPGRADE_LEVELS!r}, "
                f"found {levels!r}"
            )

        expected_recoil_count = 1 if item in _TIER_RECOIL_RESEARCH_ITEMS else 5
        if len(recoil_sites) != expected_recoil_count:
            raise ValidationError(
                f"{item}: expected {expected_recoil_count} active ShootVertRecoil "
                f"call(s), found {len(recoil_sites)}"
            )
        if len(sway_sites) != 4:
            raise ValidationError(
                f"{item}: expected 4 active SwayMaxAngle calls, found {len(sway_sites)}"
            )

        result[item] = {
            "blocks": blocks,
            "upgrade_levels": list(levels),
            "recoil_sites": recoil_sites,
            "sway_sites": sway_sites,
            "shoot_max_angle_sites": shoot_max_angle_sites,
            "research_class": (
                "tier_recoil_insertion_candidate"
                if item in _TIER_RECOIL_RESEARCH_ITEMS
                else "existing_five_recoil_sequence"
            ),
        }

    if set(result) != set(FOV_RECOIL_ITEMS):
        raise ValidationError("FOV recoil audit item set mismatch")
    if _TIER_RECOIL_RESEARCH_ITEMS | _PISTOL_RECOIL_ITEMS != frozenset(FOV_RECOIL_ITEMS):
        raise ValidationError("FOV recoil audit item classification mismatch")
    return result


def audit_fov_recoil(root: Path) -> dict[str, object]:
    """Read only the native inventory member needed to finish FOV recoil parity."""
    game = validate_game_root(root)
    with ZipFile(game.data0, "r") as archive:
        inventory_gen = _read_text(archive, INVENTORY_GEN)
    return {
        "archive_sha256": game.archive.sha256,
        "member": INVENTORY_GEN,
        "items": recoil_layouts(inventory_gen),
    }
