"""Setuptools backend wrapper with deterministic source-distribution output."""

from __future__ import annotations

import copy
import gzip
import io
import os
from pathlib import Path, PurePosixPath
import tarfile

from setuptools import build_meta as _orig
from setuptools.build_meta import *  # noqa: F401,F403


_MAX_GZIP_MTIME = (1 << 32) - 1


def _source_date_epoch() -> int:
    raw = os.environ.get("SOURCE_DATE_EPOCH", "0")
    try:
        epoch = int(raw, 10)
    except ValueError as exc:
        raise RuntimeError("SOURCE_DATE_EPOCH must be an integer") from exc
    if not 0 <= epoch <= _MAX_GZIP_MTIME:
        raise RuntimeError("SOURCE_DATE_EPOCH is outside the gzip timestamp range")
    return epoch


def _safe_member_name(name: str) -> None:
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        not name
        or name.startswith("/")
        or "\\" in name
        or ".." in path.parts
    ):
        raise RuntimeError(f"unsafe sdist member path: {name!r}")


def _normalize_sdist(path: Path, epoch: int) -> None:
    """Rewrite a setuptools tar.gz sdist with deterministic archive metadata."""

    path = Path(path)
    temporary = path.with_name(path.name + ".normalized")

    try:
        with tarfile.open(path, "r:gz") as source:
            members = source.getmembers()
            seen: set[str] = set()

            for member in members:
                _safe_member_name(member.name)
                if member.name in seen:
                    raise RuntimeError(
                        f"duplicate sdist member path: {member.name!r}"
                    )
                seen.add(member.name)
                if not (member.isfile() or member.isdir()):
                    raise RuntimeError(
                        "unsupported non-file/non-directory sdist member: "
                        f"{member.name!r}"
                    )

            with temporary.open("wb") as raw_output:
                with gzip.GzipFile(
                    filename="",
                    mode="wb",
                    fileobj=raw_output,
                    compresslevel=9,
                    mtime=epoch,
                ) as compressed_output:
                    with tarfile.open(
                        fileobj=compressed_output,
                        mode="w",
                        format=tarfile.PAX_FORMAT,
                    ) as target:
                        for member in sorted(
                            members,
                            key=lambda item: item.name,
                        ):
                            normalized = copy.copy(member)
                            normalized.uid = 0
                            normalized.gid = 0
                            normalized.uname = ""
                            normalized.gname = ""
                            normalized.mtime = epoch
                            normalized.pax_headers = {}
                            normalized.devmajor = 0
                            normalized.devminor = 0

                            if normalized.isdir():
                                normalized.mode = 0o755
                                target.addfile(normalized)
                                continue

                            normalized.mode = (
                                0o755 if member.mode & 0o111 else 0o644
                            )
                            payload = source.extractfile(member)
                            if payload is None:
                                raise RuntimeError(
                                    f"cannot read sdist member: {member.name!r}"
                                )
                            data = payload.read()
                            if len(data) != member.size:
                                raise RuntimeError(
                                    f"sdist member size changed: {member.name!r}"
                                )
                            target.addfile(normalized, io.BytesIO(data))

        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def build_sdist(
    sdist_directory: str,
    config_settings: dict[str, object] | None = None,
) -> str:
    """Build with setuptools, then normalize the resulting tar.gz."""

    filename = _orig.build_sdist(sdist_directory, config_settings)
    if not filename.endswith(".tar.gz"):
        raise RuntimeError(f"unexpected sdist format: {filename}")

    artifact = Path(sdist_directory) / filename
    if not artifact.is_file():
        raise RuntimeError(f"setuptools did not produce expected sdist: {filename}")

    _normalize_sdist(artifact, _source_date_epoch())
    return filename
