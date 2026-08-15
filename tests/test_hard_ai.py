import hashlib
import json
import unittest

from dirue.definitions import apply_definition
from dirue.errors import PatchError
from dirue.hard_ai import HARD_AI, HARD_AI_AUDIT_DIGEST, HARD_AI_ROWS


class HardAiTests(unittest.TestCase):
    def test_table_matches_accepted_audit_shape_and_digest(self):
        self.assertEqual(len(HARD_AI.edits), 209)
        self.assertEqual(len(HARD_AI_ROWS), 209)
        self.assertEqual(len({row[0] for row in HARD_AI_ROWS}), 57)
        self.assertTrue(all(row[1] == "ParamFloat" for row in HARD_AI_ROWS))
        canonical = json.dumps(HARD_AI_ROWS, separators=(",", ":"))
        self.assertEqual(
            hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            HARD_AI_AUDIT_DIGEST,
        )

    def test_definition_applies_every_audited_named_value(self):
        lines: dict[str, list[str]] = {}
        for edit in HARD_AI.edits:
            lines.setdefault(edit.member, []).append(
                f'{edit.call_name}("{edit.argument}",{edit.expected_value})'
            )
        members = {member: "\r\n".join(values) for member, values in lines.items()}
        result = apply_definition(members, HARD_AI)
        for edit in HARD_AI.edits:
            self.assertIn(
                f'{edit.call_name}("{edit.argument}",{edit.desired_value})',
                result[edit.member],
            )

    def test_custom_31_preserves_the_released_special_scale(self):
        member = "data/ai/zombie/vessel_data_preset_custom_31.scr"
        edits = {edit.argument: edit for edit in HARD_AI.edits if edit.member == member}
        self.assertEqual(len(edits), 8)
        self.assertEqual((edits["health_mul"].expected_value, edits["health_mul"].desired_value), ("10.0", "13.0"))
        self.assertEqual((edits["head_health_influence"].expected_value, edits["head_health_influence"].desired_value), ("1.0", "0.16"))
        self.assertEqual((edits["left_arm_health_influence"].expected_value, edits["left_arm_health_influence"].desired_value), ("0.5", "0.08"))

    def test_wrong_prior_fails_closed(self):
        first = HARD_AI.edits[0]
        with self.assertRaises(PatchError):
            apply_definition(
                {first.member: f'{first.call_name}("{first.argument}",99.0)'},
                HARD_AI,
            )


if __name__ == "__main__":
    unittest.main()
