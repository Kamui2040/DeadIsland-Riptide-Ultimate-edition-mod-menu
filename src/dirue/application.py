"""GUI-independent application service for safe native Linux patch transactions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tempfile

from .archive import (
    ArchiveInfo,
    ensure_pristine_backup,
    install_candidate,
    restore_backup,
    validate_archive,
)
from .catalog import EXCLUSIVE_PATCH_GROUPS, READY_PATCHES
from .engine import CandidateBuild, build_candidate
from .errors import PatchError, ValidationError
from .game import GameInstallation, validate_game_root


BACKUP_SUFFIX = ".dirue-pristine"


@dataclass(frozen=True)
class ApplicationStatus:
    game: GameInstallation
    backup_path: Path
    backup: ArchiveInfo | None
    live_matches_backup: bool | None


@dataclass(frozen=True)
class ApplyResult:
    source_sha256: str
    candidate_sha256: str
    installed_sha256: str
    backup_sha256: str
    entry_count: int
    selected_options: tuple[str, ...]
    changed_members: tuple[str, ...]


@dataclass(frozen=True)
class RestoreResult:
    restored_sha256: str
    backup_sha256: str
    entry_count: int


def default_backup_path(data0: Path) -> Path:
    data0 = Path(data0)
    return data0.with_name(data0.name + BACKUP_SUFFIX)


def validate_selection(selected_options: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    selected = tuple(selected_options)
    if not selected:
        raise PatchError("no patch options selected")
    if len(selected) != len(set(selected)):
        raise PatchError("duplicate patch option selected")

    unknown = sorted(name for name in selected if name not in READY_PATCHES)
    if unknown:
        raise PatchError("option is not ready for candidate builds: " + ", ".join(unknown))

    selected_set = set(selected)
    for group in EXCLUSIVE_PATCH_GROUPS:
        conflicts = sorted(selected_set & group)
        if len(conflicts) > 1:
            raise PatchError(
                "mutually exclusive patch options selected: " + ", ".join(conflicts)
            )
    return selected


def inspect_game(root: Path) -> ApplicationStatus:
    game = validate_game_root(root)
    backup_path = default_backup_path(game.data0)
    backup: ArchiveInfo | None = None
    live_matches_backup: bool | None = None
    if backup_path.exists():
        backup = validate_archive(backup_path)
        live_matches_backup = backup.sha256 == game.archive.sha256
        if backup.entry_count != game.archive.entry_count:
            raise ValidationError("pristine backup entry count differs from live archive")
    return ApplicationStatus(
        game=game,
        backup_path=backup_path,
        backup=backup,
        live_matches_backup=live_matches_backup,
    )


def apply_selection(
    root: Path,
    selected_options: tuple[str, ...] | list[str],
) -> ApplyResult:
    """Build and install one selection only over the exact validated live source."""
    selected = validate_selection(selected_options)
    status = inspect_game(root)
    game = status.game

    if status.backup is not None and status.live_matches_backup is False:
        raise ValidationError(
            "live Data0 differs from the pristine backup; restore pristine before applying a new selection"
        )

    backup = ensure_pristine_backup(
        game.data0,
        status.backup_path,
        expected_live_sha256=game.archive.sha256,
    )

    with tempfile.TemporaryDirectory(prefix="dirue-candidate-") as temp_dir:
        candidate_path = Path(temp_dir) / "Data0.candidate.pak"
        candidate: CandidateBuild = build_candidate(
            game.data0,
            candidate_path,
            selected,
        )
        if candidate.source_sha256 != game.archive.sha256:
            raise ValidationError("candidate source hash differs from validated live archive")

        installed = install_candidate(
            candidate_path,
            game.data0,
            status.backup_path,
            expected_live_sha256=candidate.source_sha256,
            expected_candidate_sha256=candidate.candidate_sha256,
        )

    return ApplyResult(
        source_sha256=candidate.source_sha256,
        candidate_sha256=candidate.candidate_sha256,
        installed_sha256=installed.sha256,
        backup_sha256=backup.sha256,
        entry_count=installed.entry_count,
        selected_options=candidate.selected_options,
        changed_members=candidate.changed_members,
    )


def restore_pristine(root: Path) -> RestoreResult:
    """Restore the retained pristine backup over a currently valid native installation."""
    status = inspect_game(root)
    if status.backup is None:
        raise ValidationError("pristine backup does not exist")

    restored = restore_backup(
        status.backup_path,
        status.game.data0,
        expected_backup_sha256=status.backup.sha256,
    )
    return RestoreResult(
        restored_sha256=restored.sha256,
        backup_sha256=status.backup.sha256,
        entry_count=restored.entry_count,
    )
