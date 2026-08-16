import json
import unittest

from dirue.errors import ValidationError
from dirue.spawn_member_recipe_audit import (
    same_member_recipe_summary,
    unresolved_member_mode_summary,
)


class SpawnMemberRecipeAuditTests(unittest.TestCase):
    def _native_values(self):
        values = [
            "Spawn_Type_Normal_Default",
        ]
        values.extend(
            f"Native_{ordinal}_Default"
            for ordinal in range(2, 166)
        )
        return tuple(values)

    def _native_text(self, native_values):
        lines = [
            f'SetField("m_AIPresets", "{value}");'
            for value in native_values
        ]
        lines.append('SetField("Description", "Rare_Butcher_Label");')
        return "\n".join(lines) + "\n"

    def test_recipe_can_use_token_from_other_quoted_string(self):
        native = self._native_values()
        text = self._native_text(native)
        target = "Spawn_Type_Butcher_Default"

        result = same_member_recipe_summary(text, native, target)

        self.assertTrue(result["recipe_found"])
        recipe = result["recipe"]
        self.assertEqual(recipe["base_ordinal"], 1)
        self.assertEqual(recipe["replacement_count"], 1)
        self.assertEqual(recipe["replacements"][0]["part_index"], 4)
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn(target, serialized)
        self.assertNotIn("Butcher", serialized)
        self.assertNotIn("Rare_Butcher_Label", serialized)

    def test_separator_change_still_fails(self):
        native = self._native_values()
        text = self._native_text(native)

        result = same_member_recipe_summary(
            text,
            native,
            "Spawn-Type-Butcher-Default",
        )

        self.assertFalse(result["recipe_found"])
        self.assertIsNone(result["recipe"])

    def test_exact_quoted_donor_is_not_a_reconstruction(self):
        native = self._native_values()
        target = "Spawn_Type_Butcher_Default"
        text = self._native_text(native) + f'Note("{target}");\n'

        with self.assertRaises(ValidationError):
            same_member_recipe_summary(text, native, target)

    def test_mode_summary_preserves_only_sanitized_metadata(self):
        native = self._native_values()
        text = self._native_text(native)
        target = "Spawn_Type_Butcher_Default"
        preset = tuple(
            value if ordinal == 60 else target
            for ordinal, value in enumerate(native, 1)
        )

        result = unresolved_member_mode_summary(
            text,
            native,
            preset,
        )

        self.assertEqual(result["changed_count"], 164)
        self.assertEqual(result["preserved_ordinals"], [60])
        self.assertTrue(result["recipe_found"])
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn(target, serialized)
        self.assertNotIn("Butcher", serialized)

    def test_multiple_desired_identifiers_fail_closed(self):
        native = self._native_values()
        text = self._native_text(native)
        preset = list(native)
        preset[0] = "Spawn_Type_Butcher_Default"
        preset[1] = "Spawn_Type_Ram_Default"

        with self.assertRaises(ValidationError):
            unresolved_member_mode_summary(
                text,
                native,
                tuple(preset),
            )


if __name__ == "__main__":
    unittest.main()
