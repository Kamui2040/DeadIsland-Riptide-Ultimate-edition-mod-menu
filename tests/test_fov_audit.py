import unittest

from dirue.errors import ValidationError
from dirue.fov_audit import FOV_RECOIL_ITEMS, recoil_sequences


class FovRecoilAuditTests(unittest.TestCase):
    def test_collects_exact_five_call_sequences(self):
        parts = ["sub main()\n{\n"]
        for item in FOV_RECOIL_ITEMS:
            parts.append(f'Item("{item}", CategoryType_Firearm)\n{{\n')
            for value in ("0.1", "0.2", "0.3", "0.4", "0.5"):
                parts.append(f"    ShootVertRecoil({value});\n")
            parts.append("}\n")
        parts.append("}\n")

        result = recoil_sequences("".join(parts))
        self.assertEqual(set(result), set(FOV_RECOIL_ITEMS))
        self.assertTrue(
            all(values == ["0.1", "0.2", "0.3", "0.4", "0.5"] for values in result.values())
        )

    def test_rejects_missing_or_ambiguous_call_count(self):
        parts = ["sub main()\n{\n"]
        for item in FOV_RECOIL_ITEMS:
            parts.append(f'Item("{item}", CategoryType_Firearm)\n{{\n')
            count = 4 if item == FOV_RECOIL_ITEMS[0] else 5
            for _ in range(count):
                parts.append("    ShootVertRecoil(0.1);\n")
            parts.append("}\n")
        parts.append("}\n")
        with self.assertRaisesRegex(ValidationError, "expected 5"):
            recoil_sequences("".join(parts))


if __name__ == "__main__":
    unittest.main()
