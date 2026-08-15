"""Semantic firearm upgrading definitions reconstructed from source and native audits."""

from __future__ import annotations

from dataclasses import dataclass

from .structured import (
    insert_calls_after_marker_ordinals_in_first_quoted_block,
    replace_call_sequence_in_first_quoted_block,
)

INVENTORY_GEN = "data/inventory_gen.scr"
_UPGRADE_LEVEL_SEQUENCE = ("0", "0", "1", "1", "2", "2", "3", "3")
_TIER_MARKER_ORDINALS = (3, 5, 7)


@dataclass(frozen=True)
class ItemCallSequenceEdit:
    member: str
    item: str
    call_name: str
    expected_arguments: tuple[str, ...]
    desired_arguments: tuple[str, ...]

    def apply(self, text: str) -> str:
        return replace_call_sequence_in_first_quoted_block(
            text,
            block_call="Item",
            block_name=self.item,
            call_name=self.call_name,
            expected_arguments=self.expected_arguments,
            desired_arguments=self.desired_arguments,
        )


@dataclass(frozen=True)
class ItemUpgradeInsertEdit:
    member: str
    item: str
    insertions: tuple[tuple[int, tuple[str, ...]], ...]

    def apply(self, text: str) -> str:
        return insert_calls_after_marker_ordinals_in_first_quoted_block(
            text,
            block_call="Item",
            block_name=self.item,
            marker_call="UpgradeLevel",
            expected_marker_arguments=_UPGRADE_LEVEL_SEQUENCE,
            insertions=self.insertions,
        )


@dataclass(frozen=True)
class FirearmPatchDefinition:
    name: str
    edits: tuple[ItemCallSequenceEdit | ItemUpgradeInsertEdit, ...]


def _tier_insert(
    item: str,
    *,
    shot_times: tuple[str, str, str] | None,
    reload_times: tuple[str, str, str],
) -> ItemUpgradeInsertEdit:
    calls: list[tuple[int, tuple[str, ...]]] = []
    for position, marker_ordinal in enumerate(_TIER_MARKER_ORDINALS):
        tier_calls: list[str] = []
        if shot_times is not None:
            tier_calls.append(f"ShotTime({shot_times[position]});")
        tier_calls.append(f"ReloadTime({reload_times[position]});")
        calls.append((marker_ordinal, tuple(tier_calls)))
    return ItemUpgradeInsertEdit(INVENTORY_GEN, item, tuple(calls))


def _sequence(
    item: str,
    call_name: str,
    expected: tuple[str, ...],
    desired: tuple[str, ...],
) -> ItemCallSequenceEdit:
    return ItemCallSequenceEdit(
        INVENTORY_GEN,
        item,
        call_name,
        expected,
        desired,
    )


_PISTOL_INSERTIONS = (
    _tier_insert(
        "Firearm_ColtGen",
        shot_times=("0.94", "0.88", "0.82"),
        reload_times=("3.8", "3.5", "3.2"),
    ),
    _tier_insert(
        "Firearm_MagnumGen",
        shot_times=("0.96", "0.90", "0.82"),
        reload_times=("3.8", "3.5", "3.2"),
    ),
    _tier_insert(
        "Firearm_M9Gen",
        shot_times=("0.28", "0.27", "0.26"),
        reload_times=("1.2", "1.1", "1.0"),
    ),
    _tier_insert(
        "Firearm_DesertEagleGen",
        shot_times=("0.38", "0.37", "0.36"),
        reload_times=("1.2", "1.1", "1.0"),
    ),
    _tier_insert(
        "Firearm_leg_Mccall9Mm",
        shot_times=("0.28", "0.27", "0.26"),
        reload_times=("1.3", "1.1", "0.9"),
    ),
)

_SHOTGUN_ITEMS = (
    "Firearm_ShotgunShortGen",
    "Firearm_ShotgunGen",
    "Firearm_Shotgun_BGen",
    "Firearm_Shotgun_CGen",
    "Firearm_Shotgun_DGen",
    "Firearm_Shotgun_EGen",
    "Firearm_Shotgun_FGen",
)

