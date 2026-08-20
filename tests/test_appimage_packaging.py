from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APPIMAGE_DIR = ROOT / "packaging" / "appimage"


class AppImagePackagingTests(unittest.TestCase):
    def test_required_proof_files_exist(self):
        for relative in (
            "README.md",
            "build.sh",
            "check_appdir.py",
            "entrypoint.py",
            "dirue-linux.desktop",
            "dirue-linux.svg",
        ):
            self.assertTrue((APPIMAGE_DIR / relative).is_file(), relative)

    def test_build_is_bounded_to_runtime_source(self):
        script = (APPIMAGE_DIR / "build.sh").read_text(encoding="utf-8")
        self.assertIn('--paths "$ROOT/src"', script)
        self.assertNotIn('cp -a "$ROOT/."', script)
        self.assertNotIn("Required_files_and_scripts", script)
        self.assertNotIn("Data0.pak", script)
        self.assertNotIn("DIRUE.ahk", script)

    def test_build_freezes_one_directory_inside_appimage(self):
        script = (APPIMAGE_DIR / "build.sh").read_text(encoding="utf-8")
        self.assertIn("--onedir", script)
        self.assertNotIn("--onefile", script)
        self.assertIn('"PyInstaller==$PYINSTALLER_VERSION"', script)
        self.assertIn('"PySide6==$PYSIDE_VERSION"', script)
        self.assertIn("APPIMAGE_EXTRACT_AND_RUN=1", script)

    def test_build_checks_both_appdir_and_final_artifact(self):
        script = (APPIMAGE_DIR / "build.sh").read_text(encoding="utf-8")
        checker = '"$ROOT/packaging/appimage/check_appdir.py"'
        self.assertGreaterEqual(script.count(checker), 2)
        self.assertIn("--appimage-extract", script)
        self.assertIn("APPIMAGE_SHA256=", script)

    def test_payload_checker_rejects_game_and_inherited_names(self):
        checker = (APPIMAGE_DIR / "check_appdir.py").read_text(encoding="utf-8")
        for forbidden in (
            "Data0.pak",
            "DIRUE.ahk",
            "Required_files_and_scripts",
            "DeadIslandRiptideGame",
        ):
            self.assertIn(forbidden, checker)
        self.assertIn("symlink escapes AppDir", checker)
        self.assertIn("bundled Python runtime was not found", checker)
        self.assertIn("bundled PySide6 runtime was not found", checker)

    def test_desktop_entry_matches_bundled_launcher(self):
        desktop = (APPIMAGE_DIR / "dirue-linux.desktop").read_text(encoding="utf-8")
        self.assertIn("Exec=dirue-linux", desktop)
        self.assertIn("Icon=dirue-linux", desktop)
        self.assertIn("Terminal=false", desktop)

    def test_entrypoint_is_gui_only(self):
        entrypoint = (APPIMAGE_DIR / "entrypoint.py").read_text(encoding="utf-8")
        self.assertIn("from dirue.gui import main", entrypoint)
        self.assertNotIn("application", entrypoint)
        self.assertNotIn("Data0", entrypoint)


if __name__ == "__main__":
    unittest.main()
