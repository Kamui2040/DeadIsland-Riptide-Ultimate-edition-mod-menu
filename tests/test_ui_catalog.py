import unittest

from dirue.catalog import READY_PATCHES
from dirue.ui_catalog import CHOICE_GROUPS, ready_ui_options


class UICatalogTests(unittest.TestCase):
    def test_ready_ui_options_match_semantic_catalog_exactly(self):
        ui_options = ready_ui_options()
        self.assertEqual(len(ui_options), 38)
        self.assertEqual(len(ui_options), len(set(ui_options)))
        self.assertEqual(set(ui_options), set(READY_PATCHES))

    def test_unresolved_spawn_choices_are_visible_but_disabled(self):
        forced = next(group for group in CHOICE_GROUPS if group.key == "forced_spawn")
        disabled = [choice for choice in forced.choices if not choice.enabled]

        self.assertEqual(
            [choice.label for choice in disabled],
            [
                "Butchers — unavailable",
                "Rams — unavailable",
                "Bloaters — unavailable",
                "Thugs — unavailable",
            ],
        )
        self.assertTrue(all(choice.option is None for choice in disabled))
        self.assertTrue(all(choice.note for choice in disabled))


if __name__ == "__main__":
    unittest.main()
