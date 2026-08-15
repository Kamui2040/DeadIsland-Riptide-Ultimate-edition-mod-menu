import unittest

from dirue.errors import PatchError
from dirue.zombie_size import (
    ZOMBIE_SIZE_PATCHES,
    _BASELINE_SCALE_SEQUENCES,
    _sequence_digest,
    replace_scale_sequence,
)


class ZombieSizeTests(unittest.TestCase):
    def test_replaces_only_validated_target_calls_and_preserves_crlf(self):
        source = (
            'AddField("m_ForcedBodyScaleMin", "1.0");\r\n'
            'AddField("other", "9");\r\n'
            'AddField("m_ForcedBodyScaleMin", "1.2"), // note\r\n'
            '//AddField("m_ForcedBodyScaleMin", "7");\r\n'
        )
        digest = _sequence_digest(("1.0", "1.2"))
        result = replace_scale_sequence(
            source,
            call_name="AddField",
            field_name="m_ForcedBodyScaleMin",
            expected_count=2,
            expected_digest=digest,
            desired_value="0.6",
        )
        self.assertEqual(
            result.count('AddField("m_ForcedBodyScaleMin", "0.6")'),
            2,
        )
        self.assertIn('AddField("other", "9")', result)
        self.assertIn('//AddField("m_ForcedBodyScaleMin", "7")', result)
        self.assertIn("\r\n", result)

    def test_wrong_count_or_digest_fails_closed(self):
        source = 'SetField("m_ForcedBodyScaleMax", "1.0");\n'
        digest = _sequence_digest(("1.0",))
        with self.assertRaises(PatchError):
            replace_scale_sequence(
                source,
                call_name="SetField",
                field_name="m_ForcedBodyScaleMax",
                expected_count=2,
                expected_digest=digest,
                desired_value="2.0",
            )
        with self.assertRaises(PatchError):
            replace_scale_sequence(
                source,
                call_name="SetField",
                field_name="m_ForcedBodyScaleMax",
                expected_count=1,
                expected_digest="0" * 64,
                desired_value="2.0",
            )

    def test_production_modes_use_only_counts_and_baseline_digests(self):
        self.assertEqual(
            set(ZOMBIE_SIZE_PATCHES),
            {
                "zombie_size_extra_small",
                "zombie_size_midget",
                "zombie_size_large",
                "zombie_size_supersize",
            },
        )
        self.assertEqual(len(_BASELINE_SCALE_SEQUENCES), 8)
        desired = {
            "zombie_size_extra_small": "0.3",
            "zombie_size_midget": "0.6",
            "zombie_size_large": "2.0",
            "zombie_size_supersize": "5.0",
        }
        for name, definition in ZOMBIE_SIZE_PATCHES.items():
            self.assertEqual(len(definition.edits), 8)
            self.assertEqual(
                {edit.desired_value for edit in definition.edits},
                {desired[name]},
            )
            self.assertTrue(all(edit.expected_count > 0 for edit in definition.edits))
            self.assertTrue(all(len(edit.expected_digest) == 64 for edit in definition.edits))


if __name__ == "__main__":
    unittest.main()
