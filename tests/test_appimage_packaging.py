from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_ID = "io.github.Kamui2040.DIRUELinux"
APPIMAGE_DIR = ROOT / "packaging" / "appimage"
COMMON_DIR = ROOT / "packaging" / "common"
BASELINE_IMAGE = (
    "quay.io/pypa/manylinux_2_34_x86_64@"
    "sha256:64decb8ae4b373180c246525a755c0afb2ca136334f0d64b41cf5f229283a7b6"
)


class AppImagePackagingTests(unittest.TestCase):
    def test_required_proof_files_exist(self):
        for relative in (
            "README.md",
            "build.sh",
            "build-baseline.sh",
            "check_appdir.py",
            "entrypoint.py",
        ):
            self.assertTrue((APPIMAGE_DIR / relative).is_file(), relative)
        for relative in (
            f"{APP_ID}.desktop",
            f"{APP_ID}.metainfo.xml",
            f"{APP_ID}.svg",
        ):
            self.assertTrue((COMMON_DIR / relative).is_file(), relative)

    def test_shell_build_scripts_parse(self):
        for relative in ("build.sh", "build-baseline.sh"):
            result = subprocess.run(
                ["bash", "-n", str(APPIMAGE_DIR / relative)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, f"{relative}: {result.stderr}")

    def test_python_helpers_parse(self):
        for relative in ("check_appdir.py", "entrypoint.py"):
            source = (APPIMAGE_DIR / relative).read_text(encoding="utf-8")
            compile(source, relative, "exec")

    def test_build_is_bounded_to_runtime_source(self):
        script = (APPIMAGE_DIR / "build.sh").read_text(encoding="utf-8")
        self.assertIn('--paths "$ROOT/src"', script)
        self.assertIn('COMMON="$ROOT/packaging/common"', script)
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

    def test_external_appimage_tools_are_immutable_and_digest_checked(self):
        script = (APPIMAGE_DIR / "build.sh").read_text(encoding="utf-8")
        self.assertIn("releases/download/1.9.1/appimagetool-x86_64.AppImage", script)
        self.assertNotIn("appimagetool/releases/download/continuous", script)
        self.assertIn("APPIMAGETOOL_SHA256=", script)
        self.assertIn("type2-runtime/releases/download/20251108/runtime-x86_64", script)
        self.assertNotIn("type2-runtime/releases/download/continuous", script)
        self.assertIn("APPIMAGE_RUNTIME_SHA256=", script)
        self.assertIn("verify_sha256", script)
        self.assertIn('--runtime-file "$APPIMAGE_RUNTIME"', script)

    def test_portability_baseline_is_explicit(self):
        script = (APPIMAGE_DIR / "build.sh").read_text(encoding="utf-8")
        self.assertIn('APPIMAGE_GLIBC_BASELINE="2.34"', script)
        self.assertIn("APPIMAGE_TARGET_GLIBC=", script)
        self.assertIn("APPIMAGE_BUILD_GLIBC=", script)

    def test_baseline_builder_pins_verified_manylinux_image(self):
        script = (APPIMAGE_DIR / "build-baseline.sh").read_text(encoding="utf-8")
        self.assertIn(f'BASELINE_IMAGE="{BASELINE_IMAGE}"', script)
        self.assertIn('BASELINE_GLIBC="glibc 2.34"', script)
        self.assertIn('BASELINE_PYTHON="/opt/python/cp311-cp311/bin/python"', script)
        self.assertNotIn("manylinux_2_34_x86_64:latest", script)
        self.assertNotIn("manylinux_2_34_x86_64:202", script)

    def test_baseline_builder_isolated_and_fail_closed(self):
        script = (APPIMAGE_DIR / "build-baseline.sh").read_text(encoding="utf-8")
        self.assertIn("podman run --rm", script)
        self.assertIn("--userns=keep-id", script)
        self.assertIn("--security-opt label=disable", script)
        self.assertIn('--volume "$ROOT:/workspace:ro"', script)
        self.assertIn('actual_glibc="$(getconf GNU_LIBC_VERSION', script)
        self.assertIn('[ "$actual_glibc" = "$expected_glibc" ]', script)
        self.assertIn('PYTHON_BIN="$python_bin" packaging/appimage/build.sh /output', script)
        self.assertIn("SOURCE_DATE_EPOCH=", script)
        self.assertIn("APPIMAGE_BASELINE_BUILD=PASS", script)

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
        self.assertIn("missing shared AppStream metainfo", checker)

    def test_entrypoint_is_gui_only(self):
        entrypoint = (APPIMAGE_DIR / "entrypoint.py").read_text(encoding="utf-8")
        self.assertIn("from dirue.gui import main", entrypoint)
        self.assertNotIn("application", entrypoint)
        self.assertNotIn("Data0", entrypoint)


if __name__ == "__main__":
    unittest.main()
