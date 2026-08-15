import contextlib
import io
from pathlib import Path
import tempfile
import unittest
import zipfile

from dirue.archive import validate_archive
from dirue.cli import build_parser, main


class TransactionCliTests(unittest.TestCase):
    def make_zip(self, path: Path, content: bytes) -> None:
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("data/a", content)

    def test_install_parser_requires_explicit_hashes(self):
        digest = "a" * 64
        args = build_parser().parse_args(
            [
                "install-candidate",
                "/candidate.pak",
                "/live.pak",
                "/backup.pak",
                "--expected-live-sha256",
                digest,
                "--expected-candidate-sha256",
                digest,
            ]
        )
        self.assertEqual(args.expected_live_sha256, digest)
        self.assertEqual(args.expected_candidate_sha256, digest)

    def test_backup_install_restore_round_trip(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            live = root / "Data0.pak"
            backup = root / "Data0.pak.dirue-pristine"
            candidate = root / "candidate.pak"
            self.make_zip(live, b"base")
            source = validate_archive(live)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main(
                    [
                        "backup-pristine",
                        str(live),
                        str(backup),
                        "--expected-live-sha256",
                        source.sha256,
                    ]
                )
            self.assertEqual(code, 0)

            self.make_zip(candidate, b"modified")
            candidate_info = validate_archive(candidate)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main(
                    [
                        "install-candidate",
                        str(candidate),
                        str(live),
                        str(backup),
                        "--expected-live-sha256",
                        source.sha256,
                        "--expected-candidate-sha256",
                        candidate_info.sha256,
                    ]
                )
            self.assertEqual(code, 0)
            self.assertEqual(validate_archive(live).sha256, candidate_info.sha256)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main(
                    [
                        "restore-backup",
                        str(backup),
                        str(live),
                        "--expected-backup-sha256",
                        source.sha256,
                    ]
                )
            self.assertEqual(code, 0)
            self.assertEqual(validate_archive(live).sha256, source.sha256)


if __name__ == "__main__":
    unittest.main()
