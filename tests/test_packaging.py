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


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_distribution_checker():
    return _load_module(
        ROOT / "tools" / "check_distribution.py",
        "dirue_check_distribution",
    )


def _load_build_backend():
    return _load_module(
        ROOT / "build_backend.py",
        "dirue_build_backend",
    )


def _add_tar_file(archive: tarfile.TarFile, name: str, data: bytes = b"x") -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    archive.addfile(info, io.BytesIO(data))


def _write_sdist_variant(
    path: Path,
    *,
    names: tuple[str, ...],
    mtime: int,
    uid: int,
) -> None:
    with tarfile.open(path, "w:gz") as archive:
        for name in names:
            data = name.encode("utf-8")
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mtime = mtime
            info.uid = uid
            info.gid = uid + 1
            info.uname = f"user-{uid}"
            info.gname = f"group-{uid}"
            info.mode = 0o664
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

        self.assertEqual(data["build-system"]["requires"], ["setuptools==83.0.0"])
        self.assertEqual(data["build-system"]["build-backend"], "build_backend")
        self.assertEqual(data["build-system"]["backend-path"], ["."])
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
        self.assertIn("include build_backend.py", lines)
        self.assertIn("include tools/check_distribution.py", lines)


class DeterministicSdistBackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = _load_build_backend()

    def test_normalization_makes_metadata_variants_byte_identical(self):
        epoch = 1_700_000_000
        names = (
            "dirue-linux-0.1.0/src/dirue/__init__.py",
            "dirue-linux-0.1.0/pyproject.toml",
            "dirue-linux-0.1.0/build_backend.py",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "first.tar.gz"
            second = Path(temp_dir) / "second.tar.gz"
            _write_sdist_variant(
                first,
                names=names,
                mtime=100,
                uid=1000,
            )
            _write_sdist_variant(
                second,
                names=tuple(reversed(names)),
                mtime=200,
                uid=2000,
            )

            self.backend._normalize_sdist(first, epoch)
            self.backend._normalize_sdist(second, epoch)

            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(
                int.from_bytes(first.read_bytes()[4:8], "little"),
                epoch,
            )

            with tarfile.open(first, "r:gz") as archive:
                members = archive.getmembers()

            self.assertEqual(
                [member.name for member in members],
                sorted(names),
            )
            for member in members:
                self.assertEqual(member.mtime, epoch)
                self.assertEqual(member.uid, 0)
                self.assertEqual(member.gid, 0)
                self.assertEqual(member.uname, "")
                self.assertEqual(member.gname, "")
                self.assertEqual(member.mode, 0o644)

    def test_normalization_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact = Path(temp_dir) / "unsafe.tar.gz"
            with tarfile.open(artifact, "w:gz") as archive:
                link = tarfile.TarInfo("dirue-linux-0.1.0/link")
                link.type = tarfile.SYMTYPE
                link.linkname = "../outside"
                archive.addfile(link)

            with self.assertRaisesRegex(
                RuntimeError,
                "unsupported non-file/non-directory",
            ):
                self.backend._normalize_sdist(artifact, 0)


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
                    "build_backend.py",
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
                    "build_backend.py",
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
