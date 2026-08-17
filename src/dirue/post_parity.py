"""Post-parity gameplay options for the native Linux port."""

from __future__ import annotations

from .definitions import DEFAULT_LEVELS, PatchDefinition, XmlPropertyEdit


HOLD_EVEN_MORE_AMMO = PatchDefinition(
    "hold_even_more_ammo",
    (
        XmlPropertyEdit(DEFAULT_LEVELS, "MaxAmmoPistol", "50", "9999"),
        XmlPropertyEdit(DEFAULT_LEVELS, "MaxAmmoRifle", "60", "9999"),
        XmlPropertyEdit(DEFAULT_LEVELS, "MaxAmmoShotgun", "20", "9999"),
    ),
)


POST_PARITY_PATCHES = {
    HOLD_EVEN_MORE_AMMO.name: HOLD_EVEN_MORE_AMMO,
}
