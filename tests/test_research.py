import unittest

from dirue.research import call_sites, firearm_items


class ResearchTests(unittest.TestCase):
    def test_call_sites_keep_block_identity(self):
        source = (
            'Physics("Car")\n'
            '{\n'
            '    Ignore(0);\n'
            '    Part("Door")\n'
            '    {\n'
            '        Ignore(1);\n'
            '    }\n'
            '}\n'
        )
        result = call_sites(source, "Ignore")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["arguments"], "0")
        self.assertEqual(result[1]["arguments"], "1")
        self.assertEqual(result[1]["block_path"][-1], "Part:Door")

    def test_firearm_items_group_calls_by_item(self):
        source = (
            'Item("Firearm_ColtGen")\n'
            '{\n'
            '    Upgrade("1")\n'
            '    {\n'
            '        ShotTime(1.0);\n'
            '        ReloadTime(4.0);\n'
            '    }\n'
            '}\n'
        )
        result = firearm_items(source)
        self.assertIn("Item:Firearm_ColtGen", result)
        calls = result["Item:Firearm_ColtGen"]
        self.assertEqual([entry["call"] for entry in calls], ["ShotTime", "ReloadTime"])
        self.assertEqual(calls[0]["block_path"][-1], "Upgrade:1")

    def test_firearm_items_ignore_commented_calls(self):
        source = (
            'Item("Firearm_M9Gen")\n'
            '{\n'
            '    //ReloadTime(0.5);\n'
            '    ReloadTime(1.5);\n'
            '}\n'
        )
        calls = firearm_items(source)["Item:Firearm_M9Gen"]
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["arguments"], "1.5")


if __name__ == "__main__":
    unittest.main()
