import json
import unittest

from dirue.errors import ValidationError
from dirue.spawn_ai_recipe_audit import (
    _AI_SOURCE_MEMBERS,
    ai_source_recipe_summary,
)


class SpawnAISourceRecipeAuditTests(unittest.TestCase):
    def _spawn_values(self):
        values = [
            "Spawn_Type_Suicider_Default",
            "Other_Butcher_Value",
            "Other_Ram_Value",
            "Other_Bloater_Value",
            "Other_Thug_Value",
        ]
        values.extend(
            f"Native_{ordinal}_Default"
            for ordinal in range(6, 166)
        )
        return tuple(values)

    def _members(self):
        members = {member: 'Label("Neutral_Default");\n' for member in _AI_SOURCE_MEMBERS}
        members["data/bestiary.scr"] = 'Label("Butcher");\n'
        return members

    def test_recipe_can_use_token_from_other_ai_member(self):
        native = self._spawn_values()
        members = self._members()
        target = "Spawn_Type_Butcher_Default"

        result = ai_source_recipe_summary(native, members, target)

        self.assertTrue(result["recipe_found"])
        recipe = result["recipe"]
        self.assertEqual(recipe["base_ordinal"], 1)
        self.assertEqual(recipe["replacement_count"], 1)
        change = recipe["replacements"][0]
        self.assertEqual(change["part_index"], 4)
        self.assertEqual(change["donor_member"], "data/bestiary.scr")
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn(target, serialized)
        self.assertNotIn("Butcher", serialized)
        self.assertNotIn("Suicider", serialized)

    def test_separator_change_is_rejected(self):
        native = self._spawn_values()
        members = self._members()
        target = "Spawn-Type-Butcher-Default"

        result = ai_source_recipe_summary(native, members, target)

        self.assertFalse(result["recipe_found"])
        self.assertIsNone(result["recipe"])

    def test_missing_token_is_rejected(self):
        native = self._spawn_values()
        members = self._members()
        target = "Spawn_Type_Unknown_Default"

        result = ai_source_recipe_summary(native, members, target)

        self.assertFalse(result["recipe_found"])

    def test_exact_donor_is_outside_recipe_scope(self):
        native = self._spawn_values()
        members = self._members()
        members["data/bestiary.scr"] = 'Label("Spawn_Type_Butcher_Default");\n'

        with self.assertRaises(ValidationError):
            ai_source_recipe_summary(
                native,
                members,
                "Spawn_Type_Butcher_Default",
            )

    def test_unexpected_member_set_fails_closed(self):
        native = self._spawn_values()
        members = self._members()
        members.pop("data/bestiary.scr")

        with self.assertRaises(ValidationError):
            ai_source_recipe_summary(
                native,
                members,
                "Spawn_Type_Butcher_Default",
            )


if __name__ == "__main__":
    unittest.main()
