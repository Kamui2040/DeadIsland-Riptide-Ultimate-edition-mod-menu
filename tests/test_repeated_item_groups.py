import unittest

from dirue.errors import PatchError
from dirue.firearm_structured import replace_unique_call_in_first_quoted_block
from dirue.structured import (
    insert_calls_after_marker_ordinals_in_first_quoted_block,
    replace_call_sequence_in_first_quoted_block,
)


def _repeated_item_group() -> str:
    parts: list[str] = []
    for ordinal, level in enumerate((0, 0, 1, 1, 2, 2, 3, 3), 1):
        parts.append(
            'Item("Firearm_A", CategoryType_Firearm)\r\n'
            '{\r\n'
            f'    UpgradeLevel({level})\r\n'
        )
        if ordinal == 1:
            parts.append('    HolderOffset([0.0,0.1,0.0]); // native\r\n')
        if ordinal in (1, 3, 4, 6, 8):
            recoil = "0.025" if ordinal == 1 else "0.01"
            parts.append(f"    ShootVertRecoil({recoil});\r\n")
        parts.append('}\r\n')
    return "".join(parts)


class RepeatedItemGroupTests(unittest.TestCase):
    def test_sequence_replacement_spans_repeated_item_group(self):
        result = replace_call_sequence_in_first_quoted_block(
            _repeated_item_group(),
            block_call="Item",
            block_name="Firearm_A",
            call_name="ShootVertRecoil",
            expected_arguments=("0.025", "0.01", "0.01", "0.01", "0.01"),
            desired_arguments=("0.025", "0.01", "0.0095", "0.0090", "0.0085"),
        )
        self.assertEqual(result.count('Item("Firearm_A"'), 8)
        self.assertIn("ShootVertRecoil(0.0095);\r\n", result)
        self.assertIn("ShootVertRecoil(0.0085);\r\n", result)

    def test_upgrade_insertions_use_group_marker_ordinals(self):
        result = insert_calls_after_marker_ordinals_in_first_quoted_block(
            _repeated_item_group(),
            block_call="Item",
            block_name="Firearm_A",
            marker_call="UpgradeLevel",
            expected_marker_arguments=("0", "0", "1", "1", "2", "2", "3", "3"),
            insertions=(
                (3, ("ShotTime(0.9);", "ReloadTime(3.8);")),
                (5, ("ShotTime(0.8);", "ReloadTime(3.5);")),
                (7, ("ShotTime(0.7);", "ReloadTime(3.2);")),
            ),
        )
        self.assertEqual(result.count("ShotTime("), 3)
        self.assertEqual(result.count("ReloadTime("), 3)

    def test_unique_call_replacement_spans_group_and_preserves_crlf(self):
        result = replace_unique_call_in_first_quoted_block(
            _repeated_item_group(),
            block_call="Item",
            block_name="Firearm_A",
            expected_call="HolderOffset",
            expected_argument="[0.0,0.1,0.0]",
            desired_call="HandOffset",
            desired_argument="HandModification_Normal, [0,0,0]",
        )
        self.assertIn(
            "HandOffset(HandModification_Normal, [0,0,0]); // native\r\n",
            result,
        )
        self.assertNotIn("HolderOffset(", result)

    def test_interleaved_same_name_blocks_fail_closed(self):
        source = (
            'Item("Firearm_A", X)\n{\n    Foo(1)\n}\n'
            'Item("Other", X)\n{\n}\n'
            'Item("Firearm_A", X)\n{\n    Foo(2)\n}\n'
        )
        with self.assertRaises(PatchError):
            replace_call_sequence_in_first_quoted_block(
                source,
                block_call="Item",
                block_name="Firearm_A",
                call_name="Foo",
                expected_arguments=("1", "2"),
                desired_arguments=("3", "4"),
            )


if __name__ == "__main__":
    unittest.main()
