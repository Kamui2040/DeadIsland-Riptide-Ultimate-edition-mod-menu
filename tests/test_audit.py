import unittest

from dirue.audit import (
    ResearchHint,
    _brace_paths,
    _deeper_pockets_state,
    _find_hint,
    _loot_groups,
    _reverb_state,
    _statement_ids,
    _xml_property_values,
)
from dirue.errors import ValidationError


class AuditTests(unittest.TestCase):
    def test_xml_property_audit_requires_unique_match(self):
        text = '<prop n="CameraDefaultFOV" v="62.5"/>'
        self.assertEqual(
            _xml_property_values(text, ("CameraDefaultFOV",)),
            {"CameraDefaultFOV": "62.5"},
        )
        with self.assertRaises(ValidationError):
            _xml_property_values(text + text, ("CameraDefaultFOV",))

    def test_deeper_pockets_audit_is_scoped(self):
        text = (
            '<skill id="Other" desc_params="x"><effect id="InventorySize" change="99"/></skill>\n'
            '<skill id="DeeperPockets" desc_params="2;4;6">'
            '<effect id="InventorySize" change="2"/></skill>'
        )
        self.assertEqual(
            _deeper_pockets_state(text),
            {"desc_params": "2;4;6", "inventory_change": "2"},
        )

    def test_reverb_audit_separates_active_and_commented(self):
        text = (
            '!ReverbPreset(i)\n!//ReverbWetDryMix(f)\n'
            'ReverbPreset(10)\n// ReverbWetDryMix(0.5)\n'
        )
        state = _reverb_state(text)
        self.assertEqual(state["declarations"]["preset_active"], 1)
        self.assertEqual(state["declarations"]["mix_commented"], 1)
        self.assertEqual(state["calls"]["preset_active"], 1)
        self.assertEqual(state["calls"]["mix_commented"], 1)

    def test_brace_paths_extract_short_identifiers(self):
        lines = ['Weapon("AutoGen")\n', '{\n', '  Upgrade("Level1")\n', '  {\n', '    ReloadTime(3.0)\n', '  }\n', '}\n']
        paths = _brace_paths(lines)
        self.assertEqual(paths[4], ("Weapon:AutoGen", "Upgrade:Level1"))

    def test_firearm_hint_uses_line_only_for_read_only_discovery(self):
        text = '\n'.join([
            'Weapon("AutoGen")',
            '{',
            '  Upgrade("Level1")',
            '  {',
            '    ReloadTime(2.95)',
            '  }',
            '}',
        ])
        result = _find_hint(text, ResearchHint("auto", "x", 6, "ReloadTime"), window=5)
        self.assertEqual(result["status"], "found")
        self.assertEqual(result["native_line"], 5)
        self.assertEqual(result["block_path"], ["Weapon:AutoGen", "Upgrade:Level1"])

    def test_loot_groups_report_weights_by_block(self):
        text = '''Loot("Chest")
{
 ColorWeight(Color_White, 91)
 ColorWeight(Color_Green, 7)
 ColorWeight(Color_Blue, 2)
 ColorWeight(Color_Violet, 0)
 ColorWeight(Color_Orange, 0)
}
'''
        groups = _loot_groups(text)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["block_path"], ["Loot:Chest"])
        self.assertEqual(groups[0]["weights"]["Color_White"], "91")

    def test_statement_ids_do_not_copy_full_lines(self):
        text = 'PlayMovie("intro_a") // details\n// PlayMovie("intro_b")\nnot a call\n'
        self.assertEqual(
            _statement_ids(text),
            [
                {"call": "PlayMovie", "argument": "intro_a", "commented": False},
                {"call": "PlayMovie", "argument": "intro_b", "commented": True},
            ],
        )


if __name__ == "__main__":
    unittest.main()
