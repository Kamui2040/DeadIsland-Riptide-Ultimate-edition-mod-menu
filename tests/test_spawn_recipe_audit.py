import json
import unittest

from dirue.errors import ValidationError
from dirue.spawn_recipe_audit import (
    token_recipe_summary,
    unresolved_mode_summary,
)


class SpawnRecipeAuditTests(unittest.TestCase):
    def _native_values(self):
        seed = [
            "Spawn_Type_Suicider_Default",
            "Other_Butcher_Value",
            "Other_Ram_Value",
            "Other_Bloater_Value",
            "Other_Thug_Value",
            "Other_Bandit_Value",
            "Other_Melee_Value",
        ]
        seed.extend(
            f"Native_{ordinal}_Default"
            for ordinal in range(8, 166)
        )
        return tuple(seed)

    def test_one_token_recipe_uses_native_token_donor(self):
        native = self._native_values()
        target = "Spawn_Type_Butcher_Default"

        result = token_recipe_summary(native, target)

        self.assertTrue(result["recipe_found"])
        recipe = result["recipe"]
        self.assertEqual(recipe["base_ordinal"], 1)
        self.assertEqual(recipe["replacement_count"], 1)
        self.assertEqual(recipe["replacements"][0]["part_index"], 4)
        self.assertEqual(recipe["replacements"][0]["donor_ordinal"], 2)
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn(target, serialized)
        self.assertNotIn("Butcher", serialized)
        self.assertNotIn("Suicider", serialized)

    def test_two_token_recipe_can_combine_native_donors(self):
        native = self._native_values()
        target = "Spawn_Bandit_Melee_Default"

        result = token_recipe_summary(native, target)

        self.assertTrue(result["recipe_found"])
        recipe = result["recipe"]
        self.assertEqual(recipe["base_ordinal"], 1)
        self.assertEqual(recipe["replacement_count"], 2)
        donors = {
            item["donor_ordinal"]
            for item in recipe["replacements"]
        }
        self.assertEqual(donors, {6, 7})

    def test_separator_change_is_not_encoded_as_token_recipe(self):
        native = self._native_values()
        target = "Spawn-Type-Butcher-Default"

        result = token_recipe_summary(native, target)

        self.assertFalse(result["recipe_found"])
        self.assertIsNone(result["recipe"])

    def test_exact_native_donor_is_outside_unresolved_recipe_scope(self):
        native = self._native_values()

        with self.assertRaises(ValidationError):
            token_recipe_summary(native, native[0])

    def test_unresolved_mode_reports_only_sanitized_recipe_metadata(self):
        native = self._native_values()
        target = "Spawn_Type_Butcher_Default"
        preset = tuple(
            native[0] if ordinal == 1 else target
            for ordinal in range(1, 166)
        )

        result = unresolved_mode_summary(native, preset)

        self.assertEqual(result["changed_count"], 164)
        self.assertEqual(result["changed_occurrences"], 164)
        self.assertTrue(result["recipe_found"])
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn(target, serialized)
        self.assertNotIn("Butcher", serialized)

    def test_multiple_desired_changed_values_fail_closed(self):
        native = self._native_values()
        preset = list(native)
        preset[1] = "Spawn_Type_Butcher_Default"
        preset[2] = "Spawn_Type_Ram_Default"

        with self.assertRaises(ValidationError):
            unresolved_mode_summary(native, tuple(preset))


if __name__ == "__main__":
    unittest.main()
