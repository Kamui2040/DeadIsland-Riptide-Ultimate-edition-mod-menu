"""Declarative Milestone-1 patch definitions for direct-value options."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .errors import PatchError
from .patches import replace_varfloat_value, replace_xml_prop_value


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


TextEdit = XmlPropertyEdit | VarFloatEdit


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

# These values are reconstructed from the released AHK behavior. Native archive
# prior-state verification is still required before live-game use.
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
    )
}
