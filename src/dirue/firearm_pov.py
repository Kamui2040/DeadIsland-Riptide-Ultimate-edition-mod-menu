"""Semantic Better Firearms POV definitions reconstructed from source and native audits."""

from __future__ import annotations

from dataclasses import dataclass

from .firearm_structured import replace_unique_call_in_first_quoted_block
from .structured import replace_call_sequence_in_first_quoted_block

INVENTORY_GEN = "data/inventory_gen.scr"
INVENTORY_SPECIAL = "data/inventory_special.scr"


@dataclass(frozen=True)
class PovCallSequenceEdit:
    member: str
    item: str
    call_name: str
    expected_arguments: tuple[str, ...]
    desired_arguments: tuple[str, ...]
    source_target_count: int

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
class PovCallTypeEdit:
    member: str
    item: str
    expected_call: str
    expected_argument: str
    desired_call: str
    desired_argument: str
    source_target_count: int = 1

    def apply(self, text: str) -> str:
        return replace_unique_call_in_first_quoted_block(
            text,
            block_call="Item",
            block_name=self.item,
            expected_call=self.expected_call,
            expected_argument=self.expected_argument,
            desired_call=self.desired_call,
            desired_argument=self.desired_argument,
        )


PovEdit = PovCallSequenceEdit | PovCallTypeEdit


@dataclass(frozen=True)
class PovPatchDefinition:
    name: str
    edits: tuple[PovEdit, ...]

    @property
    def source_target_count(self) -> int:
        return sum(edit.source_target_count for edit in self.edits)


def _sequence(
    item: str,
    call_name: str,
    expected: tuple[str, ...],
    desired: tuple[str, ...],
    *,
    source_target_count: int,
    member: str = INVENTORY_GEN,
) -> PovCallSequenceEdit:
    return PovCallSequenceEdit(
        member,
        item,
        call_name,
        expected,
        desired,
        source_target_count,
    )


def _call_type(
    item: str,
    expected_argument: str,
    desired_argument: str,
    *,
    member: str = INVENTORY_GEN,
) -> PovCallTypeEdit:
    return PovCallTypeEdit(
        member,
        item,
        "HolderOffset",
        expected_argument,
        "HandOffset",
        desired_argument,
    )


_PISTOL_HAND_PRIORS = {
    "Firearm_ColtGen": (
        "HandModification_Normal, [-0.050,-0.050,0.0]",
        "HandModification_Custom, [-0.050,-0.050,0.0]",
        "HandModification_Normal, [0.000625,0.0,0.070]",
    ) * 4,
    "Firearm_MagnumGen": (
        "HandModification_Normal, [-0.050,-0.050,0.0]",
        "HandModification_Custom, [-0.050,-0.050,0.0]",
        "HandModification_Normal, [0.00125,0.00125,0.160]",
    ) * 4,
    "Firearm_M9Gen": (
        "HandModification_Normal, [-0.030,-0.030,0.0]",
        "HandModification_Custom, [-0.030,-0.030,0.0]",
        "HandModification_Normal, [0.0,0.0,0.070]",
    ) * 4,
    "Firearm_DesertEagleGen": (
        "HandModification_Normal, [-0.020,-0.030,0.0]",
        "HandModification_Custom, [-0.020,-0.030,0.0]",
        "HandModification_Normal, [0.000625,-0.005,0.070]",
    ) * 4,
    "Firearm_leg_Mccall9Mm": (
        "HandModification_Normal, [-0.030,-0.030,0.0]",
        "HandModification_Custom, [-0.030,-0.030,0.0]",
        "HandModification_Normal, [0.0,0.0,0.070]",
    ) * 4,
}

