import unittest

from dirue.catalog import READY_PATCHES
from dirue.ui_catalog import CHECKBOX_OPTIONS, CHOICE_GROUPS, ready_ui_options


class UICatalogTests(unittest.TestCase):
    def test_ready_ui_options_match_semantic_catalog_exactly(self):
        ui_options = ready_ui_options()
        self.assertEqual(len(ui_options), 42)
        self.assertEqual(len(ui_options), len(set(ui_options)))
        self.assertEqual(set(ui_options), set(READY_PATCHES))

    def test_all_released_spawn_choices_are_available(self):
        forced = next(group for group in CHOICE_GROUPS if group.key == "forced_spawn")
        self.assertTrue(all(choice.enabled for choice in forced.choices))
        self.assertEqual(
            [(choice.label, choice.option) for choice in forced.choices],
            [
                ("Normal", None),
                ("Butchers", "force_butchers"),
                ("Rams", "force_rams"),
                ("Bloaters", "force_bloaters"),
                ("Thugs", "force_thugs"),
                ("Suiciders", "force_suiciders"),
                ("Bandits with guns", "force_bandits_guns"),
                ("Bandits with melee", "force_bandits_melee"),
            ],
        )

    def test_every_option_has_short_hover_help(self):
        self.assertTrue(CHECKBOX_OPTIONS)
        for item in CHECKBOX_OPTIONS:
            self.assertTrue(item.help_text.strip(), item.option)
            self.assertLessEqual(len(item.help_text), 100, item.option)

        self.assertTrue(CHOICE_GROUPS)
        for group in CHOICE_GROUPS:
            self.assertTrue(group.help_text.strip(), group.key)
            self.assertLessEqual(len(group.help_text), 100, group.key)
            for choice in group.choices:
                self.assertTrue(choice.note.strip(), f"{group.key}:{choice.label}")
                self.assertLessEqual(len(choice.note), 100, f"{group.key}:{choice.label}")

    def test_gameplay_options_are_grouped_by_theme(self):
        themes = {item.theme for item in CHECKBOX_OPTIONS if item.section == "Gameplay"}
        self.assertEqual(
            themes,
            {"Movement", "Combat", "Gear & loot", "Comfort", "Vehicles"},
        )

    def test_noclip_help_contains_stuck_warning(self):
        noclip = next(item for item in CHECKBOX_OPTIONS if item.option == "noclip_vehicles")
        self.assertIn("stuck", noclip.help_text.lower())


if __name__ == "__main__":
    unittest.main()
