"""Data0 archive validation, extraction, rebuilding, backup, and replacement."""

from __future__ import annotations

import copy
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import zipfile

from .errors import ValidationError


@dataclass(frozen=True)
class ArchiveInfo:
    path: Path
    size: int
    sha256: str
    entry_count: int


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_member_name(name: str) -> None:
    member = PurePosixPath(name)
    if member.is_absolute() or ".." in member.parts:
        raise ValidationError(f"unsafe archive member path: {name!r}")
    if "\\" in name:
        raise ValidationError(f"unexpected backslash in archive member path: {name!r}")


def validate_archive(path: Path, required_entries: tuple[str, ...] = ()) -> ArchiveInfo:
    path = Path(path)
    if not path.is_file():
        raise ValidationError(f"archive does not exist: {path}")
    if not zipfile.is_zipfile(path):
        raise ValidationError(f"archive is not ZIP-compatible: {path}")

    with zipfile.ZipFile(path, "r") as archive:
        infos = archive.infolist()
        names: set[str] = set()
        duplicates: set[str] = set()
        for info in infos:
            _validate_member_name(info.filename)
            if info.filename in names:
                duplicates.add(info.filename)
            names.add(info.filename)
        if duplicates:
            raise ValidationError(
                "archive contains duplicate member names: " + ", ".join(sorted(duplicates))
            )
        missing = [name for name in required_entries if name not in names]
        if missing:
            raise ValidationError("archive is missing required entries: " + ", ".join(missing))
        bad = archive.testzip()
        if bad is not None:
            raise ValidationError(f"archive CRC validation failed at: {bad}")

    return ArchiveInfo(
        path=path,
        size=path.stat().st_size,
        sha256=sha256_file(path),
        entry_count=len(infos),
    )


def safe_extract(path: Path, destination: Path) -> None:
    """Extract a validated ZIP archive without permitting path traversal."""
    validate_archive(path)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()

    with zipfile.ZipFile(path, "r") as archive:
        for info in archive.infolist():
            _validate_member_name(info.filename)
            target = (destination / PurePosixPath(info.filename)).resolve()
            if target != root and root not in target.parents:
                raise ValidationError(f"archive member escapes extraction root: {info.filename!r}")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info, "r") as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


def rebuild_from_worktree(source_archive: Path, worktree: Path, destination: Path) -> ArchiveInfo:
    """Rebuild an archive from a worktree while preserving source ZIP metadata/order."""
    validate_archive(source_archive)
    worktree = Path(worktree)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    source_names: set[str] = set()
    with zipfile.ZipFile(source_archive, "r") as source, zipfile.ZipFile(
        destination, "w", allowZip64=True
    ) as output:
        for info in source.infolist():
            source_names.add(info.filename)
            _validate_member_name(info.filename)
            candidate = worktree / PurePosixPath(info.filename)
            if info.is_dir():
                if candidate.is_dir():
                    output.writestr(copy.copy(info), b"")
                continue
            if not candidate.is_file():
                continue
            output.writestr(copy.copy(info), candidate.read_bytes())

        added: list[Path] = []
        for item in worktree.rglob("*"):
            if item.is_file():
                relative = item.relative_to(worktree).as_posix()
                if relative not in source_names:
                    added.append(item)
        for item in sorted(added, key=lambda p: p.relative_to(worktree).as_posix()):
            relative = item.relative_to(worktree).as_posix()
            _validate_member_name(relative)
            output.write(item, relative, compress_type=zipfile.ZIP_DEFLATED)

    return validate_archive(destination)


def _fsync_directory(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _atomic_copy(source: Path, destination: Path, mode: int | None = None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as output, source.open("rb") as input_stream:
            shutil.copyfileobj(input_stream, output)
            output.flush()
            os.fsync(output.fileno())
        if mode is not None:
            os.chmod(temp_path, mode)
        os.replace(temp_path, destination)
        _fsync_directory(destination.parent)
    except BaseException:
        temp_path.unlink(missing_ok=True)
        raise


def ensure_pristine_backup(live_archive: Path, backup_path: Path) -> ArchiveInfo:
    """Create a backup once; never overwrite an existing recoverable original."""
    live_info = validate_archive(live_archive)
    backup_path = Path(backup_path)
    if backup_path.exists():
        return validate_archive(backup_path)
    _atomic_copy(Path(live_archive), backup_path, mode=Path(live_archive).stat().st_mode & 0o7777)
    backup_info = validate_archive(backup_path)
    if backup_info.sha256 != live_info.sha256:
        raise ValidationError("pristine backup hash differs from source archive")
    return backup_info


def install_candidate(candidate: Path, live_archive: Path, pristine_backup: Path) -> ArchiveInfo:
    """Validate a candidate and atomically replace the live archive, retaining backup."""
    candidate_info = validate_archive(candidate)
    validate_archive(pristine_backup)
    live_archive = Path(live_archive)
    if not live_archive.is_file():
        raise ValidationError(f"live archive does not exist: {live_archive}")
    mode = live_archive.stat().st_mode & 0o7777
    _atomic_copy(Path(candidate), live_archive, mode=mode)
    installed = validate_archive(live_archive)
    if installed.sha256 != candidate_info.sha256:
        raise ValidationError("installed archive hash differs from validated candidate")
    return installed


def restore_backup(pristine_backup: Path, live_archive: Path) -> ArchiveInfo:
    """Validate and atomically restore the pristine archive."""
    backup_info = validate_archive(pristine_backup)
    live_archive = Path(live_archive)
    mode = (live_archive.stat().st_mode & 0o7777) if live_archive.exists() else 0o644
    _atomic_copy(Path(pristine_backup), live_archive, mode=mode)
    restored = validate_archive(live_archive)
    if restored.sha256 != backup_info.sha256:
        raise ValidationError("restored archive hash differs from pristine backup")
    return restored
