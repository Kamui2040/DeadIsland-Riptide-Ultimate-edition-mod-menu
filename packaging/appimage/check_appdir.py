"""Fail-closed checks for the DIRUE Linux AppImage/AppDir payload."""

from __future__ import annotations

import argparse
from configparser import ConfigParser
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

APP_ID = "io.github.Kamui2040.DIRUELinux"
FORBIDDEN_NAMES = {
    "Data0.pak",
    "DIRUE.ahk",
    "Required_files_and_scripts",
    "DeadIslandRiptideGame",
    "DeadIslandRiptideGame.exe",
}
FORBIDDEN_BASE_LIBRARIES = {"libgcc_s.so.1"}
REQUIRED_TOP_LEVEL = {"AppRun", f"{APP_ID}.desktop", f"{APP_ID}.svg", ".DirIcon", "usr"}


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

    desktop_path = root / f"{APP_ID}.desktop"
    if desktop_path.is_file():
        parser = ConfigParser(interpolation=None)
        parser.read(desktop_path, encoding="utf-8")
        if "Desktop Entry" not in parser:
            errors.append("root desktop entry is malformed")
        else:
            entry = parser["Desktop Entry"]
            if entry.get("Exec") != "dirue-linux":
                errors.append("desktop Exec does not match bundled launcher")
            if entry.get("Icon") != APP_ID:
                errors.append("desktop Icon does not match application identity")

    metainfo_path = root / "usr" / "share" / "metainfo" / f"{APP_ID}.metainfo.xml"
    if not metainfo_path.is_file():
        errors.append("missing shared AppStream metainfo")
    else:
        try:
            component = ET.parse(metainfo_path).getroot()
        except ET.ParseError as exc:
            errors.append(f"invalid AppStream metainfo: {exc}")
        else:
            if component.findtext("id") != APP_ID:
                errors.append("AppStream id does not match application identity")

    for path in root.rglob("*"):
        if path.name in FORBIDDEN_NAMES:
            errors.append(f"forbidden payload entry: {path.relative_to(root)}")

        if path.name in FORBIDDEN_BASE_LIBRARIES:
            errors.append(f"forbidden bundled base library: {path.relative_to(root)}")

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
