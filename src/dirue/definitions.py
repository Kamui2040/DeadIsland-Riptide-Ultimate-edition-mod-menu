"""Declarative Milestone-1 patch definitions for verified text options."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .errors import PatchError
from .patches import (
    replace_call_value,
    replace_color_weight_set,
    replace_deeper_pockets_skill,
    replace_varfloat_value,
    replace_xml_prop_value,
    set_reverb_enabled,
)
from .structured import set_first_quoted_argument_call_commented


@dataclass(frozen=True)
class XmlPropertyEdit:
    member: str
    property_name: str
    expected_value: str
    desired_value: str

    def apply(self, text: str) -> str:
        return replace_xml_prop_value(
            text, self.property_name, self.expected_value, self.desired_value
        )


@dataclass(frozen=True)
class VarFloatEdit:
    member: str
    variable_name: str
    expected_value: str
    desired_value: str

    def apply(self, text: str) -> str:
        return replace_varfloat_value(
            text, self.variable_name, self.expected_value, self.desired_value
        )


@dataclass(frozen=True)
class CallValueEdit:
    member: str
    call_name: str
    expected_value: str
    desired_value: str
    expected_matches: int = 1

    def apply(self, text: str) -> str:
        return replace_call_value(
            text,
            self.call_name,
            self.expected_value,
            self.desired_value,
            expected_matches=self.expected_matches,
        )


@dataclass(frozen=True)
class DeeperPocketsEdit:
    member: str
    expected_desc_params: str = "2;4;6"
    desired_desc_params: str = "6;12;18"
    expected_inventory_change: str = "2"
    desired_inventory_change: str = "6"

    def apply(self, text: str) -> str:
        return replace_deeper_pockets_skill(
            text,
            expected_desc_params=self.expected_desc_params,
            new_desc_params=self.desired_desc_params,
            expected_inventory_change=self.expected_inventory_change,
            new_inventory_change=self.desired_inventory_change,
        )


@dataclass(frozen=True)
class CommentedCallEdit:
    member: str
    call_name: str
    argument: str
    commented: bool
    expected_matches: int = 1

    def apply(self, text: str) -> str:
        return set_first_quoted_argument_call_commented(
            text,
            call_name=self.call_name,
            argument=self.argument,
            commented=self.commented,
            expected_matches=self.expected_matches,
        )


@dataclass(frozen=True)
class LootColorSetEdit:
    member: str
    color_set: str
    expected_weights: tuple[tuple[str, str], ...]
    desired_weights: tuple[tuple[str, str], ...]

    def apply(self, text: str) -> str:
        return replace_color_weight_set(
            text,
            self.color_set,
            dict(self.expected_weights),
            dict(self.desired_weights),
        )


@dataclass(frozen=True)
class ReverbEdit:
    member: str
    enabled: bool
    expected_preset_calls: int
    expected_mix_calls: int

    def apply(self, text: str) -> str:
        return set_reverb_enabled(
            text,
            enabled=self.enabled,
            expected_preset_calls=self.expected_preset_calls,
            expected_mix_calls=self.expected_mix_calls,
        )


TextEdit = (
    XmlPropertyEdit
    | VarFloatEdit
    | CallValueEdit
    | DeeperPocketsEdit
    | CommentedCallEdit
    | LootColorSetEdit
    | ReverbEdit
)


@dataclass(frozen=True)
class PatchDefinition:
    name: str
    edits: tuple[TextEdit, ...]


def apply_definition(
    members: Mapping[str, str], definition: PatchDefinition
) -> dict[str, str]:
    """Apply one definition to an in-memory member map without mutating the input."""
    updated = dict(members)
    for edit in definition.edits:
        if edit.member not in updated:
            raise PatchError(f"{definition.name}: missing archive member {edit.member}")
        updated[edit.member] = edit.apply(updated[edit.member])
    return updated


DEFAULT_LEVELS = "data/skills/default_levels.xml"
GLOW_SCD = "data/scripts/varlist_glow.scd"
GLOW_SCR = "data/scripts/varlist_glow.scr"
CAR_PHYSICS = "data/odephysics/vehicle/cardi.phx"
OLD_BOAT_PHYSICS = "data/odephysics/vehicle/old_boat_a.phx"
DEFAULT_LOOT = "data/default.loot"
GAME_AUDIO_EFFECTS = "data/gameaudioeffects.scr"
INTRO_MOVIES = "data/menu/movies/intromovies.scr"
LOGAN_SKILLS = "data/skills/logan_skills.xml"
PURNA_SKILLS = "data/skills/purna_skills.xml"
SAMB_SKILLS = "data/skills/samb_skills.xml"
XIAN_SKILLS = "data/skills/xian_skills.xml"
JOHN_SKILLS = "data/skills/john_skills.xml"


def _loot_weights(
    white: str,
    green: str,
    blue: str,
    violet: str,
    orange: str,
) -> tuple[tuple[str, str], ...]:
    return (
        ("Color_White", white),
        ("Color_Green", green),
        ("Color_Blue", blue),
        ("Color_Violet", violet),
        ("Color_Orange", orange),
    )


# The native read-only audit verified these prior values against the installed
# Linux Data0 baseline. The patch engine still validates them again at runtime.
REDUCE_SPRINT_STAMINA = PatchDefinition(
    "reduce_sprint_stamina",
    (XmlPropertyEdit(DEFAULT_LEVELS, "MoveSprintStaminaConsumption", "0.05", "0.03"),),
)
REDUCE_JUMP_STAMINA = PatchDefinition(
    "reduce_jump_stamina",
    (XmlPropertyEdit(DEFAULT_LEVELS, "JumpStaminaCost", "0.06", "0.03"),),
)
REDUCE_SUNFLARE = PatchDefinition(
    "reduce_sunflare",
    (
        VarFloatEdit(GLOW_SCD, "f_pp_glow_factor", "1.0", "0.1"),
        VarFloatEdit(GLOW_SCR, "f_glow_factor", "1.0", "0.1"),
    ),
)
RUN_WITH_WEAPONS = PatchDefinition(
    "run_with_weapons",
    (XmlPropertyEdit(DEFAULT_LEVELS, "HideWeaponsDuringSprint", "1.0", "0.0"),),
)
BETTER_MOVEMENT = PatchDefinition(
    "better_movement",
    (
        XmlPropertyEdit(DEFAULT_LEVELS, "MoveForwardMaxSpeed", "3.5", "3.70"),
        XmlPropertyEdit(DEFAULT_LEVELS, "MoveBackwardMaxSpeed", "2.5", "2.70"),
        XmlPropertyEdit(DEFAULT_LEVELS, "MoveStrafeMaxSpeed", "2.5", "3.70"),
        XmlPropertyEdit(DEFAULT_LEVELS, "MoveAcceleration", "7.0", "12.00"),
        XmlPropertyEdit(DEFAULT_LEVELS, "MoveDeceleration", "10.0", "12.00"),
    ),
)
HOLD_MORE_AMMO = PatchDefinition(
    "hold_more_ammo",
    (
        XmlPropertyEdit(DEFAULT_LEVELS, "MaxAmmoPistol", "50", "200"),
        XmlPropertyEdit(DEFAULT_LEVELS, "MaxAmmoRifle", "60", "150"),
        XmlPropertyEdit(DEFAULT_LEVELS, "MaxAmmoShotgun", "20", "90"),
    ),
)
INSTANT_BREAK_DOORS = PatchDefinition(
    "instant_break_doors",
    (XmlPropertyEdit(DEFAULT_LEVELS, "BreakDoorEffectivens", "0", "99"),),
)
INCREASE_DURABILITY = PatchDefinition(
    "increase_durability",
    (
        XmlPropertyEdit(DEFAULT_LEVELS, "BluntWpnDurabilityLoss", "1.0", "-9.0"),
        XmlPropertyEdit(DEFAULT_LEVELS, "CutWpnDurabilityLoss", "1.0", "-9.0"),
        XmlPropertyEdit(DEFAULT_LEVELS, "RangedWpnDurabilityLoss", "0.1", "-9.0"),
        XmlPropertyEdit(DEFAULT_LEVELS, "BulletWpnDurabilityLoss", "0.1", "-9.0"),
    ),
)
BULLET_PENETRATION = PatchDefinition(
    "bullet_penetration",
    (XmlPropertyEdit(DEFAULT_LEVELS, "BulletPenetrationChance", "0.", "0.98"),),
)
DEEPER_POCKETS = PatchDefinition(
    "deeper_pockets",
    tuple(
        DeeperPocketsEdit(member)
        for member in (
            LOGAN_SKILLS,
            PURNA_SKILLS,
            SAMB_SKILLS,
            XIAN_SKILLS,
            JOHN_SKILLS,
        )
    ),
)
SKIP_INTRO_VIDEOS = PatchDefinition(
    "skip_intro_videos",
    (CommentedCallEdit(INTRO_MOVIES, "File", "Intro_720p", True),),
)
REMOVE_REVERB_ECHO = PatchDefinition(
    "remove_reverb_echo",
    (ReverbEdit(GAME_AUDIO_EFFECTS, False, 52, 52),),
)
IMPROVED_LOOT = PatchDefinition(
    "improved_loot",
    (
        LootColorSetEdit(
            DEFAULT_LOOT,
            "ColorSet_Default",
            _loot_weights("91.0", "7.0", "2.0", "0.0", "0.0"),
            _loot_weights("55.0", "32.0", "8.0", "3.0", "2.0"),
        ),
        LootColorSetEdit(
            DEFAULT_LOOT,
            "ColorSet_LockPick1",
            _loot_weights("0.0", "92.0", "6.0", "1.0", "0.0"),
            _loot_weights("0.0", "77.0", "10.0", "8.0", "5.0"),
        ),
        LootColorSetEdit(
            DEFAULT_LOOT,
            "ColorSet_LockPick2",
            _loot_weights("0.0", "85.0", "11.0", "3.0", "1.0"),
            _loot_weights("0.0", "55.0", "16.0", "15.0", "14.0"),
        ),
        LootColorSetEdit(
            DEFAULT_LOOT,
            "ColorSet_LockPick3",
            _loot_weights("0.0", "72.0", "21.0", "5.0", "2.0"),
            _loot_weights("0.0", "37.0", "33.0", "14.0", "16.0"),
        ),
        LootColorSetEdit(
            DEFAULT_LOOT,
            "ColorSet_Ram",
            _loot_weights("0.0", "10.0", "67.0", "20.0", "3.0"),
            _loot_weights("0.0", "5.0", "30.0", "50.0", "15.0"),
        ),
        LootColorSetEdit(
            DEFAULT_LOOT,
            "ColorSet_MeleeFighter",
            _loot_weights("0.0", "65.0", "35.0", "0.0", "0.0"),
            _loot_weights("0.0", "6.0", "31.0", "52.0", "11.0"),
        ),
    ),
)

# Source reconstruction only. The native audit found four active Ignore(0)
# calls in the car file and five in the old-boat file, so the AHK's two line
# edits per file need block-level identity before this can be exposed.
NOCLIP_VEHICLES = PatchDefinition(
    "noclip_vehicles",
    (
        CallValueEdit(CAR_PHYSICS, "Ignore", "0", "1", expected_matches=2),
        CallValueEdit(OLD_BOAT_PHYSICS, "Ignore", "0", "1", expected_matches=2),
    ),
)

DIRECT_PATCHES = {
    definition.name: definition
    for definition in (
        REDUCE_SPRINT_STAMINA,
        REDUCE_JUMP_STAMINA,
        REDUCE_SUNFLARE,
        RUN_WITH_WEAPONS,
        BETTER_MOVEMENT,
        HOLD_MORE_AMMO,
        INSTANT_BREAK_DOORS,
        INCREASE_DURABILITY,
        BULLET_PENETRATION,
        DEEPER_POCKETS,
        SKIP_INTRO_VIDEOS,
        REMOVE_REVERB_ECHO,
        IMPROVED_LOOT,
    )
}