_PISTOL_AIMED_OFFSETS = {
    62: {
        "Firearm_ColtGen": ("HandModification_Normal, [0.000625,0.0,0.070]",) * 4,
        "Firearm_MagnumGen": ("HandModification_Normal, [0.000625,0.0,0.070]",) * 4,
        "Firearm_M9Gen": ("HandModification_Normal, [0.0,0.0,0.120]",) * 4,
        "Firearm_DesertEagleGen": (
            "HandModification_Normal, [0.000625,-0.005,0.120]",
        ) * 4,
        "Firearm_leg_Mccall9Mm": ("HandModification_Normal, [0.0,0.0,0.120]",) * 4,
    },
    72: {
        "Firearm_ColtGen": ("HandModification_Normal, [0.000625,0.0,0.030]",) * 4,
        "Firearm_MagnumGen": ("HandModification_Normal, [0.000625,0.0,0.030]",) * 4,
        "Firearm_M9Gen": ("HandModification_Normal, [0.0,0.0,0.070]",) * 4,
        "Firearm_DesertEagleGen": (
            "HandModification_Normal, [0.000625,-0.005,0.070]",
        ) * 4,
        "Firearm_leg_Mccall9Mm": ("HandModification_Normal, [0.0,0.0,0.070]",) * 4,
    },
    82: {
        "Firearm_ColtGen": ("HandModification_Normal, [0.000625,0.0,-0.002]",) * 4,
        "Firearm_MagnumGen": ("HandModification_Normal, [0.000625,0.0,-0.002]",) * 4,
        "Firearm_M9Gen": ("HandModification_Normal, [0.0,0.0,0.040]",) * 4,
        "Firearm_DesertEagleGen": (
            "HandModification_Normal, [0.000625,-0.005,0.040]",
            "HandModification_Normal, [0.000625,-0.005,0.045]",
            "HandModification_Normal, [0.000625,-0.005,0.045]",
            "HandModification_Normal, [0.000625,-0.005,0.045]",
        ),
        "Firearm_leg_Mccall9Mm": ("HandModification_Normal, [0.0,0.0,0.040]",) * 4,
    },
}

_PISTOL_AIMBLUR_PRIORS = {
    "Firearm_ColtGen": "0.3",
    "Firearm_MagnumGen": "0.4",
    "Firearm_M9Gen": "0.25",
    "Firearm_DesertEagleGen": "0.26",
    "Firearm_leg_Mccall9Mm": "0.25",
}

_PISTOL_AIMFOV_PRIORS = {
    "Firearm_ColtGen": "2.0",
    "Firearm_MagnumGen": "2.5",
    "Firearm_M9Gen": "2.0",
    "Firearm_DesertEagleGen": "2.0",
    "Firearm_leg_Mccall9Mm": "1.5",
}

_RIFLE_GROUP_A = (
    "Firearm_AutoRifleGen",
    "Firearm_AutoRifle_BGen",
    "Firearm_AutoRifle_CGen",
    "Firearm_BurstRifleGen",
    "Firearm_SingleShotRifleGen",
)
_RIFLE_GROUP_B = (
    "Firearm_AutoRifle_DGen",
    "Firearm_AutoRifle_EGen",
    "Firearm_BurstRifle_BGen",
    "Firearm_SingleShotRifle_BGen",
    "Firearm_leg_DefenderOfTheMotherland",
)
_AUTO_RIFLES = (
    "Firearm_AutoRifleGen",
    "Firearm_AutoRifle_BGen",
    "Firearm_AutoRifle_CGen",
    "Firearm_AutoRifle_DGen",
    "Firearm_AutoRifle_EGen",
)

_RIFLE_HAND_PRIOR = ("HandModification_Normal, [-0.0059,-0.03391,0.070]",) * 4
_RIFLE_HANDROT_PRIOR = ("HandModification_Normal, [-0.1875,0.1875,0.0]",) * 4
_RIFLE_HANDROT_DESIRED = ("HandModification_Normal, [-0.6875,0.1875,0.0]",) * 4

_RIFLE_AIMBLUR_PRIORS = {
    **{item: "0.25" for item in _AUTO_RIFLES},
    "Firearm_BurstRifleGen": "0.2",
    "Firearm_BurstRifle_BGen": "0.2",
    "Firearm_SingleShotRifleGen": "0.2",
    "Firearm_SingleShotRifle_BGen": "0.2",
    "Firearm_leg_DefenderOfTheMotherland": "0.25",
}

