"""PyInstaller entry point for the DIRUE Linux AppImage proof."""

from dirue.gui import main


if __name__ == "__main__":
    raise SystemExit(main())
