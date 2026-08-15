import unittest

from dirue.definitions import (
    BETTER_MOVEMENT,
    DEFAULT_LEVELS,
    DIRECT_PATCHES,
    GLOW_SCD,
    GLOW_SCR,
    REDUCE_SPRINT_STAMINA,
    REDUCE_SUNFLARE,
    apply_definition,
)
from dirue.errors import PatchError


class DefinitionTests(unittest.TestCase):
    def test_sprint_definition(self):
        source = {
            DEFAULT_LEVELS: '<prop n="MoveSprintStaminaConsumption" v="0.05"/>'
        }
        result = apply_definition(source, REDUCE_SPRINT_STAMINA)
        self.assertIn('v="0.03"', result[DEFAULT_LEVELS])
        self.assertIn('v="0.05"', source[DEFAULT_LEVELS])

    def test_sunflare_updates_both_members(self):
        source = {
            GLOW_SCD: 'VarFloat("f_pp_glow_factor", 1.0)',
            GLOW_SCR: 'VarFloat("f_glow_factor", 1.0)',
        }
        result = apply_definition(source, REDUCE_SUNFLARE)
        self.assertEqual(result[GLOW_SCD], 'VarFloat("f_pp_glow_factor", 0.1)')
        self.assertEqual(result[GLOW_SCR], 'VarFloat("f_glow_factor", 0.1)')

    def test_movement_updates_all_properties(self):
        text = "\n".join(
            [
                '<prop n="MoveForwardMaxSpeed" v="3.5"/>',
                '<prop n="MoveBackwardMaxSpeed" v="2.5"/>',
                '<prop n="MoveStrafeMaxSpeed" v="2.5"/>',
                '<prop n="MoveAcceleration" v="7.0"/>',
                '<prop n="MoveDeceleration" v="10.0"/>',
            ]
        )
        result = apply_definition({DEFAULT_LEVELS: text}, BETTER_MOVEMENT)[DEFAULT_LEVELS]
        for value in ("3.70", "2.70", "12.00"):
            self.assertIn(value, result)

    def test_missing_member_fails_closed(self):
        with self.assertRaises(PatchError):
            apply_definition({}, REDUCE_SPRINT_STAMINA)

    def test_wrong_prior_value_fails_closed(self):
        source = {
            DEFAULT_LEVELS: '<prop n="MoveSprintStaminaConsumption" v="0.04"/>'
        }
        with self.assertRaises(PatchError):
            apply_definition(source, REDUCE_SPRINT_STAMINA)

    def test_direct_patch_catalog_is_unique(self):
        self.assertEqual(len(DIRECT_PATCHES), 9)
        self.assertEqual(len(DIRECT_PATCHES), len(set(DIRECT_PATCHES)))


if __name__ == "__main__":
    unittest.main()
