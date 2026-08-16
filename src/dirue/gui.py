"""Optional PySide6 launcher for the native Linux GUI."""

from __future__ import annotations

import sys


def _configure_palette(app) -> None:
    """Keep disabled text readable without making disabled controls selectable."""
    from PySide6.QtGui import QColor, QPalette

    palette = app.palette()
    active_text = palette.color(
        QPalette.ColorGroup.Active,
        QPalette.ColorRole.Text,
    )
    disabled_text = QColor(active_text)
    disabled_text.setAlphaF(0.72)

    for role in (
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
        QPalette.ColorRole.WindowText,
    ):
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            role,
            disabled_text,
        )

    app.setPalette(palette)


def main() -> int:
    try:
        from PySide6.QtWidgets import QApplication

        from .qt_gui import MainWindow
    except ModuleNotFoundError as exc:
        if exc.name is not None and exc.name.startswith("PySide6"):
            print(
                "DIRUE Linux GUI requires the optional PySide6 dependency; "
                "install the project with the 'gui' extra.",
                file=sys.stderr,
            )
            return 2
        raise

    app = QApplication.instance() or QApplication(sys.argv)
    _configure_palette(app)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
