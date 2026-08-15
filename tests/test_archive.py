from pathlib import Path
import tempfile
import unittest
import warnings
import zipfile

from dirue.archive import (
    ensure_pristine_backup,
    install_candidate,
    rebuild_from_worktree,
    restore_backup,
    safe_extract,
    validate_archive,
)
from dirue.errors import ValidationError


class ArchiveTests(unittest.TestCase):
    def make_zip(self, path: Path, files: dict[str, bytes]) -> None:
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, content in files.items():
                archive.writestr(name, content)

    def test_validate_extract_rebuild(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "Data0.pak"
            self.make_zip(source, {"data/a.txt": b"old", "data/b.txt": b"keep"})
            info = validate_archive(source, required_entries=("data/a.txt",))
            self.assertEqual(info.entry_count, 2)

            worktree = root / "work"
            safe_extract(source, worktree)
            (worktree / "data/a.txt").write_bytes(b"new")
            (worktree / "data/c.txt").write_bytes(b"added")
            candidate = root / "candidate.pak"
            rebuilt = rebuild_from_worktree(source, worktree, candidate)
            self.assertEqual(rebuilt.entry_count, 3)
            with zipfile.ZipFile(candidate) as archive:
                self.assertEqual(archive.read("data/a.txt"), b"new")
                self.assertEqual(archive.read("data/b.txt"), b"keep")
                self.assertEqual(archive.read("data/c.txt"), b"added")

    def test_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.pak"
            self.make_zip(path, {"../escape": b"no"})
            with self.assertRaises(ValidationError):
                validate_archive(path)

    def test_backup_install_restore(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            live = root / "Data0.pak"
            candidate = root / "candidate.pak"
            backup = root / "Data0.pak.dirue-pristine"
            self.make_zip(live, {"data/value": b"original"})
            self.make_zip(candidate, {"data/value": b"modified"})

            live_info = validate_archive(live)
            candidate_info = validate_archive(candidate)
            pristine = ensure_pristine_backup(
                live,
                backup,
                expected_live_sha256=live_info.sha256,
            )
            original_hash = pristine.sha256
            installed = install_candidate(
                candidate,
                live,
                backup,
                expected_live_sha256=original_hash,
                expected_candidate_sha256=candidate_info.sha256,
            )
            self.assertNotEqual(installed.sha256, original_hash)
            restored = restore_backup(
                backup,
                live,
                expected_backup_sha256=original_hash,
            )
            self.assertEqual(restored.sha256, original_hash)

    def test_rejects_duplicate_member_names(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "duplicate.pak"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr("data/a.txt", b"first")
                    archive.writestr("data/a.txt", b"second")
            with self.assertRaises(ValidationError):
                validate_archive(path)

    def test_invalid_candidate_leaves_live_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            live = root / "Data0.pak"
            backup = root / "Data0.pak.dirue-pristine"
            candidate = root / "candidate.pak"
            self.make_zip(live, {"data/value": b"original"})
            original = validate_archive(live).sha256
            ensure_pristine_backup(
                live,
                backup,
                expected_live_sha256=original,
            )
            candidate.write_bytes(b"not a zip")

            with self.assertRaises(ValidationError):
                install_candidate(
                    candidate,
                    live,
                    backup,
                    expected_live_sha256=original,
                )
            self.assertEqual(validate_archive(live).sha256, original)

    def test_existing_pristine_backup_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            live = root / "Data0.pak"
            backup = root / "Data0.pak.dirue-pristine"
            self.make_zip(live, {"data/value": b"original"})
            original = validate_archive(live).sha256
            original_backup = ensure_pristine_backup(
                live,
                backup,
                expected_live_sha256=original,
            ).sha256
            self.make_zip(live, {"data/value": b"later"})

            existing = ensure_pristine_backup(live, backup)
            self.assertEqual(existing.sha256, original_backup)

    def test_expected_backup_baseline_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            live = root / "Data0.pak"
            backup = root / "Data0.pak.dirue-pristine"
            self.make_zip(live, {"data/value": b"original"})
            original = validate_archive(live).sha256
            self.make_zip(backup, {"data/value": b"wrong"})

            with self.assertRaises(ValidationError):
                ensure_pristine_backup(
                    live,
                    backup,
                    expected_live_sha256=original,
                )
            self.assertEqual(validate_archive(live).sha256, original)

    def test_unexpected_live_source_leaves_live_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            live = root / "Data0.pak"
            backup = root / "Data0.pak.dirue-pristine"
            candidate = root / "candidate.pak"
            self.make_zip(live, {"data/value": b"original"})
            original = validate_archive(live).sha256
            ensure_pristine_backup(
                live,
                backup,
                expected_live_sha256=original,
            )
            self.make_zip(candidate, {"data/value": b"modified"})
            self.make_zip(live, {"data/value": b"unexpected"})
            unexpected = validate_archive(live).sha256

            with self.assertRaises(ValidationError):
                install_candidate(
                    candidate,
                    live,
                    backup,
                    expected_live_sha256=original,
                )
            self.assertEqual(validate_archive(live).sha256, unexpected)

    def test_wrong_backup_or_candidate_count_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            live = root / "Data0.pak"
            backup = root / "Data0.pak.dirue-pristine"
            candidate = root / "candidate.pak"
            self.make_zip(live, {"data/value": b"original"})
            original = validate_archive(live).sha256
            self.make_zip(backup, {"data/value": b"wrong"})
            self.make_zip(candidate, {"data/value": b"modified"})

            with self.assertRaises(ValidationError):
                install_candidate(
                    candidate,
                    live,
                    backup,
                    expected_live_sha256=original,
                )

            self.make_zip(backup, {"data/value": b"original"})
            self.make_zip(
                candidate,
                {"data/value": b"modified", "data/extra": b"unexpected"},
            )
            with self.assertRaises(ValidationError):
                install_candidate(
                    candidate,
                    live,
                    backup,
                    expected_live_sha256=original,
                )

    def test_restore_checks_expected_backup_hash_and_recovers_missing_live(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            live = root / "Data0.pak"
            backup = root / "Data0.pak.dirue-pristine"
            self.make_zip(backup, {"data/value": b"original"})
            original = validate_archive(backup).sha256

            with self.assertRaises(ValidationError):
                restore_backup(
                    backup,
                    live,
                    expected_backup_sha256="0" * 64,
                )
            self.assertFalse(live.exists())

            restored = restore_backup(
                backup,
                live,
                expected_backup_sha256=original,
            )
            self.assertEqual(restored.sha256, original)


if __name__ == "__main__":
    unittest.main()
