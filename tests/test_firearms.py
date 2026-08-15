import unittest
from collections import defaultdict

from dirue.errors import PatchError
from dirue.firearms import (
    BETTER_FIREARM_UPGRADING,
    ItemCallSequenceEdit,
    ItemUpgradeInsertEdit,
    _UPGRADE_LEVEL_SEQUENCE,
)
from dirue.structured import (
    insert_calls_after_marker_ordinals_in_first_quoted_block,
    replace_call_sequence_in_first_quoted_block,
)


class FirearmUpgradingTests(unittest.TestCase):
    def test_definition_accounts_for_all_active_released_targets(self):
        sequence_changes = sum(
            sum(
                expected != desired
                for expected, desired in zip(
                    edit.expected_arguments,
                    edit.desired_arguments,
                )
            )
            for edit in BETTER_FIREARM_UPGRADING.edits
            if isinstance(edit, ItemCallSequenceEdit)
        )
        inserted_calls = sum(
            sum(len(calls) for _, calls in edit.insertions)
            for edit in BETTER_FIREARM_UPGRADING.edits
            if isinstance(edit, ItemUpgradeInsertEdit)
        )
        self.assertEqual(len(BETTER_FIREARM_UPGRADING.edits), 41)
        self.assertEqual(sequence_changes, 58)
        self.assertEqual(inserted_calls, 99)
        self.assertEqual(sequence_changes + inserted_calls, 157)

    def test_first_quoted_item_scope_handles_extra_header_arguments(self):
        text = (
            'Item("Firearm_A", CategoryType_Firearm)\n'
            '{\n'
            '    ShootVertRecoil(0.1);\n'
            '    ShootVertRecoil(0.2);\n'
            '}\n'
            'Item("Firearm_B", CategoryType_Firearm)\n'
            '{\n'
            '    ShootVertRecoil(0.3);\n'
            '}\n'
        )
        result = replace_call_sequence_in_first_quoted_block(
            text,
            block_call="Item",
            block_name="Firearm_A",
            call_name="ShootVertRecoil",
            expected_arguments=("0.1", "0.2"),
            desired_arguments=("0.1", "0.15"),
        )
        self.assertIn("ShootVertRecoil(0.15)", result)
        self.assertIn("ShootVertRecoil(0.3)", result)

    def test_upgrade_insertions_use_validated_first_tier_markers(self):
        text = (
            'Item("Firearm_A", CategoryType_Firearm)\r\n'
            '{\r\n'
            '    UpgradeLevel(0)\r\n    Foo(0)\r\n'
            '    UpgradeLevel(0)\r\n    Foo(0)\r\n'
            '    UpgradeLevel(1)\r\n    Foo(1)\r\n'
            '    UpgradeLevel(1)\r\n    Foo(1)\r\n'
            '    UpgradeLevel(2)\r\n    Foo(2)\r\n'
            '    UpgradeLevel(2)\r\n    Foo(2)\r\n'
            '    UpgradeLevel(3)\r\n    Foo(3)\r\n'
            '    UpgradeLevel(3)\r\n    Foo(3)\r\n'
            '}\r\n'
        )
        result = insert_calls_after_marker_ordinals_in_first_quoted_block(
            text,
            block_call="Item",
            block_name="Firearm_A",
            marker_call="UpgradeLevel",
            expected_marker_arguments=_UPGRADE_LEVEL_SEQUENCE,
            insertions=(
                (3, ("ShotTime(0.9);", "ReloadTime(3.8);")),
                (5, ("ShotTime(0.8);", "ReloadTime(3.5);")),
                (7, ("ShotTime(0.7);", "ReloadTime(3.2);")),
            ),
        )
        self.assertIn(
            "UpgradeLevel(1)\r\n    ShotTime(0.9);\r\n    ReloadTime(3.8);\r\n",
            result,
        )
        self.assertEqual(result.count("ShotTime("), 3)
        self.assertEqual(result.count("ReloadTime("), 3)

    def test_full_definition_fails_on_wrong_upgrade_marker_sequence(self):
        edits_by_item: dict[str, list[object]] = defaultdict(list)
        for edit in BETTER_FIREARM_UPGRADING.edits:
            edits_by_item[edit.item].append(edit)

        parts: list[str] = []
        for item, edits in edits_by_item.items():
            parts.append(f'Item("{item}", CategoryType_Firearm)\n{{\n')
            for edit in edits:
                if isinstance(edit, ItemCallSequenceEdit):
                    for argument in edit.expected_arguments:
                        parts.append(f"    {edit.call_name}({argument});\n")
            parts.append("    ReloadTime(9.9);\n")
            for level in _UPGRADE_LEVEL_SEQUENCE:
                parts.append(f"    UpgradeLevel({level})\n")
                parts.append("    DamageType(DamageType_Bullet)\n")
            parts.append("}\n")

        text = "".join(parts)
        text = text.replace("UpgradeLevel(3)", "UpgradeLevel(4)", 1)
        with self.assertRaises(PatchError):
            updated = text
            for edit in BETTER_FIREARM_UPGRADING.edits:
                updated = edit.apply(updated)


if __name__ == "__main__":
    unittest.main()
