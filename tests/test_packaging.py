from pathlib import Path
import tomllib
import unittest


class PackagingMetadataTests(unittest.TestCase):
    def test_gui_is_optional_and_has_native_entry_point(self):
        root = Path(__file__).resolve().parents[1]
        data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))

        gui_dependencies = data["project"]["optional-dependencies"]["gui"]
        self.assertEqual(gui_dependencies, ["PySide6>=6.7,<7"])
        self.assertEqual(
            data["project"]["gui-scripts"]["dirue-gui"],
            "dirue.gui:main",
        )
        self.assertEqual(
            data["project"]["scripts"]["dirue"],
            "dirue.cli:main",
        )


if __name__ == "__main__":
    unittest.main()