_RIFLE_AIMFOV = {
    62: {**{item: "1.7" for item in _RIFLE_GROUP_A}, **{item: "1.7" for item in _RIFLE_GROUP_B}},
    72: {**{item: "1.8" for item in _RIFLE_GROUP_A}, **{item: "1.7" for item in _RIFLE_GROUP_B}},
    82: {**{item: "2.0" for item in _RIFLE_GROUP_A}, **{item: "1.9" for item in _RIFLE_GROUP_B}},
}

_RIFLE_HAND_DESIRED = {
    **{
        item: ("HandModification_Normal, [-0.0055,-0.03291,0.080]",) * 5
        for item in _RIFLE_GROUP_A
    },
    **{
        item: (
            "HandModification_Normal, [-0.0055,-0.03291,0.080]",
            "HandModification_Normal, [-0.0062,-0.03570,0.080]",
            "HandModification_Normal, [-0.0062,-0.03570,0.080]",
            "HandModification_Normal, [-0.0062,-0.03570,0.080]",
            "HandModification_Normal, [-0.0062,-0.03570,0.080]",
        )
        for item in _RIFLE_GROUP_B
    },
}

_SHOTGUN_ITEMS = (
    "Firearm_ShotgunShortGen",
    "Firearm_ShotgunGen",
    "Firearm_Shotgun_BGen",
    "Firearm_Shotgun_CGen",
    "Firearm_Shotgun_DGen",
    "Firearm_Shotgun_EGen",
    "Firearm_Shotgun_FGen",
)
_SHOTGUN_HOLDER_REPLACEMENTS = (
    "Firearm_Shotgun_DGen",
    "Firearm_Shotgun_EGen",
    "Firearm_Shotgun_FGen",
)

_FURY_OFFSETS = {
    62: {
        "Fury_Colt": "HandModification_Normal, [0.000625,0.0,0.070]",
        "Fury_M9": "HandModification_Normal, [0.0,0.0,0.120]",
    },
    72: {
        "Fury_Colt": "HandModification_Normal, [0.000625,0.0,0.030]",
        "Fury_M9": "HandModification_Normal, [0.0,0.0,0.070]",
    },
    82: {
        "Fury_Colt": "HandModification_Normal, [0.000625,0.0,-0.002]",
        "Fury_M9": "HandModification_Normal, [0.0,0.0,0.040]",
    },
}

_CROWD_OFFSETS = {
    62: "HandModification_Normal, [-0.0000,-0.0050,0.010]",
    72: "HandModification_Normal, [-0.0000,-0.0050,0.020]",
    82: "HandModification_Normal, [-0.0000,-0.0050,0.020]",
}

_SHOTGUN_SHORT_AIMFOV = {62: "1.1", 72: "1.3", 82: "1.2"}

_SWAY_PISTOLS = tuple(_PISTOL_HAND_PRIORS)
_SWAY_DESIRED = {
    62: {item: "0.007" for item in _SWAY_PISTOLS},
    72: {
        **{item: "0.005" for item in _SWAY_PISTOLS},
        **{item: "0.015" for item in _SHOTGUN_ITEMS},
    },
    82: {
        **{item: "0.003" for item in _SWAY_PISTOLS},
        **{item: "0.01" for item in _SHOTGUN_ITEMS},
    },
}


def _replace_audited_pistol_offsets(
    expected: tuple[str, ...],
    aimed: tuple[str, str, str, str],
) -> tuple[str, ...]:
    desired = list(expected)
    for ordinal, value in zip((3, 6, 9, 12), aimed):
        desired[ordinal - 1] = value
    return tuple(desired)


