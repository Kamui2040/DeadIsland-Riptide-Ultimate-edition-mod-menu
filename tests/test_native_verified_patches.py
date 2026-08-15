import re
import unittest

from dirue.errors import PatchError
from dirue.patches import (
    replace_color_weight_set,
    replace_named_call_value,
    set_quoted_call_commented,
    set_reverb_enabled,
)


class NativeVerifiedPatchTests(unittest.TestCase):
    def test_intro_toggle_round_trip_preserves_crlf(self):
        source = '  File("Intro_720p");\r\n//File("Other");\r\n'
        disabled = set_quoted_call_commented(
            source,
            call_name="File",
            argument="Intro_720p",
            commented=True,
        )
        self.assertEqual(
            disabled,
            '  //File("Intro_720p");\r\n//File("Other");\r\n',
        )
        self.assertEqual(
            set_quoted_call_commented(
                disabled,
                call_name="File",
                argument="Intro_720p",
                commented=False,
            ),
            source,
        )

    def test_intro_toggle_rejects_duplicate_target(self):
        source = 'File("Intro_720p");\nFile("Intro_720p");\n'
        with self.assertRaises(PatchError):
            set_quoted_call_commented(
                source,
                call_name="File",
                argument="Intro_720p",
                commented=True,
            )

    def test_loot_edit_stays_in_named_color_set(self):
        source = (
            "DefColorSet(ColorSet_Default)\n"
            "{\n"
            "    ColorWeight(Color_White, 91.0);\n"
            "    ColorWeight(Color_Green, 7.0);\n"
            "    ColorWeight(Color_Blue, 2.0);\n"
            "    ColorWeight(Color_Violet, 0.0);\n"
            "    ColorWeight(Color_Orange, 0.0);\n"
            "}\n"
            "DefColorSet(ColorSet_Other)\n"
            "{\n"
            "    ColorWeight(Color_White, 1.0);\n"
            "}\n"
        )
        expected = {
            "Color_White": "91.0",
            "Color_Green": "7.0",
            "Color_Blue": "2.0",
            "Color_Violet": "0.0",
            "Color_Orange": "0.0",
        }
        desired = {
            "Color_White": "55.0",
            "Color_Green": "32.0",
            "Color_Blue": "8.0",
            "Color_Violet": "3.0",
            "Color_Orange": "2.0",
        }
        result = replace_color_weight_set(source, "ColorSet_Default", expected, desired)
        self.assertIn("ColorWeight(Color_White, 55.0)", result)
        self.assertIn("ColorWeight(Color_White, 1.0)", result)

    def test_loot_edit_rejects_wrong_prior_value(self):
        source = (
            "DefColorSet(ColorSet_Default)\n"
            "{\n"
            "    ColorWeight(Color_White, 90.0);\n"
            "}\n"
        )
        with self.assertRaises(PatchError):
            replace_color_weight_set(
                source,
                "ColorSet_Default",
                {"Color_White": "91.0"},
                {"Color_White": "55.0"},
            )

    def test_named_call_value_uses_argument_identity(self):
        self.assertEqual(
            replace_named_call_value(
                'ParamBool("one_shot",0)',
                "ParamBool",
                "one_shot",
                "0",
                "1",
            ),
            'ParamBool("one_shot",1)',
        )

    def test_native_reverb_call_counts_are_enforced(self):
        source = (
            "!ReverbPreset(i)\n"
            "!ReverbWetDryMix(f)\n"
            + "".join(
                f"ReverbPreset({index})\nReverbWetDryMix(0.5)\n"
                for index in range(52)
            )
        )
        result = set_reverb_enabled(
            source,
            enabled=False,
            expected_preset_calls=52,
            expected_mix_calls=52,
        )
        self.assertEqual(
            len(re.findall(r"^//ReverbPreset\(", result, re.MULTILINE)),
            52,
        )
        self.assertEqual(
            len(re.findall(r"^//ReverbWetDryMix\(", result, re.MULTILINE)),
            52,
        )
        self.assertTrue(result.startswith("!//ReverbPreset(i)"))


if __name__ == "__main__":
    unittest.main()
