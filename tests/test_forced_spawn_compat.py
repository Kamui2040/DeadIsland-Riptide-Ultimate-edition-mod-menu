import hashlib
import unittest
from unittest.mock import patch

from dirue.errors import PatchError
from dirue.forced_spawn import _AI_PRESET_PATTERN, _vector_digest
from dirue.forced_spawn_compat import (
    FORCE_BLOATERS,
    FORCE_BUTCHERS,
    FORCE_RAMS,
    FORCE_THUGS,
    ForcedSpawnCompatibilityEdit,
)


def _text(values):
    return "".join(
        f'\tSetField("m_AIPresets", "{value}");\r\n'
        for value in values
    )


class ForcedSpawnCompatibilityTests(unittest.TestCase):
    def test_released_modes_replace_164_and_preserve_ordinal_60(self):
        values = tuple(f"Native_{ordinal}" for ordinal in range(1, 166))
        for definition in (FORCE_BUTCHERS, FORCE_RAMS, FORCE_BLOATERS, FORCE_THUGS):
            with self.subTest(definition=definition.name):
                edit = definition.edits[0]
                with patch(
                    "dirue.forced_spawn._NATIVE_VECTOR_SHA256",
                    _vector_digest(values),
                ):
                    result = edit.apply(_text(values))
                result_values = tuple(
                    match.group("value") for match in _AI_PRESET_PATTERN.finditer(result)
                )
                self.assertEqual(len(result_values), 165)
                self.assertEqual(result_values[59], values[59])
                for ordinal, value in enumerate(result_values, 1):
                    if ordinal != 60:
                        self.assertEqual(value, edit.desired_value)

    def test_released_identifier_evidence_is_pinned(self):
        expected = {
            "force_butchers": (
                "ec4d6bedc647b7d142c57da6c56e83338601b2c999b80cca08429bdb18f5d951",
                2,
                55,
            ),
            "force_rams": (
                "e130867801c23bfee629df6ab83b4f1f353710c1cf89c62f081c67f08afd0caf",
                2,
                46,
            ),
            "force_bloaters": (
                "b6108d8f2f9ef99dee5440626562e53625b8b7de83de7eafacf8cef1eb3e601a",
                3,
                77,
            ),
            "force_thugs": (
                "efdbf3422daec1a9c960453a957ab5149383973ca97bcfb1c3e8f3cf3bff7f92",
                13,
                297,
            ),
        }
        for definition in (FORCE_BUTCHERS, FORCE_RAMS, FORCE_BLOATERS, FORCE_THUGS):
            with self.subTest(definition=definition.name):
                edit = definition.edits[0]
                digest, identifier_count, length = expected[definition.name]
                self.assertEqual(edit.desired_sha256, digest)
                self.assertEqual(edit.expected_identifier_count, identifier_count)
                self.assertEqual(len(edit.desired_value), length)
                self.assertEqual(
                    hashlib.sha256(edit.desired_value.encode("utf-8")).hexdigest(),
                    digest,
                )
                self.assertEqual(edit.preserved_ordinals, (60,))
                self.assertEqual(edit.expected_changed_count, 164)

    def test_wrong_literal_digest_fails_closed(self):
        values = tuple(f"Native_{ordinal}" for ordinal in range(1, 166))
        edit = ForcedSpawnCompatibilityEdit(
            "data/presets/aispawnbox_pre.def",
            "BS_Test",
            "0" * 64,
            1,
            (60,),
            164,
        )
        with patch(
            "dirue.forced_spawn._NATIVE_VECTOR_SHA256",
            _vector_digest(values),
        ):
            with self.assertRaises(PatchError):
                edit.apply(_text(values))

    def test_malformed_literal_fails_closed(self):
        values = tuple(f"Native_{ordinal}" for ordinal in range(1, 166))
        desired = "BS_Test bad"
        edit = ForcedSpawnCompatibilityEdit(
            "data/presets/aispawnbox_pre.def",
            desired,
            hashlib.sha256(desired.encode("utf-8")).hexdigest(),
            1,
            (60,),
            164,
        )
        with patch(
            "dirue.forced_spawn._NATIVE_VECTOR_SHA256",
            _vector_digest(values),
        ):
            with self.assertRaises(PatchError):
                edit.apply(_text(values))


if __name__ == "__main__":
    unittest.main()
