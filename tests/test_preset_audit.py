import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from dirue.preset_audit import (
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

    def test_semantic_delta_reports_only_unique_changed_facts(self):
        before = b'VarFloat("x", 1.0)\n<prop n="Y" v="2"/>\n'
        after = b'VarFloat("x", 0.1)\n<prop n="Y" v="3"/>\n'
        delta = _semantic_delta(before, after)
        self.assertIn({"key": "VarFloat:x", "native": "1.0", "preset": "0.1"}, delta)
        self.assertIn({"key": "prop:Y", "native": "2", "preset": "3"}, delta)

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
            self.assertEqual(result["members"][0]["status"], "different")
            self.assertEqual(native.read_bytes(), native_before)
            self.assertEqual(preset.read_bytes(), preset_before)


if __name__ == "__main__":
    unittest.main()
