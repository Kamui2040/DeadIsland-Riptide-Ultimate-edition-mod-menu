#!/usr/bin/env python3
"""Validate Linux distribution artifacts without extracting them."""

from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import tarfile
import zipfile


FORBIDDEN_COMPONENTS = frozenset({"Required_files_and_scripts", "UI"})
FORBIDDEN_BASENAMES = frozenset({"Data0.pak", "aibeh_mod.scr"})
FORBIDDEN_SUFFIXES = (".pak", ".zip", ".exe", ".wav", ".xui", ".scr")

WHEEL_REQUIRED_SUFFIXES = (
    "dirue/__init__.py",
    "dirue/cli.py",
    "dirue/gui.py",
)
SDIST_REQUIRED_SUFFIXES = (
    "pyproject.toml",
    "build_backend.py",
    "README.md",
    "LICENSE",
    "DIRUE.ahk",
    "src/dirue/__init__.py",
    "tools/check_distribution.py",
)


def _safe_name(name: str) -> PurePosixPath:
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    if not normalized or normalized.startswith("/") or ".." in path.parts:
        raise ValueError(f"unsafe archive path: {name!r}")
    return path


def _validate_names(names: list[str], *, artifact_kind: str) -> None:
    paths = [_safe_name(name) for name in names if name and not name.endswith("/")]
    if not paths:
        raise ValueError("artifact contains no files")

    for path in paths:
        if FORBIDDEN_COMPONENTS.intersection(path.parts):
            raise ValueError(f"provenance-sensitive directory packaged: {path}")
        if path.name in FORBIDDEN_BASENAMES:
            raise ValueError(f"provenance-sensitive file packaged: {path}")
        if path.name.lower().endswith(FORBIDDEN_SUFFIXES):
            raise ValueError(f"forbidden payload type packaged: {path}")

    required = (
        WHEEL_REQUIRED_SUFFIXES if artifact_kind == "wheel" else SDIST_REQUIRED_SUFFIXES
    )
    rendered = tuple(path.as_posix() for path in paths)
    missing = [
        suffix
        for suffix in required
        if not any(name == suffix or name.endswith("/" + suffix) for name in rendered)
    ]
    if missing:
        raise ValueError(
            f"{artifact_kind} missing required files: " + ", ".join(sorted(missing))
        )


def check_artifact(path: Path) -> str:
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"artifact does not exist: {path}")

    if path.suffix == ".whl":
        with zipfile.ZipFile(path, "r") as archive:
            _validate_names(archive.namelist(), artifact_kind="wheel")
        return "wheel"

    if path.name.endswith((".tar.gz", ".tgz", ".tar")):
        with tarfile.open(path, "r:*") as archive:
            _validate_names(
                [member.name for member in archive.getmembers() if member.isfile()],
                artifact_kind="sdist",
            )
        return "sdist"

    raise ValueError(f"unsupported artifact type: {path.name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check DIRUE Linux wheel/sdist contents for packaging safety."
    )
    parser.add_argument("artifacts", nargs="+", type=Path)
    args = parser.parse_args(argv)

    for artifact in args.artifacts:
        kind = check_artifact(artifact)
        print(f"PASS: {kind}: {artifact.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
