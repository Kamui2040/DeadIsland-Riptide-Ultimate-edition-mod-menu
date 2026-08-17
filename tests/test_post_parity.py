import unittest

from dirue.definitions import DEFAULT_LEVELS, apply_definition
from dirue.errors import PatchError
from dirue.post_parity import HOLD_EVEN_MORE_AMMO, POST_PARITY_PATCHES


class PostParityAmmoTests(unittest.TestCase):
    def test_9999_ammo_updates_all_three_validated_capacities(self):
        source = {
            DEFAULT_LEVELS: "\n".join(
                (
                    '<prop n="MaxAmmoPistol" v="50"/>',
                    '<prop n="MaxAmmoRifle" v="60"/>',
                    '<prop n="MaxAmmoShotgun" v="20"/>',
                )
            )
        }

        result = apply_definition(source, HOLD_EVEN_MORE_AMMO)[DEFAULT_LEVELS]

        self.assertEqual(result.count('v="9999"'), 3)
        self.assertIn('<prop n="MaxAmmoPistol" v="9999"/>', result)
        self.assertIn('<prop n="MaxAmmoRifle" v="9999"/>', result)
        self.assertIn('<prop n="MaxAmmoShotgun" v="9999"/>', result)
        self.assertIn('v="50"', source[DEFAULT_LEVELS])
        self.assertIn('v="60"', source[DEFAULT_LEVELS])
        self.assertIn('v="20"', source[DEFAULT_LEVELS])

    def test_9999_ammo_fails_closed_on_non_pristine_prior(self):
        source = {
            DEFAULT_LEVELS: "\n".join(
                (
                    '<prop n="MaxAmmoPistol" v="200"/>',
                    '<prop n="MaxAmmoRifle" v="60"/>',
                    '<prop n="MaxAmmoShotgun" v="20"/>',
                )
            )
        }

        with self.assertRaises(PatchError):
            apply_definition(source, HOLD_EVEN_MORE_AMMO)

    def test_post_parity_catalog_contains_only_9999_ammo_for_now(self):
        self.assertEqual(
            POST_PARITY_PATCHES,
            {"hold_even_more_ammo": HOLD_EVEN_MORE_AMMO},
        )


if __name__ == "__main__":
    unittest.main()
