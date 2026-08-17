import unittest

from dirue.advanced import (
    CAR_PHYSICS,
    HEADSHOT_ONLY_AI,
    NOCLIP_VEHICLES,
    OLD_BOAT_PHYSICS,
    ONE_HIT_AI,
)
from dirue.catalog import EXCLUSIVE_PATCH_GROUPS, READY_PATCHES
from dirue.definitions import DIRECT_PATCHES, apply_definition
from dirue.errors import PatchError


class AdvancedDefinitionTests(unittest.TestCase):
    def test_ready_catalog_includes_semantic_options(self):
        self.assertEqual(len(DIRECT_PATCHES), 13)
        self.assertEqual(len(READY_PATCHES), 43)
        self.assertIn("noclip_vehicles", READY_PATCHES)
        self.assertIn("one_hit_ai", READY_PATCHES)
        self.assertIn("hard_ai", READY_PATCHES)
        self.assertIn("headshot_only_ai", READY_PATCHES)
        self.assertIn("better_firearm_upgrading", READY_PATCHES)
        self.assertIn("better_firearm_pov_62", READY_PATCHES)
        self.assertIn("better_firearm_pov_72", READY_PATCHES)
        self.assertIn("better_firearm_pov_82", READY_PATCHES)
        self.assertIn("camera_fov_72", READY_PATCHES)
        self.assertIn("camera_fov_82", READY_PATCHES)
        self.assertIn("zombie_size_extra_small", READY_PATCHES)
        self.assertIn("zombie_size_midget", READY_PATCHES)
        self.assertIn("zombie_size_large", READY_PATCHES)
        self.assertIn("zombie_size_supersize", READY_PATCHES)
        self.assertIn("weather_just_night", READY_PATCHES)
        self.assertIn("weather_rain_day", READY_PATCHES)
        self.assertIn("weather_rain_night", READY_PATCHES)
        self.assertIn("weather_storm_day", READY_PATCHES)
        self.assertIn("weather_storm_night", READY_PATCHES)
        self.assertIn("weather_just_night_darker", READY_PATCHES)
        self.assertIn("weather_rain_night_darker", READY_PATCHES)
        self.assertIn("weather_storm_night_darker", READY_PATCHES)
        self.assertIn("force_suiciders", READY_PATCHES)
        self.assertIn("force_bandits_guns", READY_PATCHES)
        self.assertIn("force_bandits_melee", READY_PATCHES)
        self.assertIn("force_butchers", READY_PATCHES)
        self.assertIn("force_rams", READY_PATCHES)
        self.assertIn("force_bloaters", READY_PATCHES)
        self.assertIn("force_thugs", READY_PATCHES)
        self.assertIn("hold_even_more_ammo", READY_PATCHES)
        self.assertIn(
            frozenset({"one_hit_ai", "hard_ai", "headshot_only_ai"}),
            EXCLUSIVE_PATCH_GROUPS,
        )
        self.assertIn(
            frozenset(
                {
                    "better_firearm_pov_62",
                    "better_firearm_pov_72",
                    "better_firearm_pov_82",
                }
            ),
            EXCLUSIVE_PATCH_GROUPS,
        )
        self.assertIn(
            frozenset({"camera_fov_72", "camera_fov_82"}),
            EXCLUSIVE_PATCH_GROUPS,
        )
        self.assertIn(
            frozenset(
                {
                    "zombie_size_extra_small",
                    "zombie_size_midget",
                    "zombie_size_large",
                    "zombie_size_supersize",
                }
            ),
            EXCLUSIVE_PATCH_GROUPS,
        )
        self.assertIn(
            frozenset({"hold_more_ammo", "hold_even_more_ammo"}),
            EXCLUSIVE_PATCH_GROUPS,
        )
        self.assertIn(
            frozenset(
                {
                    "weather_just_night",
                    "weather_rain_day",
                    "weather_rain_night",
                    "weather_storm_day",
                    "weather_storm_night",
                    "weather_just_night_darker",
                    "weather_rain_night_darker",
                    "weather_storm_night_darker",
                }
            ),
            EXCLUSIVE_PATCH_GROUPS,
        )
        self.assertIn(
            frozenset(
                {
                    "force_suiciders",
                    "force_bandits_guns",
                    "force_bandits_melee",
                    "force_butchers",
                    "force_rams",
                    "force_bloaters",
                    "force_thugs",
                }
            ),
            EXCLUSIVE_PATCH_GROUPS,
        )

    def test_noclip_updates_only_released_contact_blocks(self):
        car = (
            'ContactParams("Terrain")\n{\n    Ignore(0)\n}\n'
            'ContactParams("SimpleObjects")\n{\n    Ignore(0)\n}\n'
            'ContactParams("NonODEObjects")\n{\n    Ignore(0)\n}\n'
            'ContactParams("ODEObjects")\n{\n    Ignore(0)\n}\n'
            'ContactParams("Water")\n{\n    Ignore(1)\n}\n'
        )
        boat = car.replace('ContactParams("Water")\n{\n    Ignore(1)', 'ContactParams("Water")\n{\n    Ignore(0)')
        result = apply_definition(
            {CAR_PHYSICS: car, OLD_BOAT_PHYSICS: boat},
            NOCLIP_VEHICLES,
        )
        self.assertIn('ContactParams("Terrain")\n{\n    Ignore(0)', result[CAR_PHYSICS])
        self.assertIn('ContactParams("ODEObjects")\n{\n    Ignore(0)', result[CAR_PHYSICS])
        self.assertIn('ContactParams("Water")\n{\n    Ignore(1)', result[CAR_PHYSICS])
        self.assertEqual(result[CAR_PHYSICS].count("Ignore(1)"), 3)
        self.assertEqual(result[OLD_BOAT_PHYSICS].count("Ignore(1)"), 2)

    def test_noclip_wrong_prior_state_fails_closed(self):
        text = (
            'ContactParams("SimpleObjects")\n{\n    Ignore(1)\n}\n'
            'ContactParams("NonODEObjects")\n{\n    Ignore(0)\n}\n'
        )
        with self.assertRaises(PatchError):
            apply_definition(
                {CAR_PHYSICS: text, OLD_BOAT_PHYSICS: text},
                NOCLIP_VEHICLES,
            )

    def test_one_hit_definition_covers_both_audited_members(self):
        members = {
            edit.member: f'{edit.call_name}("{edit.argument}", {edit.expected_value})'
            for edit in ONE_HIT_AI.edits
        }
        self.assertEqual(len(ONE_HIT_AI.edits), 2)
        self.assertEqual(len(members), 2)

        result = apply_definition(members, ONE_HIT_AI)
        for edit in ONE_HIT_AI.edits:
            self.assertIn(
                f'{edit.call_name}("{edit.argument}", {edit.desired_value})',
                result[edit.member],
            )

    def test_one_hit_wrong_prior_value_fails_closed(self):
        first = ONE_HIT_AI.edits[0]
        with self.assertRaises(PatchError):
            apply_definition(
                {first.member: f'{first.call_name}("{first.argument}", 9)'},
                ONE_HIT_AI,
            )

    def test_headshot_definition_covers_all_audited_value_changes(self):
        self.assertEqual(len(HEADSHOT_ONLY_AI.edits), 115)
        lines: dict[str, list[str]] = {}
        for edit in HEADSHOT_ONLY_AI.edits:
            lines.setdefault(edit.member, []).append(
                f'{edit.call_name}("{edit.argument}",{edit.expected_value})'
            )
        members = {member: "\n".join(member_lines) for member, member_lines in lines.items()}
        self.assertEqual(len(members), 20)

        result = apply_definition(members, HEADSHOT_ONLY_AI)
        for edit in HEADSHOT_ONLY_AI.edits:
            self.assertIn(
                f'{edit.call_name}("{edit.argument}",{edit.desired_value})',
                result[edit.member],
            )

    def test_headshot_wrong_prior_value_fails_closed(self):
        first = HEADSHOT_ONLY_AI.edits[0]
        with self.assertRaises(PatchError):
            apply_definition(
                {first.member: f'{first.call_name}("{first.argument}",9.9)'},
                HEADSHOT_ONLY_AI,
            )


if __name__ == "__main__":
    unittest.main()
