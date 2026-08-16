from __future__ import annotations

import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import tomllib
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def _load_distribution_checker():
    path = ROOT / "tools" / "check_distribution.py"
    spec = importlib.util.spec_from_file_location("dirue_check_distribution", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load distribution checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _add_tar_file(archive: tarfile.TarFile, name: str, data: bytes = b"x") -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    archive.addfile(info, io.BytesIO(data))


class PackagingMetadataTests(unittest.TestCase):
    def test_gui_is_optional_and_has_native_entry_point(self):
        data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

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

    def test_distribution_metadata_is_explicit_and_package_data_is_disabled(self):
        data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual(data["project"]["readme"], "README.md")
        self.assertFalse(data["tool"]["setuptools"]["include-package-data"])
        self.assertEqual(data["tool"]["setuptools"]["packages"]["find"]["where"], ["src"])

    def test_manifest_excludes_provenance_sensitive_payloads(self):
        lines = {
            line.strip()
            for line in (ROOT / "MANIFEST.in").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }

        self.assertIn("exclude Data0.pak", lines)
        self.assertIn("exclude aibeh_mod.scr", lines)
        self.assertIn("prune Required_files_and_scripts", lines)
        self.assertIn("prune UI", lines)
        self.assertIn("include tools/check_distribution.py", lines)


class DistributionArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checker = _load_distribution_checker()

    def test_safe_wheel_is_accepted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact = Path(temp_dir) / "dirue_linux-0.1.0-py3-none-any.whl"
            with zipfile.ZipFile(artifact, "w") as archive:
                archive.writestr("dirue/__init__.py", "")
                archive.writestr("dirue/cli.py", "")
                archive.writestr("dirue/gui.py", "")
                archive.writestr("dirue_linux-0.1.0.dist-info/METADATA", "")

            self.assertEqual(self.checker.check_artifact(artifact), "wheel")

    def test_wheel_with_data0_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact = Path(temp_dir) / "dirue_linux-0.1.0-py3-none-any.whl"
            with zipfile.ZipFile(artifact, "w") as archive:
                archive.writestr("dirue/__init__.py", "")
                archive.writestr("dirue/cli.py", "")
                archive.writestr("dirue/gui.py", "")
                archive.writestr("Data0.pak", b"not-game-data")

            with self.assertRaisesRegex(ValueError, "provenance-sensitive file"):
                self.checker.check_artifact(artifact)

    def test_safe_sdist_is_accepted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact = Path(temp_dir) / "dirue-linux-0.1.0.tar.gz"
            root = "dirue-linux-0.1.0"
            with tarfile.open(artifact, "w:gz") as archive:
                for relative in (
                    "pyproject.toml",
                    "README.md",
                    "LICENSE",
                    "DIRUE.ahk",
                    "src/dirue/__init__.py",
                    "tools/check_distribution.py",
                ):
                    _add_tar_file(archive, f"{root}/{relative}")

            self.assertEqual(self.checker.check_artifact(artifact), "sdist")

    def test_sdist_with_preset_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact = Path(temp_dir) / "dirue-linux-0.1.0.tar.gz"
            root = "dirue-linux-0.1.0"
            with tarfile.open(artifact, "w:gz") as archive:
                for relative in (
                    "pyproject.toml",
                    "README.md",
                    "LICENSE",
                    "DIRUE.ahk",
                    "src/dirue/__init__.py",
                    "tools/check_distribution.py",
                ):
                    _add_tar_file(archive, f"{root}/{relative}")
                _add_tar_file(
                    archive,
                    f"{root}/Required_files_and_scripts/example-preset.zip",
                )

            with self.assertRaisesRegex(ValueError, "provenance-sensitive directory"):
                self.checker.check_artifact(artifact)


if __name__ == "__main__":
    unittest.main()