def _build_pov(fov: int) -> PovPatchDefinition:
    if fov not in (62, 72, 82):
        raise ValueError("unsupported POV FOV")

    edits: list[PovEdit] = []

    # Sequence replacements run before HolderOffset -> HandOffset edits so the
    # latter cannot change the expected HandOffset sequence length mid-patch.
    for item, expected in _PISTOL_HAND_PRIORS.items():
        edits.extend(
            (
                _sequence(
                    item,
                    "HandOffset",
                    expected,
                    _replace_audited_pistol_offsets(
                        expected,
                        _PISTOL_AIMED_OFFSETS[fov][item],
                    ),
                    source_target_count=4,
                ),
                _sequence(
                    item,
                    "AimBlurStart",
                    (_PISTOL_AIMBLUR_PRIORS[item],),
                    ("0.01",),
                    source_target_count=1,
                ),
                _sequence(
                    item,
                    "AimFov",
                    (_PISTOL_AIMFOV_PRIORS[item],),
                    ("1.05",),
                    source_target_count=1,
                ),
            )
        )

    for item in _RIFLE_GROUP_A + _RIFLE_GROUP_B:
        desired_hand = _RIFLE_HAND_DESIRED[item]
        edits.extend(
            (
                _sequence(
                    item,
                    "HandOffset",
                    _RIFLE_HAND_PRIOR,
                    desired_hand[1:],
                    source_target_count=4,
                ),
                _sequence(
                    item,
                    "HandRot",
                    _RIFLE_HANDROT_PRIOR,
                    _RIFLE_HANDROT_DESIRED,
                    source_target_count=4,
                ),
                _sequence(
                    item,
                    "AimBlurStart",
                    (_RIFLE_AIMBLUR_PRIORS[item],),
                    ("0.01",),
                    source_target_count=1,
                ),
                _sequence(
                    item,
                    "AimFov",
                    ("2.0",),
                    (_RIFLE_AIMFOV[fov][item],),
                    source_target_count=1,
                ),
            )
        )

    for item in _SHOTGUN_ITEMS:
        edits.append(
            _sequence(
                item,
                "AimBlurStart",
                ("0.3",),
                ("0.01",),
                source_target_count=1,
            )
        )
    edits.append(
        _sequence(
            "Firearm_ShotgunShortGen",
            "AimFov",
            ("1.5",),
            (_SHOTGUN_SHORT_AIMFOV[fov],),
            source_target_count=1,
        )
    )
    edits.append(
        _sequence(
            "Firearm_leg_CrowdPleaser",
            "AimBlurStart",
            ("0.3",),
            ("0.01",),
            source_target_count=1,
        )
    )

    for item, desired in _SWAY_DESIRED[fov].items():
        edits.append(
            _sequence(
                item,
                "SwayMaxAngle",
                ("0.02",) * 4,
                (desired,) * 4,
                source_target_count=4,
            )
        )

    for item in ("Fury_Colt", "Fury_M9"):
        edits.extend(
            (
                _sequence(
                    item,
                    "AimFov",
                    ("1.5",),
                    ("1.05",),
                    source_target_count=1,
                    member=INVENTORY_SPECIAL,
                ),
                _call_type(
                    item,
                    "[0.0,0.1,0.0]",
                    _FURY_OFFSETS[fov][item],
                    member=INVENTORY_SPECIAL,
                ),
            )
        )

    for item in _SHOTGUN_HOLDER_REPLACEMENTS:
        edits.append(
            _call_type(
                item,
                "[0.0,0.1,0.0]",
                "HandModification_Normal, [-0.0000,-0.0050,0.020]",
            )
        )

    edits.append(
        _call_type(
            "Firearm_leg_CrowdPleaser",
            "[0.0,0.1,0.0]",
            _CROWD_OFFSETS[fov],
        )
    )

    for item in _RIFLE_GROUP_A + _RIFLE_GROUP_B:
        holder_prior = (
            "[0.1,-0.1,0.15]"
            if item in _AUTO_RIFLES
            else "[0.0,0.1,0.0]"
        )
        edits.append(
            _call_type(
                item,
                holder_prior,
                _RIFLE_HAND_DESIRED[item][0],
            )
        )

    return PovPatchDefinition(f"better_firearm_pov_{fov}", tuple(edits))


BETTER_FIREARM_POV_62 = _build_pov(62)
BETTER_FIREARM_POV_72 = _build_pov(72)
BETTER_FIREARM_POV_82 = _build_pov(82)

POV_PATCHES = {
    definition.name: definition
    for definition in (
        BETTER_FIREARM_POV_62,
        BETTER_FIREARM_POV_72,
        BETTER_FIREARM_POV_82,
    )
}
