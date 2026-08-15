import re
import unittest

from dirue.definitions import DEFAULT_LEVELS, apply_definition
from dirue.errors import PatchError
from dirue.fov import (
    CAMERA_FOV_72,
    CAMERA_FOV_82,
    FOV72_RELEASED_WRITE_COUNT,
    FOV82_RELEASED_WRITE_COUNT,
    INVENTORY_GEN,
    ItemFirstRecoilEdit,
    _PISTOL_RECOIL_VARIANTS,
    _TIER_RECOIL_ITEMS,
)


_LEVELS = (0, 0, 1, 1, 2, 2, 3, 3)


def _group(item: str, recoil: tuple[str, ...], newline: str = "\r\n") -> str:
    recoil_blocks = (1,) if len(recoil) == 1 else (1, 2, 4, 6, 8)
    by_block = dict(zip(recoil_blocks, recoil))
    parts: list[str] = []
    for ordinal, level in enumerate(_LEVELS, 1):
        parts.extend(
            (
                f'Item("{item}", CategoryType_Firearm){newline}',
                f"{{{newline}",
                f"    UpgradeLevel({level});{newline}",
            )
        )
        if ordinal in by_block:
            parts.append(f"    ShootVertRecoil({by_block[ordinal]});{newline}")
        if ordinal in (2, 4, 6, 8):
            parts.append(f"    SwayMaxAngle(0.02);{newline}")
        parts.append(f"}}{newline}")
    return "".join(parts)


def _native_inventory(*, upgraded_pistols: bool = False) -> str:
    parts = [_group(item, ("0.1",)) for item in _TIER_RECOIL_ITEMS]
    parts.extend(
        _group(item, variants[1] if upgraded_pistols else variants[0])
        for item, variants in _PISTOL_RECOIL_VARIANTS.items()
    )
    return "".join(parts)


def _recoil_values(text: str, item: str) -> tuple[str, ...]:
    start = text.index(f'Item("{item}"')
    tail = text[start:]
    other = re.search(
        rf'\r\nItem\("(?!{re.escape(item)}")[^"]+"',
        tail,
    )
    if other:
        tail = tail[: other.start()]
    return tuple(
        match.group(1).strip()
        for match in re.finditer(
            r"^[ \t]*ShootVertRecoil\(([^)]+)\)",
            tail,
            re.MULTILINE,
        )
    )


class CameraFovTests(unittest.TestCase):
    def _members(self, *, upgraded_pistols: bool = False) -> dict[str, str]:
        return {
            DEFAULT_LEVELS: '<prop n="CameraDefaultFOV" v="62.5"/>\r\n',
            INVENTORY_GEN: _native_inventory(upgraded_pistols=upgraded_pistols),
        }

    def test_fov72_matches_released_active_recoil_shape(self):
        result = apply_definition(self._members(), CAMERA_FOV_72)
        self.assertIn('v="72"', result[DEFAULT_LEVELS])
        for item in _TIER_RECOIL_ITEMS:
            self.assertEqual(
                _recoil_values(result[INVENTORY_GEN], item),
                ("0.06", "0.14", "0.14", "0.14", "0.14"),
            )
        expected_bases = {
            "Firearm_DesertEagleGen": "0.015",
            "Firearm_MagnumGen": "0.017",
            "Firearm_M9Gen": "0.015",
            "Firearm_leg_Mccall9Mm": "0.015",
            "Firearm_ColtGen": "0.025",
        }
        for item, value in expected_bases.items():
            self.assertEqual(_recoil_values(result[INVENTORY_GEN], item)[0], value)
        self.assertEqual(FOV72_RELEASED_WRITE_COUNT, 45)

    def test_fov82_matches_released_active_recoil_shape(self):
        result = apply_definition(self._members(), CAMERA_FOV_82)
        self.assertIn('v="82"', result[DEFAULT_LEVELS])
        for item in _TIER_RECOIL_ITEMS:
            self.assertEqual(
                _recoil_values(result[INVENTORY_GEN], item),
                ("0.033", "0.14", "0.14", "0.14", "0.14"),
            )
        expected_bases = {
            "Firearm_DesertEagleGen": "0.008",
            "Firearm_MagnumGen": "0.010",
            "Firearm_M9Gen": "0.015",
            "Firearm_leg_Mccall9Mm": "0.015",
            "Firearm_ColtGen": "0.015",
        }
        for item, value in expected_bases.items():
            self.assertEqual(_recoil_values(result[INVENTORY_GEN], item)[0], value)
        self.assertEqual(FOV82_RELEASED_WRITE_COUNT, 46)

    def test_pistol_base_edit_accepts_upgrading_tail_and_preserves_it(self):
        result = apply_definition(
            self._members(upgraded_pistols=True),
            CAMERA_FOV_82,
        )
        for item, variants in _PISTOL_RECOIL_VARIANTS.items():
            values = _recoil_values(result[INVENTORY_GEN], item)
            expected_base = {
                "Firearm_DesertEagleGen": "0.008",
                "Firearm_MagnumGen": "0.010",
                "Firearm_M9Gen": "0.015",
                "Firearm_leg_Mccall9Mm": "0.015",
                "Firearm_ColtGen": "0.015",
            }[item]
            self.assertEqual(values, (expected_base, *variants[1][1:]))

    def test_first_recoil_edit_rejects_unexpected_prior(self):
        edit = ItemFirstRecoilEdit(
            INVENTORY_GEN,
            "Firearm_ColtGen",
            _PISTOL_RECOIL_VARIANTS["Firearm_ColtGen"],
            "0.015",
        )
        with self.assertRaises(PatchError):
            edit.apply(
                _group(
                    "Firearm_ColtGen",
                    ("9", "0.01", "0.01", "0.01", "0.01"),
                )
            )

    def test_reapplying_fov_fails_closed_instead_of_duplicating_tier_calls(self):
        first = apply_definition(self._members(), CAMERA_FOV_72)
        with self.assertRaises(PatchError):
            apply_definition(first, CAMERA_FOV_72)


if __name__ == "__main__":
    unittest.main()
