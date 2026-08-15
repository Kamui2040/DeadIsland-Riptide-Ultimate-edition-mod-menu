import unittest

from dirue.errors import ValidationError
from dirue.fov_audit import FOV_RECOIL_ITEMS, recoil_layouts


_TIER_RECOIL_ITEMS = frozenset(FOV_RECOIL_ITEMS[:8])
_PISTOL_ITEMS = frozenset(FOV_RECOIL_ITEMS[8:])
_LEVELS = (0, 0, 1, 1, 2, 2, 3, 3)


def _native_layout() -> str:
    parts = ["sub main()\r\n{\r\n"]
    for item in FOV_RECOIL_ITEMS:
        for ordinal, level in enumerate(_LEVELS, 1):
            parts.append(
                f'Item("{item}", CategoryType_Firearm)\r\n'
                "{\r\n"
                f"    UpgradeLevel({level});\r\n"
            )
            if item in _TIER_RECOIL_ITEMS:
                if ordinal == 1:
                    parts.append("    ShootVertRecoil(0.1);\r\n")
                if ordinal in (2, 4, 6, 8):
                    parts.append("    SwayMaxAngle(0.02);\r\n")
            else:
                if ordinal in (1, 3, 4, 6, 8):
                    parts.append("    ShootVertRecoil(0.01);\r\n")
                if ordinal in (2, 4, 6, 8):
                    parts.append("    SwayMaxAngle(0.02);\r\n")
            if ordinal in (1, 2, 4, 6, 8):
                parts.append("    ShootMaxAngle(0.05);\r\n")
            parts.append("}\r\n")
    parts.append("}\r\n")
    return "".join(parts)


class FovRecoilAuditTests(unittest.TestCase):
    def test_reports_native_repeated_item_layout(self):
        result = recoil_layouts(_native_layout())
        self.assertEqual(set(result), set(FOV_RECOIL_ITEMS))

        shotgun = result["Firearm_ShotgunShortGen"]
        self.assertEqual(
            shotgun["upgrade_levels"],
            ["0", "0", "1", "1", "2", "2", "3", "3"],
        )
        self.assertEqual(len(shotgun["blocks"]), 8)
        self.assertEqual(
            [site["item_block_ordinal"] for site in shotgun["recoil_sites"]],
            [1],
        )
        self.assertEqual(
            [site["item_block_ordinal"] for site in shotgun["sway_sites"]],
            [2, 4, 6, 8],
        )
        self.assertEqual(
            shotgun["research_class"],
            "tier_recoil_insertion_candidate",
        )

        pistol = result["Firearm_ColtGen"]
        self.assertEqual(
            [site["item_block_ordinal"] for site in pistol["recoil_sites"]],
            [1, 3, 4, 6, 8],
        )
        self.assertEqual(
            pistol["research_class"],
            "existing_five_recoil_sequence",
        )
        self.assertTrue(
            all(site["line_number"] > 0 for site in pistol["recoil_sites"])
        )

    def test_rejects_wrong_upgrade_level_sequence(self):
        source = _native_layout().replace(
            'Item("Firearm_ShotgunShortGen", CategoryType_Firearm)\r\n'
            "{\r\n"
            "    UpgradeLevel(2);",
            'Item("Firearm_ShotgunShortGen", CategoryType_Firearm)\r\n'
            "{\r\n"
            "    UpgradeLevel(9);",
            1,
        )
        with self.assertRaisesRegex(ValidationError, "UpgradeLevel sequence"):
            recoil_layouts(source)

    def test_rejects_missing_repeated_item_block(self):
        source = _native_layout()
        marker = (
            'Item("Firearm_ShotgunShortGen", CategoryType_Firearm)\r\n'
            "{\r\n"
            "    UpgradeLevel(3);\r\n"
            "    SwayMaxAngle(0.02);\r\n"
            "    ShootMaxAngle(0.05);\r\n"
            "}\r\n"
        )
        source = source.replace(marker, "", 1)
        with self.assertRaisesRegex(ValidationError, "expected 8 repeated Item blocks"):
            recoil_layouts(source)

    def test_rejects_wrong_native_recoil_count(self):
        source = _native_layout().replace(
            "    SwayMaxAngle(0.02);\r\n",
            "    SwayMaxAngle(0.02);\r\n    ShootVertRecoil(0.14);\r\n",
            1,
        )
        with self.assertRaisesRegex(ValidationError, "expected 1 active ShootVertRecoil"):
            recoil_layouts(source)

    def test_rejects_interleaved_same_name_item_group(self):
        source = _native_layout()
        needle = (
            'Item("Firearm_ShotgunShortGen", CategoryType_Firearm)\r\n'
            "{\r\n"
            "    UpgradeLevel(0);\r\n"
            "    ShootVertRecoil(0.1);\r\n"
            "    ShootMaxAngle(0.05);\r\n"
            "}\r\n"
        )
        replacement = needle + 'Item("Other", CategoryType_Firearm)\r\n{\r\n}\r\n'
        source = source.replace(needle, replacement, 1)
        with self.assertRaisesRegex(ValidationError, "not contiguous"):
            recoil_layouts(source)


if __name__ == "__main__":
    unittest.main()
