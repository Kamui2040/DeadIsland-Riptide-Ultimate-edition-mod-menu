import unittest
from pathlib import Path

from dirue.cli import build_parser
from dirue.source_map import map_targets_to_native, source_targets


class SourceMapTests(unittest.TestCase):
    def test_source_targets_read_only_handler_sections(self):
        source = (
            "better_wep_upgrades_yes:\n"
            'TF_ReplaceLine(INV_GEN,"6",6,"        ShotTime(0.94);")\n'
            ';TF_ReplaceLine(INV_GEN,"7",7,"        ReloadTime(3.8);")\n'
            "better_wep_upgrades_no:\n"
            'TF_ReplaceLine(INV_GEN,"99",99,"        ShotTime(0.6);")\n'
            "betterweppov_72:\n"
            'TF_ReplaceLine(INV_spec,"6",6,"        AimFov(1.7);")\n'
            "next_label:\n"
        )
        sections, targets = source_targets(source)
        self.assertIn("better_wep_upgrades_yes", sections)
        self.assertIn("betterweppov_72", sections)
        self.assertEqual(
            targets,
            [
                {
                    "section": "better_wep_upgrades_yes",
                    "source_target": "INV_GEN",
                    "historical_line": 6,
                    "desired_call": "ShotTime",
                    "desired_arguments": "0.94",
                },
                {
                    "section": "betterweppov_72",
                    "source_target": "INV_spec",
                    "historical_line": 6,
                    "desired_call": "AimFov",
                    "desired_arguments": "1.7",
                },
            ],
        )

    def test_maps_placeholder_line_to_named_item_and_neighbors(self):
        native = (
            "sub main()\n"
            "{\n"
            'Item("Firearm_Test")\n'
            "{\n"
            "    ShotTime(0.6);\n"
            "    // upgrade placeholder\n"
            "    HandOffset(HandModification_Normal, [0.0,0.0,0.0]);\n"
            "}\n"
            "}\n"
        )
        target = {
            "section": "better_wep_upgrades_yes",
            "source_target": "INV_GEN",
            "historical_line": 6,
            "desired_call": "ReloadTime",
            "desired_arguments": "3.8",
        }
        result = map_targets_to_native(
            [target],
            {"INV_GEN": native, "INV_spec": native},
        )[0]
        self.assertEqual(result["native_item"], "Item:Firearm_Test")
        self.assertEqual(
            result["native_block_path"],
            ["sub main()", "Item:Firearm_Test"],
        )
        self.assertEqual(result["native_line"], {"kind": "comment"})
        self.assertEqual(result["previous_relevant_call"]["call"], "ShotTime")
        self.assertEqual(result["next_relevant_call"]["call"], "HandOffset")
        self.assertEqual(result["same_call_candidates"], [])

    def test_maps_same_call_candidates_across_neighboring_items(self):
        native = (
            "sub main()\n"
            "{\n"
            'Item("Firearm_A")\n'
            "{\n"
            "    ReloadTime(3.0);\n"
            "}\n"
            'Item("Firearm_B")\n'
            "{\n"
            "    ReloadTime(4.0);\n"
            "    ReloadTime(3.5);\n"
            "}\n"
            "}\n"
        )
        target = {
            "section": "better_wep_upgrades_yes",
            "source_target": "INV_GEN",
            "historical_line": 9,
            "desired_call": "ReloadTime",
            "desired_arguments": "2.65",
        }
        result = map_targets_to_native(
            [target],
            {"INV_GEN": native, "INV_spec": native},
        )[0]
        self.assertEqual(result["native_item"], "Item:Firearm_B")
        candidates = result["same_call_candidates"]
        self.assertEqual(
            [(entry["item"], entry["line_number"]) for entry in candidates],
            [
                ("Item:Firearm_B", 9),
                ("Item:Firearm_B", 10),
                ("Item:Firearm_A", 5),
            ],
        )
        self.assertEqual(candidates[0]["ordinal_for_call"], 1)
        self.assertEqual(candidates[1]["ordinal_for_call"], 2)
        self.assertEqual(
            candidates[0]["block_path"],
            ["sub main()", "Item:Firearm_B"],
        )

    def test_upgrade_insertions_report_upgrade_level_anchors(self):
        native = (
            "sub main()\n"
            "{\n"
            'Item("Firearm_A")\n'
            "{\n"
            "    UpgradeLevel(0);\n"
            "    ReloadTime(3.0);\n"
            "}\n"
            'Item("Firearm_B")\n'
            "{\n"
            "    UpgradeLevel(1);\n"
            "    // insertion placeholder\n"
            "}\n"
            "}\n"
        )
        target = {
            "section": "better_wep_upgrades_yes",
            "source_target": "INV_GEN",
            "historical_line": 11,
            "desired_call": "ReloadTime",
            "desired_arguments": "2.65",
        }
        result = map_targets_to_native(
            [target],
            {"INV_GEN": native, "INV_spec": native},
        )[0]
        anchors = result["upgrade_level_candidates"]
        self.assertEqual(anchors[0]["item"], "Item:Firearm_B")
        self.assertEqual(anchors[0]["arguments"], "1")
        self.assertEqual(anchors[0]["line_number"], 10)

    def test_cli_parser_defaults_source_to_tracked_ahk(self):
        args = build_parser().parse_args(["audit-source-map", "/game"])
        self.assertEqual(args.command, "audit-source-map")
        self.assertEqual(args.root, Path("/game"))
        self.assertEqual(args.source, Path("DIRUE.ahk"))


if __name__ == "__main__":
    unittest.main()
