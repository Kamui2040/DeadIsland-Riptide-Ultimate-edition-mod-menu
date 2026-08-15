import codecs
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from dirue.definitions import DEFAULT_LEVELS, INTRO_MOVIES
from dirue.engine import build_candidate
from dirue.errors import PatchError, ValidationError


class CandidateBuilderTests(unittest.TestCase):
    def test_builds_candidate_without_changing_source(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            source = td / "Data0.pak"
            candidate = td / "candidate.pak"
            with ZipFile(source, "w") as archive:
                archive.writestr(
                    DEFAULT_LEVELS,
                    (
                        '<prop n="MoveSprintStaminaConsumption" v="0.05"/>\n'
                        '<prop n="JumpStaminaCost" v="0.06"/>\n'
                    ),
                )
                archive.writestr("data/untouched.scr", "unchanged\n")
            source_before = source.read_bytes()

            result = build_candidate(
                source,
                candidate,
                ["reduce_sprint_stamina", "reduce_jump_stamina"],
            )

            self.assertEqual(source.read_bytes(), source_before)
            self.assertEqual(result.entry_count, 2)
            self.assertEqual(result.changed_members, (DEFAULT_LEVELS,))
            with ZipFile(candidate, "r") as archive:
                text = archive.read(DEFAULT_LEVELS).decode("utf-8")
                self.assertIn('v="0.03"', text)
                self.assertEqual(archive.read("data/untouched.scr"), b"unchanged\n")

    def test_preserves_utf8_bom_on_changed_member(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            source = td / "Data0.pak"
            candidate = td / "candidate.pak"
            with ZipFile(source, "w") as archive:
                archive.writestr(
                    DEFAULT_LEVELS,
                    codecs.BOM_UTF8
                    + b'<prop n="MoveSprintStaminaConsumption" v="0.05"/>',
                )
            build_candidate(source, candidate, ["reduce_sprint_stamina"])
            with ZipFile(candidate, "r") as archive:
                self.assertTrue(archive.read(DEFAULT_LEVELS).startswith(codecs.BOM_UTF8))

    def test_rejects_unready_noclip_option(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            source = td / "Data0.pak"
            candidate = td / "candidate.pak"
            with ZipFile(source, "w") as archive:
                archive.writestr("data/a.scr", "x")
            with self.assertRaises(PatchError):
                build_candidate(source, candidate, ["noclip_vehicles"])
            self.assertFalse(candidate.exists())

    def test_rejects_noop_source_that_is_not_pristine(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            source = td / "Data0.pak"
            candidate = td / "candidate.pak"
            with ZipFile(source, "w") as archive:
                archive.writestr(INTRO_MOVIES, '//File("Intro_720p");\n')
            with self.assertRaises(PatchError):
                build_candidate(source, candidate, ["skip_intro_videos"])
            self.assertFalse(candidate.exists())

    def test_refuses_existing_destination(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            source = td / "Data0.pak"
            candidate = td / "candidate.pak"
            with ZipFile(source, "w") as archive:
                archive.writestr(
                    DEFAULT_LEVELS,
                    '<prop n="MoveSprintStaminaConsumption" v="0.05"/>',
                )
            candidate.write_bytes(b"existing")
            with self.assertRaises(ValidationError):
                build_candidate(source, candidate, ["reduce_sprint_stamina"])
            self.assertEqual(candidate.read_bytes(), b"existing")


if __name__ == "__main__":
    unittest.main()
