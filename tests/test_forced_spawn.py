import hashlib
import unittest
from unittest.mock import patch

from dirue.errors import PatchError
from dirue.forced_spawn import (
    FORCED_SPAWN_MEMBER,
    FORCE_BANDITS_GUNS,
    FORCE_BANDITS_MELEE,
    FORCE_SUICIDERS,
    ForcedSpawnDonorEdit,
    ForcedSpawnRecipeEdit,
    TokenRecipeReplacement,
    _AI_PRESET_PATTERN,
    _vector_digest,
)


def _text(values):
    return "".join(
        f'\tSetField("m_AIPresets", "{value}");\r\n'
        for value in values
    )


class ForcedSpawnTests(unittest.TestCase):
    def test_suicider_shape_uses_donor_and_preserves_only_donor_ordinal(self):
        values = tuple(f"value-{ordinal}" for ordinal in range(1, 166))
        donor = values[5]
        edit = ForcedSpawnDonorEdit(
            FORCED_SPAWN_MEMBER,
            donor_ordinal=6,
            donor_sha256=hashlib.sha256(donor.encode("utf-8")).hexdigest(),
            preserved_ordinals=(6,),
            expected_changed_count=164,
        )
        with patch("dirue.forced_spawn._NATIVE_VECTOR_SHA256", _vector_digest(values)):
            result = edit.apply(_text(values))

        result_values = tuple(
            match.group("value") for match in _AI_PRESET_PATTERN.finditer(result)
        )
        self.assertEqual(len(result_values), 165)
        self.assertTrue(all(value == donor for value in result_values))
        self.assertEqual(result.count("\n"), result.count("\r\n"))

    def test_armed_bandit_shape_preserves_special_and_donor_ordinals(self):
        values = tuple(f"value-{ordinal}" for ordinal in range(1, 166))
        donor = values[118]
        edit = ForcedSpawnDonorEdit(
            FORCED_SPAWN_MEMBER,
            donor_ordinal=119,
            donor_sha256=hashlib.sha256(donor.encode("utf-8")).hexdigest(),
            preserved_ordinals=(60, 119),
            expected_changed_count=163,
        )
        with patch("dirue.forced_spawn._NATIVE_VECTOR_SHA256", _vector_digest(values)):
            result = edit.apply(_text(values))

        result_values = tuple(
            match.group("value") for match in _AI_PRESET_PATTERN.finditer(result)
        )
        self.assertEqual(result_values[59], values[59])
        self.assertEqual(result_values[118], donor)
        for ordinal, value in enumerate(result_values, 1):
            if ordinal not in {60, 119}:
                self.assertEqual(value, donor)

    def test_recipe_reconstructs_target_from_native_whole_tokens(self):
        values = [f"Native_{ordinal}_Default" for ordinal in range(1, 166)]
        values[36] = "Other_Melee_Value"
        values[39] = "Spawn_Type_Armed_Default"
        values = tuple(values)
        base = values[39]
        donor = values[36]
        target = "Spawn_Type_Melee_Default"
        edit = ForcedSpawnRecipeEdit(
            FORCED_SPAWN_MEMBER,
            base_ordinal=40,
            base_value_sha256=hashlib.sha256(base.encode("utf-8")).hexdigest(),
            part_count=7,
            replacements=(
                TokenRecipeReplacement(
                    part_index=4,
                    donor_ordinal=37,
                    donor_part_index=2,
                    donor_value_sha256=hashlib.sha256(donor.encode("utf-8")).hexdigest(),
                    token_length=5,
                ),
            ),
            target_sha256=hashlib.sha256(target.encode("utf-8")).hexdigest(),
            preserved_ordinals=(60,),
            expected_changed_count=164,
        )
        with patch("dirue.forced_spawn._NATIVE_VECTOR_SHA256", _vector_digest(values)):
            result = edit.apply(_text(values))

        result_values = tuple(
            match.group("value") for match in _AI_PRESET_PATTERN.finditer(result)
        )
        self.assertEqual(result_values[59], values[59])
        for ordinal, value in enumerate(result_values, 1):
            if ordinal != 60:
                self.assertEqual(value, target)
        self.assertEqual(result.count("\n"), result.count("\r\n"))

    def test_recipe_wrong_target_digest_fails_closed(self):
        values = [f"Native_{ordinal}_Default" for ordinal in range(1, 166)]
        values[36] = "Other_Melee_Value"
        values[39] = "Spawn_Type_Armed_Default"
        values = tuple(values)
        edit = ForcedSpawnRecipeEdit(
            FORCED_SPAWN_MEMBER,
            base_ordinal=40,
            base_value_sha256=hashlib.sha256(values[39].encode("utf-8")).hexdigest(),
            part_count=7,
            replacements=(
                TokenRecipeReplacement(
                    part_index=4,
                    donor_ordinal=37,
                    donor_part_index=2,
                    donor_value_sha256=hashlib.sha256(values[36].encode("utf-8")).hexdigest(),
                    token_length=5,
                ),
            ),
            target_sha256="0" * 64,
            preserved_ordinals=(60,),
            expected_changed_count=164,
        )
        with patch("dirue.forced_spawn._NATIVE_VECTOR_SHA256", _vector_digest(values)):
            with self.assertRaises(PatchError):
                edit.apply(_text(values))

    def test_wrong_vector_digest_fails_closed(self):
        values = tuple(f"value-{ordinal}" for ordinal in range(1, 166))
        donor = values[5]
        edit = ForcedSpawnDonorEdit(
            FORCED_SPAWN_MEMBER,
            donor_ordinal=6,
            donor_sha256=hashlib.sha256(donor.encode("utf-8")).hexdigest(),
            preserved_ordinals=(6,),
            expected_changed_count=164,
        )
        with patch("dirue.forced_spawn._NATIVE_VECTOR_SHA256", "0" * 64):
            with self.assertRaises(PatchError):
                edit.apply(_text(values))

    def test_wrong_donor_digest_fails_closed(self):
        values = tuple(f"value-{ordinal}" for ordinal in range(1, 166))
        edit = ForcedSpawnDonorEdit(
            FORCED_SPAWN_MEMBER,
            donor_ordinal=6,
            donor_sha256="0" * 64,
            preserved_ordinals=(6,),
            expected_changed_count=164,
        )
        with patch("dirue.forced_spawn._NATIVE_VECTOR_SHA256", _vector_digest(values)):
            with self.assertRaises(PatchError):
                edit.apply(_text(values))

    def test_released_public_safe_definitions_keep_only_digests_and_ordinals(self):
        suicider = FORCE_SUICIDERS.edits[0]
        armed = FORCE_BANDITS_GUNS.edits[0]
        melee = FORCE_BANDITS_MELEE.edits[0]

        self.assertEqual(suicider.donor_ordinal, 6)
        self.assertEqual(suicider.preserved_ordinals, (6,))
        self.assertEqual(suicider.expected_changed_count, 164)
        self.assertEqual(
            suicider.donor_sha256,
            "eaa57a591c460bc45db948d5d4b284ed07ad290256ef201a37bc4197d918565d",
        )

        self.assertEqual(armed.donor_ordinal, 119)
        self.assertEqual(armed.preserved_ordinals, (60, 119))
        self.assertEqual(armed.expected_changed_count, 163)
        self.assertEqual(
            armed.donor_sha256,
            "2624988a60c5ce564006d96fdc6dc9fd28c918ec43a492e1f625c59c5ffb6209",
        )

        self.assertEqual(melee.base_ordinal, 40)
        self.assertEqual(melee.preserved_ordinals, (60,))
        self.assertEqual(melee.expected_changed_count, 164)
        self.assertEqual(melee.part_count, 47)
        self.assertEqual(len(melee.replacements), 6)
        self.assertEqual(
            melee.target_sha256,
            "77ab5589e4c2a6722f2bbad894781791a18d19ccfb87d6545e409a9caa1ecccb",
        )


if __name__ == "__main__":
    unittest.main()
