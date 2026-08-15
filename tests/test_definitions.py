import re
import unittest

from dirue.definitions import (
    BETTER_MOVEMENT,
    CAR_PHYSICS,
    DEEPER_POCKETS,
    DEFAULT_LEVELS,
    DEFAULT_LOOT,
    DIRECT_PATCHES,
    GAME_AUDIO_EFFECTS,
    GLOW_SCD,
    GLOW_SCR,
    IMPROVED_LOOT,
    INTRO_MOVIES,
    JOHN_SKILLS,
    LOGAN_SKILLS,
    NOCLIP_VEHICLES,
    OLD_BOAT_PHYSICS,
    PURNA_SKILLS,
    REDUCE_SPRINT_STAMINA,
    REDUCE_SUNFLARE,
    REMOVE_REVERB_ECHO,
    SAMB_SKILLS,
    SKIP_INTRO_VIDEOS,
    XIAN_SKILLS,
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

    def test_noclip_source_reconstruction_updates_two_calls_per_file(self):
        source = {
            CAR_PHYSICS: "Ignore(0)\nIgnore(0)\n",
            OLD_BOAT_PHYSICS: "Ignore(0)\nIgnore(0)\n",
            "data/odephysics/vehicle/truckdi.phx": "Ignore(0)\nIgnore(0)\n",
        }
        result = apply_definition(source, NOCLIP_VEHICLES)
        self.assertEqual(result[CAR_PHYSICS].count("Ignore(1)"), 2)
        self.assertEqual(result[OLD_BOAT_PHYSICS].count("Ignore(1)"), 2)
        self.assertEqual(result["data/odephysics/vehicle/truckdi.phx"].count("Ignore(0)"), 2)

    def test_deeper_pockets_updates_all_five_characters(self):
        members = {}
        for member in (
            LOGAN_SKILLS,
            PURNA_SKILLS,
            SAMB_SKILLS,
            XIAN_SKILLS,
            JOHN_SKILLS,
        ):
            members[member] = (
                '<skill id="DeeperPockets" cat="Tree3" desc_params="2;4;6">\n'
                '  <effect id="InventorySize" change="2"/>\n'
                '</skill>\n'
            )

        result = apply_definition(members, DEEPER_POCKETS)
        for member in members:
            self.assertIn('desc_params="6;12;18"', result[member])
            self.assertIn('change="6"', result[member])
            self.assertIn('desc_params="2;4;6"', members[member])

    def test_deeper_pockets_missing_character_fails_closed(self):
        source = {
            LOGAN_SKILLS: (
                '<skill id="DeeperPockets" desc_params="2;4;6">'
                '<effect id="InventorySize" change="2"/>'
                '</skill>'
            )
        }
        with self.assertRaises(PatchError):
            apply_definition(source, DEEPER_POCKETS)

    def test_skip_intro_comments_only_native_active_intro(self):
        source = {
            INTRO_MOVIES: (
                'File("Intro_720p");\n'
                '//File("IntroDI_720p");\n'
                '//Subtitles("IntroDI_Subs.scr");\n'
            )
        }
        result = apply_definition(source, SKIP_INTRO_VIDEOS)[INTRO_MOVIES]
        self.assertIn('//File("Intro_720p");', result)
        self.assertIn('//File("IntroDI_720p");', result)

    def test_remove_reverb_uses_native_call_counts(self):
        text = (
            "!ReverbPreset(i)\n"
            "!ReverbWetDryMix(f)\n"
            + "".join(
                f"ReverbPreset({index})\nReverbWetDryMix(0.5)\n"
                for index in range(52)
            )
        )
        result = apply_definition(
            {GAME_AUDIO_EFFECTS: text}, REMOVE_REVERB_ECHO
        )[GAME_AUDIO_EFFECTS]
        self.assertEqual(
            len(re.findall(r"^//ReverbPreset\(", result, re.MULTILINE)),
            52,
        )
        self.assertEqual(
            len(re.findall(r"^//ReverbWetDryMix\(", result, re.MULTILINE)),
            52,
        )

    def test_improved_loot_updates_six_named_sets(self):
        colors = (
            "Color_White",
            "Color_Green",
            "Color_Blue",
            "Color_Violet",
            "Color_Orange",
        )
        sets = (
            ("ColorSet_Default", ("91.0", "7.0", "2.0", "0.0", "0.0")),
            ("ColorSet_LockPick1", ("0.0", "92.0", "6.0", "1.0", "0.0")),
            ("ColorSet_LockPick2", ("0.0", "85.0", "11.0", "3.0", "1.0")),
            ("ColorSet_LockPick3", ("0.0", "72.0", "21.0", "5.0", "2.0")),
            ("ColorSet_Ram", ("0.0", "10.0", "67.0", "20.0", "3.0")),
            ("ColorSet_MeleeFighter", ("0.0", "65.0", "35.0", "0.0", "0.0")),
        )
        text = ""
        for name, values in sets:
            text += f"DefColorSet({name})\n{{\n"
            text += "".join(
                f"    ColorWeight({color}, {value});\n"
                for color, value in zip(colors, values)
            )
            text += "}\n"

        result = apply_definition({DEFAULT_LOOT: text}, IMPROVED_LOOT)[DEFAULT_LOOT]
        self.assertIn("ColorWeight(Color_White, 55.0)", result)
        self.assertIn("ColorWeight(Color_Green, 6.0)", result)
        self.assertIn("ColorWeight(Color_Violet, 52.0)", result)
        self.assertIn("ColorWeight(Color_Orange, 11.0)", result)

    def test_missing_member_fails_closed(self):
        with self.assertRaises(PatchError):
            apply_definition({}, REDUCE_SPRINT_STAMINA)

    def test_wrong_prior_value_fails_closed(self):
        source = {
            DEFAULT_LEVELS: '<prop n="MoveSprintStaminaConsumption" v="0.04"/>'
        }
        with self.assertRaises(PatchError):
            apply_definition(source, REDUCE_SPRINT_STAMINA)

    def test_direct_patch_catalog_is_unique_and_excludes_unresolved_noclip(self):
        self.assertEqual(len(DIRECT_PATCHES), 13)
        self.assertEqual(len(DIRECT_PATCHES), len(set(DIRECT_PATCHES)))
        self.assertNotIn(NOCLIP_VEHICLES.name, DIRECT_PATCHES)
        self.assertIn(SKIP_INTRO_VIDEOS.name, DIRECT_PATCHES)
        self.assertIn(REMOVE_REVERB_ECHO.name, DIRECT_PATCHES)
        self.assertIn(IMPROVED_LOOT.name, DIRECT_PATCHES)


if __name__ == "__main__":
    unittest.main()
