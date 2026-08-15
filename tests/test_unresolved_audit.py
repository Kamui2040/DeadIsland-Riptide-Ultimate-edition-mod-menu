import unittest

from dirue.errors import ValidationError
from dirue.unresolved_audit import (
    forced_spawn_donor_summary,
    structural_diff,
    structural_tokens,
)


class UnresolvedPresetAuditTests(unittest.TestCase):
    def test_value_only_call_changes_do_not_look_structural(self):
        native = (
            'ParamFloat("health_mul", 10.0)\r\n'
            'VarFloat("f_value", 1.0)\r\n'
        )
        preset = (
            'ParamFloat("health_mul", 13.0)\r\n'
            'VarFloat("f_value", 0.25)\r\n'
        )
        result = structural_diff(native, preset)
        self.assertEqual(result["structural_change_count"], 0)

    def test_comment_state_change_is_reported_without_values(self):
        native = '//ParamBool("one_shot", 0)\r\n'
        preset = 'ParamBool("one_shot", 1)\r\n'
        result = structural_diff(native, preset)
        self.assertEqual(result["structural_change_count"], 1)
        text = str(result)
        self.assertIn("commented:call:ParamBool:one_shot", text)
        self.assertIn("call:ParamBool:one_shot", text)
        self.assertNotIn("one_shot\", 0", text)
        self.assertNotIn("one_shot\", 1", text)

    def test_unknown_line_shape_masks_literals_but_not_structure(self):
        native = 'if (Mode == 1) DoThing("alpha");\n'
        same_shape = 'if (Mode == 9) DoThing("beta");\n'
        changed_shape = 'while (Mode == 9) DoThing("beta");\n'
        self.assertEqual(
            structural_diff(native, same_shape)["structural_change_count"],
            0,
        )
        self.assertEqual(
            structural_diff(native, changed_shape)["structural_change_count"],
            1,
        )

    def test_non_identifier_first_argument_is_hashed(self):
        tokens = structural_tokens('Call("secret/list;value", 1);\n')
        self.assertEqual(len(tokens), 1)
        token = str(tokens[0]["token"])
        self.assertIn("call:Call:sha256:", token)
        self.assertNotIn("secret/list;value", token)

    def test_forced_spawn_summary_reports_native_donor_without_raw_value(self):
        native = (
            'SetField("m_AIPresets", "A");\n'
            'SetField("m_AIPresets", "B");\n'
            'SetField("m_AIPresets", "C");\n'
        )
        preset = (
            'SetField("m_AIPresets", "B");\n'
            'SetField("m_AIPresets", "B");\n'
            'SetField("m_AIPresets", "B");\n'
        )
        result = forced_spawn_donor_summary(native, preset)
        self.assertEqual(result["total_calls"], 3)
        self.assertEqual(result["changed_count"], 2)
        self.assertEqual(result["changed_ordinals"], [1, 3])
        self.assertEqual(result["unique_desired_count"], 1)
        self.assertTrue(result["all_desired_have_native_donor"])
        self.assertEqual(result["desired_values"][0]["native_donor_ordinals"], [2])
        self.assertNotIn("'B'", str(result))

    def test_forced_spawn_count_mismatch_fails_closed(self):
        native = 'SetField("m_AIPresets", "A");\n'
        preset = (
            'SetField("m_AIPresets", "A");\n'
            'SetField("m_AIPresets", "B");\n'
        )
        with self.assertRaises(ValidationError):
            forced_spawn_donor_summary(native, preset)


if __name__ == "__main__":
    unittest.main()
