import json
import unittest

from dirue.errors import ValidationError
from dirue.replacement_audit import game_ini_summary, menu_summary


class ReplacementAuditTests(unittest.TestCase):
    def test_game_ini_reports_identity_and_digests_not_raw_values(self):
        native = (
            'sub main()\n'
            '{\n'
            '    GameName("Dead Island Riptide - Definitive Edition");\n'
            '    //CrashCanShowMessageBox(0);\n'
            '}\n'
        ).encode()
        replacement = (
            'sub main()\n'
            '{\n'
            '    GameName("Dead Island Riptide - Definitive Edition, modded");\n'
            '    //CrashCanShowMessageBox(0);\n'
            '}\n'
        ).encode()

        result = game_ini_summary(native, replacement)

        self.assertEqual(result["native_call_count"], 2)
        self.assertEqual(result["replacement_call_count"], 2)
        self.assertEqual(len(result["changed_calls"]), 1)
        self.assertEqual(result["changed_calls"][0]["identity"], "GameName#1")
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn("Definitive Edition, modded", serialized)
        self.assertNotIn("Definitive Edition\"", serialized)

    def test_menu_detects_replacement_only_branding_component(self):
        native = b'''<XuiCanvas version="000c">
<XuiScene>
<Properties><Id>MenuMain</Id><Width>1280</Width></Properties>
<MyText><Properties><Id>T_GameVersion</Id><TextColor>white</TextColor></Properties></MyText>
</XuiScene>
</XuiCanvas>'''
        replacement = b'''<XuiCanvas version="000c">
<XuiScene>
<Properties><Id>MenuMain</Id><Width>1280</Width></Properties>
<MyText><Properties><Id>T_Mylogo</Id><Text>private branding text</Text></Properties></MyText>
<MyText><Properties><Id>T_GameVersion</Id><TextColor>white</TextColor></Properties></MyText>
</XuiScene>
</XuiCanvas>'''

        result = menu_summary(native, replacement)

        self.assertEqual(result["native_only_components"], [])
        self.assertEqual(result["replacement_only_components"], ["MyText:T_Mylogo"])
        self.assertTrue(result["equivalent_after_removing_replacement_only_components"])
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn("private branding text", serialized)

    def test_menu_reports_existing_component_property_change(self):
        native = b'''<XuiCanvas><XuiScene><Properties><Id>MenuMain</Id></Properties>
<MyText><Properties><Id>T_GameVersion</Id><TextColor>white</TextColor></Properties></MyText>
</XuiScene></XuiCanvas>'''
        replacement = b'''<XuiCanvas><XuiScene><Properties><Id>MenuMain</Id></Properties>
<MyText><Properties><Id>T_GameVersion</Id><TextColor>orange</TextColor></Properties></MyText>
</XuiScene></XuiCanvas>'''

        result = menu_summary(native, replacement)

        self.assertFalse(result["equivalent_after_removing_replacement_only_components"])
        changed = {
            item["identity"]: item["changed_properties"]
            for item in result["changed_components"]
        }
        self.assertIn("MyText:T_GameVersion", changed)
        self.assertEqual(changed["MyText:T_GameVersion"][0]["property"], "TextColor#1")

    def test_duplicate_component_identity_fails_closed(self):
        duplicate = b'''<XuiCanvas><XuiScene><Properties><Id>MenuMain</Id></Properties>
<MyText><Properties><Id>Same</Id></Properties></MyText>
<MyText><Properties><Id>Same</Id></Properties></MyText>
</XuiScene></XuiCanvas>'''

        with self.assertRaises(ValidationError):
            menu_summary(duplicate, duplicate)


if __name__ == "__main__":
    unittest.main()
