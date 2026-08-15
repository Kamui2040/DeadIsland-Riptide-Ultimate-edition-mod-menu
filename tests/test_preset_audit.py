import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from dirue.preset_audit import (
    _semantic_complete,
    _semantic_complete_ignoring_layout_comments,
    _semantic_complete_ignoring_whitespace,
    _semantic_delta,
    _target_member,
    audit_preset_file,
)


class PresetAuditTests(unittest.TestCase):
    def test_target_member_prefers_exact_then_data_prefix(self):
        names = {"data/scripts/weather.scr", "data/presets/aispawnbox_pre.def", "direct.scr"}
        self.assertEqual(_target_member("direct.scr", names), "direct.scr")
        self.assertEqual(_target_member("scripts/weather.scr", names), "data/scripts/weather.scr")
        self.assertEqual(_target_member("aispawnbox_pre.def", names), "data/presets/aispawnbox_pre.def")
        self.assertIsNone(_target_member("missing.scr", names))

    def test_semantic_delta_reports_changed_facts(self):
        before = b'VarFloat("x", 1.0)\n<prop n="Y" v="2"/>\n'
        after = b'VarFloat("x", 0.1)\n<prop n="Y" v="3"/>\n'
        delta = _semantic_delta(before, after)
        self.assertIn({"key": "VarFloat:x", "native": "1.0", "preset": "0.1"}, delta)
        self.assertIn({"key": "prop:Y", "native": "2", "preset": "3"}, delta)

    def test_semantic_delta_numbers_repeated_identities(self):
        before = b'ParamFloat("health_mul",1.0)\nParamFloat("health_mul",2.0)\n'
        after = b'ParamFloat("health_mul",1.5)\nParamFloat("health_mul",2.5)\n'
        delta = _semantic_delta(before, after)
        self.assertIn(
            {"key": "ParamFloat:health_mul#1", "native": "1.0", "preset": "1.5"},
            delta,
        )
        self.assertIn(
            {"key": "ParamFloat:health_mul#2", "native": "2.0", "preset": "2.5"},
            delta,
        )

    def test_semantic_complete_accepts_value_only_change(self):
        before = b'ParamBool("one_shot",0);\r\n'
        after = b'ParamBool("one_shot",1);\n'
        self.assertTrue(_semantic_complete(before, after))

    def test_semantic_complete_accepts_simple_generic_call_argument_change(self):
        self.assertTrue(_semantic_complete(b'Chance(1);\n', b'Chance(2);\n'))

    def test_semantic_complete_rejects_unclassified_change(self):
        before = b'DIRECTIVE one\n'
        after = b'DIRECTIVE two\n'
        self.assertFalse(_semantic_complete(before, after))
        self.assertFalse(_semantic_complete_ignoring_whitespace(before, after))

    def test_whitespace_tolerant_completeness_keeps_code_identity(self):
        before = b'  ParamBool("one_shot",0);\n\n'
        after = b'\tParamBool("one_shot",1);   \n'
        self.assertFalse(_semantic_complete(before, after))
        self.assertTrue(_semantic_complete_ignoring_whitespace(before, after))

    def test_layout_comment_tolerant_completeness_preserves_comment_state(self):
        before = b'ParamBool("one_shot",0); // native note\n'
        after = b'ParamBool("one_shot",1); // preset note\n'
        self.assertFalse(_semantic_complete(before, after))
        self.assertFalse(_semantic_complete_ignoring_whitespace(before, after))
        self.assertTrue(_semantic_complete_ignoring_layout_comments(before, after))
        self.assertFalse(
            _semantic_complete_ignoring_layout_comments(
                b'// ParamBool("one_shot",0);\n',
                b'ParamBool("one_shot",1);\n',
            )
        )

    def test_preset_comparison_is_read_only(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            native = td / "Data0.pak"
            preset = td / "preset.zip"
            with ZipFile(native, "w") as zf:
                zf.writestr("data/a.scr", 'VarFloat("x", 1.0)')
            with ZipFile(preset, "w") as zf:
                zf.writestr("a.scr", 'VarFloat("x", 0.1)')
            native_before = native.read_bytes()
            preset_before = preset.read_bytes()
            with patch("dirue.preset_audit.validate_archive") as validate:
                validate.return_value.size = len(preset_before)
                validate.return_value.sha256 = "preset-hash"
                validate.return_value.entry_count = 1
                result = audit_preset_file(preset, native)
            member = result["members"][0]
            self.assertEqual(member["status"], "different")
            self.assertTrue(member["semantic_complete"])
            self.assertTrue(member["semantic_complete_ignoring_whitespace"])
            self.assertTrue(member["semantic_complete_ignoring_layout_comments"])
            self.assertEqual(native.read_bytes(), native_before)
            self.assertEqual(preset.read_bytes(), preset_before)


if __name__ == "__main__":
    unittest.main()
