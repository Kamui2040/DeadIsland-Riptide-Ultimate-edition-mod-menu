import unittest

from dirue.catalog import READY_PATCHES
from dirue.ui_catalog import CHOICE_GROUPS, ready_ui_options


class UICatalogTests(unittest.TestCase):
    def test_ready_ui_options_match_semantic_catalog_exactly(self):
        ui_options = ready_ui_options()
        self.assertEqual(len(ui_options), 43)
        self.assertEqual(len(ui_options), len(set(ui_options)))
        self.assertEqual(set(ui_options), set(READY_PATCHES))

    def test_ammo_capacity_choices_include_released_and_9999_modes(self):
        ammo = next(group for group in CHOICE_GROUPS if group.key == "ammo_capacity")
        self.assertEqual(ammo.section, "Gameplay")
        self.assertEqual(
            [(choice.label, choice.option) for choice in ammo.choices],
            [
                ("Default", None),
                ("More ammo", "hold_more_ammo"),
                ("9999", "hold_even_more_ammo"),
            ],
        )

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


if __name__ == "__main__":
    unittest.main()
