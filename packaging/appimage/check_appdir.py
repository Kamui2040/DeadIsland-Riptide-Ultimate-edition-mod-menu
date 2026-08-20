"""Fail-closed checks for the DIRUE Linux AppImage/AppDir payload."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

FORBIDDEN_NAMES = {
    "Data0.pak",
    "DIRUE.ahk",
    "Required_files_and_scripts",
    "DeadIslandRiptideGame",
    "DeadIslandRiptideGame.exe",
}

REQUIRED_TOP_LEVEL = {"AppRun", "dirue-linux.desktop", "dirue-linux.svg", "usr"}


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def validate_appdir(appdir: Path) -> list[str]:
    errors: list[str] = []
    root = appdir.resolve()

    if not root.is_dir():
        return [f"AppDir does not exist: {appdir}"]

    present = {item.name for item in root.iterdir()}
    missing = sorted(REQUIRED_TOP_LEVEL - present)
    if missing:
        errors.append("missing required top-level entries: " + ", ".join(missing))

    launcher = root / "usr" / "lib" / "dirue-linux" / "dirue-linux"
    if not launcher.is_file():
        errors.append("missing bundled DIRUE launcher")

    python_libs = list((root / "usr" / "lib" / "dirue-linux").rglob("libpython*.so*"))
    if not python_libs:
        errors.append("bundled Python runtime was not found")

    pyside_evidence = list((root / "usr" / "lib" / "dirue-linux").rglob("PySide6"))
    if not pyside_evidence:
        errors.append("bundled PySide6 runtime was not found")

    for path in root.rglob("*"):
        if path.name in FORBIDDEN_NAMES:
            errors.append(f"forbidden payload entry: {path.relative_to(root)}")

        if path.is_symlink():
            try:
                target = path.resolve(strict=False)
            except OSError as exc:
                errors.append(f"unresolvable symlink {path.relative_to(root)}: {exc}")
                continue
            if not _is_within(target, root):
                errors.append(f"symlink escapes AppDir: {path.relative_to(root)} -> {target}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("appdir", type=Path)
    args = parser.parse_args(argv)

    errors = validate_appdir(args.appdir)
    if errors:
        for error in errors:
            print(f"APPDIR_CHECK=FAIL: {error}", file=sys.stderr)
        return 1

    print("APPDIR_CHECK=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
