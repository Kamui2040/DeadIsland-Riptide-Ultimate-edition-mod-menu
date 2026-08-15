import unittest

from dirue.errors import PatchError
from dirue.patches import (
    replace_call_value,
    replace_deeper_pockets_skill,
    replace_varfloat_value,
    replace_xml_prop_value,
    set_reverb_enabled,
)


class PatchTests(unittest.TestCase):
    def test_replace_xml_prop_value(self):
        text = '<prop n="MoveSprintStaminaConsumption" v="0.05"/>'
        self.assertEqual(
            replace_xml_prop_value(text, "MoveSprintStaminaConsumption", "0.05", "0.03"),
            '<prop n="MoveSprintStaminaConsumption" v="0.03"/>',
        )

    def test_xml_prop_requires_expected_old_value(self):
        with self.assertRaises(PatchError):
            replace_xml_prop_value(
                '<prop n="JumpStaminaCost" v="0.04"/>', "JumpStaminaCost", "0.06", "0.03"
            )

    def test_xml_prop_rejects_ambiguous_matches(self):
        text = '<prop n="X" v="1"/>\n<prop n="X" v="1"/>'
        with self.assertRaises(PatchError):
            replace_xml_prop_value(text, "X", "1", "2")

    def test_replace_varfloat_value(self):
        text = 'VarFloat("f_pp_glow_factor", 1.0) // comment'
        self.assertEqual(
            replace_varfloat_value(text, "f_pp_glow_factor", "1.0", "0.1"),
            'VarFloat("f_pp_glow_factor", 0.1) // comment',
        )

    def test_replace_call_value_preserves_comments(self):
        text = "    Ignore(0) // first\n    Ignore(0) // second\n"
        self.assertEqual(
            replace_call_value(text, "Ignore", "0", "1", expected_matches=2),
            "    Ignore(1) // first\n    Ignore(1) // second\n",
        )

    def test_replace_call_value_requires_expected_count(self):
        with self.assertRaises(PatchError):
            replace_call_value("Ignore(0)\n", "Ignore", "0", "1", expected_matches=2)

    def test_deeper_pockets_is_scoped_to_named_skill(self):
        text = (
            '<skill id="Other" desc_params="2;4;6">\n'
            '  <effect id="InventorySize" change="99"/>\n'
            '</skill>\n'
            '<skill id="DeeperPockets" cat="Tree3" desc_params="2;4;6">\n'
            '  <effect id="InventorySize" change="2"/>\n'
            '</skill>\n'
        )
        result = replace_deeper_pockets_skill(
            text,
            expected_desc_params="2;4;6",
            new_desc_params="6;12;18",
            expected_inventory_change="2",
            new_inventory_change="6",
        )
        self.assertIn('<skill id="Other" desc_params="2;4;6">', result)
        self.assertIn('<effect id="InventorySize" change="99"/>', result)
        self.assertIn('id="DeeperPockets" cat="Tree3" desc_params="6;12;18"', result)
        self.assertIn('<effect id="InventorySize" change="6"/>', result)

    def test_deeper_pockets_rejects_wrong_prior_state(self):
        text = (
            '<skill id="DeeperPockets" desc_params="2;4;6">\n'
            '  <effect id="InventorySize" change="3"/>\n'
            '</skill>\n'
        )
        with self.assertRaises(PatchError):
            replace_deeper_pockets_skill(
                text,
                expected_desc_params="2;4;6",
                new_desc_params="6;12;18",
                expected_inventory_change="2",
                new_inventory_change="6",
            )

    def test_deeper_pockets_rejects_duplicate_skill(self):
        block = (
            '<skill id="DeeperPockets" desc_params="2;4;6">\n'
            '  <effect id="InventorySize" change="2"/>\n'
            '</skill>\n'
        )
        with self.assertRaises(PatchError):
            replace_deeper_pockets_skill(
                block + block,
                expected_desc_params="2;4;6",
                new_desc_params="6;12;18",
                expected_inventory_change="2",
                new_inventory_change="6",
            )

    def test_reverb_disable_comments_only_reverb_directives(self):
        text = (
            '!ReverbPreset(i)\n'
            '!ReverbWetDryMix(f)\n'
            '!Echo(i, f, f, f)\n'
            '    ReverbPreset(24)\n'
            '    ReverbWetDryMix(0.3)\n'
            '    //Echo(3, 500, 0.2, 0.1)\n'
        )
        expected = (
            '!//ReverbPreset(i)\n'
            '!//ReverbWetDryMix(f)\n'
            '!Echo(i, f, f, f)\n'
            '    //ReverbPreset(24)\n'
            '    //ReverbWetDryMix(0.3)\n'
            '    //Echo(3, 500, 0.2, 0.1)\n'
        )
        self.assertEqual(
            set_reverb_enabled(
                text,
                enabled=False,
                expected_preset_calls=1,
                expected_mix_calls=1,
            ),
            expected,
        )

    def test_reverb_toggle_round_trip_preserves_crlf(self):
        text = (
            '!ReverbPreset(i)\r\n'
            '!ReverbWetDryMix(f)\r\n'
            '  ReverbPreset(14)\r\n'
            '  ReverbWetDryMix(0.6)//0,6\r\n'
        )
        disabled = set_reverb_enabled(
            text,
            enabled=False,
            expected_preset_calls=1,
            expected_mix_calls=1,
        )
        self.assertEqual(
            set_reverb_enabled(
                disabled,
                enabled=True,
                expected_preset_calls=1,
                expected_mix_calls=1,
            ),
            text,
        )

    def test_reverb_requires_expected_match_counts(self):
        text = (
            '!ReverbPreset(i)\n'
            '!ReverbWetDryMix(f)\n'
            'ReverbPreset(24)\n'
            'ReverbWetDryMix(0.3)\n'
        )
        with self.assertRaises(PatchError):
            set_reverb_enabled(
                text,
                enabled=False,
                expected_preset_calls=2,
                expected_mix_calls=1,
            )

    def test_reverb_rejects_mixed_source_state(self):
        text = (
            '!ReverbPreset(i)\n'
            '!ReverbWetDryMix(f)\n'
            '//ReverbPreset(24)\n'
            'ReverbWetDryMix(0.3)\n'
        )
        with self.assertRaises(PatchError):
            set_reverb_enabled(
                text,
                enabled=False,
                expected_preset_calls=1,
                expected_mix_calls=1,
            )


if __name__ == "__main__":
    unittest.main()
