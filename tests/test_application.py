from pathlib import Path
import unittest
from unittest.mock import patch

from dirue.application import (
    SUPPORTED_PRISTINE_SHA256,
    ApplicationStatus,
    apply_selection,
    default_backup_path,
    inspect_game,
    restore_pristine,
    validate_selection,
)
from dirue.archive import ArchiveInfo
from dirue.engine import CandidateBuild
from dirue.errors import PatchError, ValidationError
from dirue.game import GameInstallation


BASELINE = next(iter(SUPPORTED_PRISTINE_SHA256))


class ApplicationServiceTests(unittest.TestCase):
    def _game(self, root: Path, sha256: str = BASELINE) -> GameInstallation:
        data0 = root / "DIR" / "Data0.pak"
        return GameInstallation(
            root=root,
            executable=root / "DeadIslandRiptideGame",
            data0=data0,
            archive=ArchiveInfo(
                path=data0,
                size=100,
                sha256=sha256,
                entry_count=3060,
            ),
        )

    def _archive(self, path: Path, sha256: str) -> ArchiveInfo:
        return ArchiveInfo(
            path=path,
            size=100,
            sha256=sha256,
            entry_count=3060,
        )

    def test_default_backup_path_is_sibling_and_non_overwriting_name(self):
        path = Path("/game/DIR/Data0.pak")
        self.assertEqual(
            default_backup_path(path),
            Path("/game/DIR/Data0.pak.dirue-pristine"),
        )

    def test_selection_rejects_unknown_duplicate_and_conflict(self):
        with self.assertRaises(PatchError):
            validate_selection(["not_ready"])
        with self.assertRaises(PatchError):
            validate_selection(["reduce_sprint_stamina", "reduce_sprint_stamina"])
        with self.assertRaises(PatchError):
            validate_selection(["camera_fov_72", "camera_fov_82"])

    def test_selection_accepts_compatible_ready_options(self):
        selected = validate_selection(
            ["reduce_sprint_stamina", "camera_fov_82", "force_bandits_melee"]
        )
        self.assertEqual(
            selected,
            ("reduce_sprint_stamina", "camera_fov_82", "force_bandits_melee"),
        )

    def test_inspect_game_reports_existing_supported_backup_state(self):
        root = Path("/game")
        game = self._game(root)
        backup_path = default_backup_path(game.data0)
        backup = self._archive(backup_path, game.archive.sha256)

        with patch("dirue.application.validate_game_root", return_value=game), patch(
            "pathlib.Path.exists", return_value=True
        ), patch("dirue.application.validate_archive", return_value=backup):
            status = inspect_game(root)

        self.assertEqual(status.backup, backup)
        self.assertTrue(status.live_matches_backup)

    def test_inspect_game_rejects_unknown_first_pristine_source(self):
        root = Path("/game")
        game = self._game(root, "b" * 64)

        with patch("dirue.application.validate_game_root", return_value=game), patch(
            "pathlib.Path.exists", return_value=False
        ):
            with self.assertRaisesRegex(ValidationError, "validated pristine"):
                inspect_game(root)

    def test_inspect_game_rejects_unrecognized_existing_backup(self):
        root = Path("/game")
        game = self._game(root, "c" * 64)
        backup_path = default_backup_path(game.data0)
        backup = self._archive(backup_path, "b" * 64)

        with patch("dirue.application.validate_game_root", return_value=game), patch(
            "pathlib.Path.exists", return_value=True
        ), patch("dirue.application.validate_archive", return_value=backup):
            with self.assertRaisesRegex(ValidationError, "not a validated pristine"):
                inspect_game(root)

    def test_apply_requires_restore_before_reapplying_over_modified_live(self):
        root = Path("/game")
        game = self._game(root, "c" * 64)
        backup_path = default_backup_path(game.data0)
        status = ApplicationStatus(
            game=game,
            backup_path=backup_path,
            backup=self._archive(backup_path, BASELINE),
            live_matches_backup=False,
        )

        with patch("dirue.application.inspect_game", return_value=status), patch(
            "dirue.application.ensure_pristine_backup"
        ) as ensure_backup:
            with self.assertRaisesRegex(ValidationError, "restore pristine"):
                apply_selection(root, ["reduce_sprint_stamina"])

        ensure_backup.assert_not_called()

    def test_apply_builds_then_installs_against_exact_source_hash(self):
        root = Path("/game")
        game = self._game(root)
        backup_path = default_backup_path(game.data0)
        status = ApplicationStatus(
            game=game,
            backup_path=backup_path,
            backup=None,
            live_matches_backup=None,
        )
        backup = self._archive(backup_path, BASELINE)
        candidate = CandidateBuild(
            source_sha256=BASELINE,
            candidate_sha256="c" * 64,
            entry_count=3060,
            selected_options=("reduce_sprint_stamina",),
            changed_members=("data/skills/default_levels.xml",),
        )
        installed = self._archive(game.data0, "c" * 64)

        with patch("dirue.application.inspect_game", return_value=status), patch(
            "dirue.application.ensure_pristine_backup", return_value=backup
        ) as ensure_backup, patch(
            "dirue.application.build_candidate", return_value=candidate
        ) as build, patch(
            "dirue.application.install_candidate", return_value=installed
        ) as install:
            result = apply_selection(root, ["reduce_sprint_stamina"])

        ensure_backup.assert_called_once_with(
            game.data0,
            backup_path,
            expected_live_sha256=BASELINE,
        )
        self.assertEqual(build.call_args.args[0], game.data0)
        self.assertEqual(build.call_args.args[2], ("reduce_sprint_stamina",))
        install.assert_called_once_with(
            build.call_args.args[1],
            game.data0,
            backup_path,
            expected_live_sha256=BASELINE,
            expected_candidate_sha256="c" * 64,
        )
        self.assertEqual(result.installed_sha256, "c" * 64)
        self.assertEqual(result.backup_sha256, BASELINE)

    def test_restore_requires_existing_pristine_backup(self):
        root = Path("/game")
        game = self._game(root)
        status = ApplicationStatus(
            game=game,
            backup_path=default_backup_path(game.data0),
            backup=None,
            live_matches_backup=None,
        )

        with patch("dirue.application.inspect_game", return_value=status):
            with self.assertRaisesRegex(ValidationError, "does not exist"):
                restore_pristine(root)

    def test_restore_binds_to_validated_backup_hash(self):
        root = Path("/game")
        game = self._game(root, "c" * 64)
        backup_path = default_backup_path(game.data0)
        backup = self._archive(backup_path, BASELINE)
        status = ApplicationStatus(
            game=game,
            backup_path=backup_path,
            backup=backup,
            live_matches_backup=False,
        )
        restored = self._archive(game.data0, BASELINE)

        with patch("dirue.application.inspect_game", return_value=status), patch(
            "dirue.application.restore_backup", return_value=restored
        ) as restore:
            result = restore_pristine(root)

        restore.assert_called_once_with(
            backup_path,
            game.data0,
            expected_backup_sha256=BASELINE,
        )
        self.assertEqual(result.restored_sha256, BASELINE)
        self.assertEqual(result.backup_sha256, BASELINE)


if __name__ == "__main__":
    unittest.main()
