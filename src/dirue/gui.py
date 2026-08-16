"""Optional PySide6 launcher for the native Linux GUI."""

from __future__ import annotations

import sys


def main() -> int:
    try:
        from .qt_gui import run
    except ModuleNotFoundError as exc:
        if exc.name is not None and exc.name.startswith("PySide6"):
            print(
                "DIRUE Linux GUI requires the optional PySide6 dependency; "
                "install the project with the 'gui' extra.",
                file=sys.stderr,
            )
            return 2
        raise
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
