import unittest

from dirue.errors import PatchError
from dirue.patches import replace_varfloat_value, replace_xml_prop_value


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


if __name__ == "__main__":
    unittest.main()