_SHOTGUN_INSERTIONS = tuple(
    _tier_insert(
        item,
        shot_times=("1.14", "1.13", "1.12"),
        reload_times=("5.5", "5.0", "4.5"),
    )
    for item in _SHOTGUN_ITEMS
)

_RIFLE_ITEMS = (
    "Firearm_AutoRifleGen",
    "Firearm_AutoRifle_BGen",
    "Firearm_AutoRifle_CGen",
    "Firearm_AutoRifle_DGen",
    "Firearm_AutoRifle_EGen",
    "Firearm_BurstRifleGen",
    "Firearm_BurstRifle_BGen",
    "Firearm_SingleShotRifleGen",
    "Firearm_SingleShotRifle_BGen",
)

_RIFLE_INSERTIONS = tuple(
    _tier_insert(
        item,
        shot_times=None,
        reload_times=("2.95", "2.65", "2.35"),
    )
    for item in _RIFLE_ITEMS
)

_SEQUENCE_EDITS = (
    _sequence(
        "Firearm_ColtGen",
        "ShotTime",
        ("0.6",),
        ("1.0",),
    ),
    _sequence(
        "Firearm_ColtGen",
        "ShootVertRecoil",
        ("0.025", "0.01", "0.01", "0.01", "0.01"),
        ("0.025", "0.01", "0.0095", "0.0090", "0.0085"),
    ),
    _sequence(
        "Firearm_MagnumGen",
        "ShootVertRecoil",
        ("0.025", "0.01", "0.01", "0.01", "0.01"),
        ("0.025", "0.01", "0.048", "0.047", "0.046"),
    ),
    _sequence(
        "Firearm_M9Gen",
        "ShootVertRecoil",
        ("0.025", "0.01", "0.01", "0.01", "0.01"),
        ("0.025", "0.01", "0.008", "0.007", "0.006"),
    ),
    _sequence(
        "Firearm_DesertEagleGen",
        "ShootVertRecoil",
        ("0.025", "0.05", "0.05", "0.05", "0.05"),
        ("0.025", "0.05", "0.012", "0.010", "0.008"),
    ),
    _sequence(
        "Firearm_leg_Mccall9Mm",
        "ShootVertRecoil",
        ("0.025", "0.01", "0.01", "0.01", "0.01"),
        ("0.025", "0.01", "0.008", "0.007", "0.006"),
    ),
) + tuple(
    edit
    for item in (
        "Firearm_AutoRifleGen",
        "Firearm_AutoRifle_BGen",
        "Firearm_AutoRifle_CGen",
        "Firearm_AutoRifle_DGen",
        "Firearm_AutoRifle_EGen",
    )
    for edit in (
        _sequence(
            item,
            "ShootMaxAngle",
            ("0.148", "0.074", "0.074", "0.074", "0.074"),
            ("0.148", "0.074", "0.069", "0.064", "0.059"),
        ),
        _sequence(
            item,
            "ShootVertRecoil",
            ("0.025", "0.02", "0.02", "0.02", "0.02"),
            ("0.025", "0.02", "0.035", "0.030", "0.025"),
        ),
    )
) + tuple(
    _sequence(
        item,
        "ShootVertRecoil",
        ("0.01", "0.015", "0.015", "0.015", "0.015"),
        ("0.01", "0.015", "0.035", "0.030", "0.025"),
    )
    for item in (
        "Firearm_BurstRifleGen",
        "Firearm_BurstRifle_BGen",
        "Firearm_SingleShotRifleGen",
        "Firearm_SingleShotRifle_BGen",
    )
)


# All 157 active edits in the released Better Firearms Upgrading handler are
# represented here: 58 validated sequence replacements and 99 authored
# tier-local insertions. Commented-out rifle ShotTime edits stay excluded.
BETTER_FIREARM_UPGRADING = FirearmPatchDefinition(
    "better_firearm_upgrading",
    _SEQUENCE_EDITS
    + _PISTOL_INSERTIONS
    + _SHOTGUN_INSERTIONS
    + _RIFLE_INSERTIONS,
)

FIREARM_PATCHES = {
    BETTER_FIREARM_UPGRADING.name: BETTER_FIREARM_UPGRADING,
}
