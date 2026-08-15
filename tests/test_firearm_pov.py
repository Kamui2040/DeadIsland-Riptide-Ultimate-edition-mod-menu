import unittest
from collections import defaultdict

from dirue.errors import PatchError
from dirue.firearm_pov import (
    BETTER_FIREARM_POV_62,
    BETTER_FIREARM_POV_72,
    BETTER_FIREARM_POV_82,
    PovCallSequenceEdit,
    PovCallTypeEdit,
)
from dirue.firearm_structured import replace_unique_call_in_first_quoted_block


class FirearmPovTests(unittest.TestCase):
    def test_definitions_account_for_released_pov_and_sway_targets(self):
        self.assertEqual(BETTER_FIREARM_POV_62.source_target_count, 177)
        self.assertEqual(BETTER_FIREARM_POV_72.source_target_count, 205)
        self.assertEqual(BETTER_FIREARM_POV_82.source_target_count, 205)

    def test_call_type_replacement_is_scoped_and_preserves_other_items(self):
        text = (
            'Item("Firearm_A", CategoryType_Firearm)\n'
            '{\n'
            '    HolderOffset([0.0,0.1,0.0]); // native\n'
            '    HandOffset(HandModification_Normal, [0,0,0]);\n'
            '}\n'
            'Item("Firearm_B", CategoryType_Firearm)\n'
            '{\n'
            '    HolderOffset([0.0,0.1,0.0]);\n'
            '}\n'
        )
        result = replace_unique_call_in_first_quoted_block(
            text,
            block_call="Item",
            block_name="Firearm_A",
            expected_call="HolderOffset",
            expected_argument="[0.0,0.1,0.0]",
            desired_call="HandOffset",
            desired_argument="HandModification_Normal, [0.0,0.0,0.040]",
        )
        self.assertIn(
            "HandOffset(HandModification_Normal, [0.0,0.0,0.040]); // native",
            result,
        )
        self.assertIn(
            'Item("Firearm_B", CategoryType_Firearm)\n{\n'
            '    HolderOffset([0.0,0.1,0.0]);',
            result,
        )

    def test_call_type_replacement_fails_on_wrong_or_duplicate_prior(self):
        wrong = (
            'Item("Firearm_A", CategoryType_Firearm)\n'
            '{\n    HolderOffset([9,9,9]);\n}\n'
        )
        with self.assertRaises(PatchError):
            replace_unique_call_in_first_quoted_block(
                wrong,
                block_call="Item",
                block_name="Firearm_A",
                expected_call="HolderOffset",
                expected_argument="[0.0,0.1,0.0]",
                desired_call="HandOffset",
                desired_argument="x",
            )

        duplicate = (
            'Item("Firearm_A", CategoryType_Firearm)\n'
            '{\n'
            '    HolderOffset([0.0,0.1,0.0]);\n'
            '    HolderOffset([0.0,0.1,0.0]);\n'
            '}\n'
        )
        with self.assertRaises(PatchError):
            replace_unique_call_in_first_quoted_block(
                duplicate,
                block_call="Item",
                block_name="Firearm_A",
                expected_call="HolderOffset",
                expected_argument="[0.0,0.1,0.0]",
                desired_call="HandOffset",
                desired_argument="x",
            )

    def test_desert_eagle_82_preserves_released_asymmetric_offsets(self):
        edit = next(
            edit
            for edit in BETTER_FIREARM_POV_82.edits
            if isinstance(edit, PovCallSequenceEdit)
            and edit.item == "Firearm_DesertEagleGen"
            and edit.call_name == "HandOffset"
        )
        changed = tuple(
            index + 1
            for index, (before, after) in enumerate(
                zip(edit.expected_arguments, edit.desired_arguments)
            )
            if before != after
        )
        self.assertEqual(changed, (3, 6, 9, 12))
        self.assertEqual(
            edit.desired_arguments[2],
            "HandModification_Normal, [0.000625,-0.005,0.040]",
        )
        self.assertEqual(
            edit.desired_arguments[5],
            "HandModification_Normal, [0.000625,-0.005,0.045]",
        )

    def test_full_pov_definitions_apply_to_synthetic_native_sequences(self):
        for definition in (
            BETTER_FIREARM_POV_62,
            BETTER_FIREARM_POV_72,
            BETTER_FIREARM_POV_82,
        ):
            members = self._synthetic_members(definition)
            updated = dict(members)
            for edit in definition.edits:
                updated[edit.member] = edit.apply(updated[edit.member])
            self.assertNotEqual(updated, members)

    @staticmethod
    def _synthetic_members(definition):
        per_item = defaultdict(lambda: {"sequences": {}, "types": {}})
        for edit in definition.edits:
            key = (edit.member, edit.item)
            if isinstance(edit, PovCallSequenceEdit):
                per_item[key]["sequences"].setdefault(
                    edit.call_name,
                    edit.expected_arguments,
                )
            elif isinstance(edit, PovCallTypeEdit):
                per_item[key]["types"].setdefault(
                    edit.expected_call,
                    edit.expected_argument,
                )

        members = defaultdict(str)
        for (member, item), facts in per_item.items():
            lines = [f'Item("{item}", CategoryType_Firearm)\n', "{\n"]
            for call_name, arguments in facts["sequences"].items():
                lines.extend(
                    f"    {call_name}({argument});\n"
                    for argument in arguments
                )
            for call_name, argument in facts["types"].items():
                lines.append(f"    {call_name}({argument});\n")
            lines.append("}\n")
            members[member] += "".join(lines)
        return dict(members)


if __name__ == "__main__":
    unittest.main()
