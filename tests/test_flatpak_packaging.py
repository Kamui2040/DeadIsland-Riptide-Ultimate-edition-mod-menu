import base64
from configparser import ConfigParser
import json
from pathlib import Path
import struct
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
APP_ID = "io.github.Kamui2040.DIRUELinux"
APP_NAME = "DIRDE UE Linux"
APP_SUMMARY = "Dead Island: Riptide DE Linux - Ultimate Edition"
PROJECT_PAGE = "https://kamui2040.github.io/gaming-mods/"
FLATPAK_DIR = ROOT / "packaging" / "flatpak"
COMMON_DIR = ROOT / "packaging" / "common"
MANIFEST = FLATPAK_DIR / f"{APP_ID}.json"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _png_dimensions(data: bytes) -> tuple[int, int]:
    if not data.startswith(PNG_SIGNATURE):
        raise AssertionError("not a PNG")
    return struct.unpack(">II", data[16:24])


def _embedded_svg_png() -> bytes:
    root = ET.parse(COMMON_DIR / f"{APP_ID}.svg").getroot()
    image = next((node for node in root if node.tag.endswith("image")), None)
    if image is None:
        raise AssertionError("shared SVG has no embedded image")
    href = next(
        (value for key, value in image.attrib.items() if key.endswith("href")),
        None,
    )
    prefix = "data:image/png;base64,"
    if href is None or not href.startswith(prefix):
        raise AssertionError("shared SVG does not contain an embedded PNG")
    return base64.b64decode(href[len(prefix):], validate=True)


class FlatpakPackagingTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_uses_pyside_base_app(self):
        self.assertEqual(self.manifest["id"], APP_ID)
        self.assertEqual(self.manifest["runtime"], "org.kde.Platform")
        self.assertEqual(self.manifest["runtime-version"], "6.11")
        self.assertEqual(self.manifest["base"], "io.qt.PySide.BaseApp")
        self.assertEqual(self.manifest["base-version"], "6.11")
        self.assertEqual(self.manifest["command"], "dirue-linux")
        self.assertEqual(
            self.manifest["cleanup-commands"],
            ["/app/cleanup-BaseApp.sh"],
        )

    def test_manifest_sources_are_public_safe_and_bounded(self):
        module = self.manifest["modules"][0]
        source_paths = [source["path"] for source in module["sources"]]
        self.assertEqual(
            source_paths,
            [
                "../../src",
                f"../common/{APP_ID}.desktop",
                f"../common/{APP_ID}.metainfo.xml",
                f"../common/{APP_ID}.svg",
                f"../common/{APP_ID}.64.png",
                f"../common/{APP_ID}.128.png",
            ],
        )
        manifest_text = MANIFEST.read_text(encoding="utf-8")
        for forbidden in (
            "Data0.pak",
            "Required_files_and_scripts",
            "DIRUE.ahk",
            "UI/",
        ):
            self.assertNotIn(forbidden, manifest_text)

    def test_manifest_starts_portal_first_without_host_filesystem_access(self):
        finish_args = self.manifest["finish-args"]
        self.assertNotIn("--share=network", finish_args)
        self.assertNotIn("--filesystem=host", finish_args)
        self.assertFalse(
            any(argument.startswith("--filesystem=") for argument in finish_args)
        )
        self.assertIn("--socket=wayland", finish_args)
        self.assertIn("--socket=fallback-x11", finish_args)

    def test_manifest_launches_existing_gui_module(self):
        commands = "\n".join(self.manifest["modules"][0]["build-commands"])
        self.assertIn("python3 -m dirue.gui", commands)
        self.assertIn("/app/bin/dirue-linux", commands)
        self.assertIn(f"/app/share/icons/hicolor/scalable/apps/{APP_ID}.svg", commands)
        self.assertIn(f"/app/share/icons/hicolor/64x64/apps/{APP_ID}.png", commands)
        self.assertIn(f"/app/share/icons/hicolor/128x128/apps/{APP_ID}.png", commands)

    def test_shared_desktop_entry_matches_identity(self):
        parser = ConfigParser(interpolation=None)
        parser.read(COMMON_DIR / f"{APP_ID}.desktop", encoding="utf-8")
        entry = parser["Desktop Entry"]
        self.assertEqual(entry["Type"], "Application")
        self.assertEqual(entry["Name"], APP_NAME)
        self.assertEqual(entry["Exec"], "dirue-linux")
        self.assertEqual(entry["Icon"], APP_ID)
        self.assertEqual(entry["Terminal"], "false")

    def test_shared_metainfo_matches_identity(self):
        root = ET.parse(COMMON_DIR / f"{APP_ID}.metainfo.xml").getroot()
        self.assertEqual(root.findtext("id"), APP_ID)
        self.assertEqual(root.findtext("name"), APP_NAME)
        self.assertEqual(root.findtext("summary"), APP_SUMMARY)
        launchable = root.find("launchable")
        self.assertIsNotNone(launchable)
        self.assertEqual(launchable.text, f"{APP_ID}.desktop")
        self.assertEqual(launchable.attrib["type"], "desktop-id")
        self.assertEqual(root.findtext("project_license"), "GPL-3.0-only")
        self.assertEqual(root.findtext("provides/binary"), "dirue-linux")
        urls = {node.attrib.get("type"): node.text for node in root.findall("url")}
        self.assertEqual(urls["homepage"], PROJECT_PAGE)
        self.assertEqual(urls["donation"], "https://ko-fi.com/k2040")

    def test_shared_icon_is_valid_svg(self):
        root = ET.parse(COMMON_DIR / f"{APP_ID}.svg").getroot()
        self.assertTrue(root.tag.endswith("svg"))
        self.assertEqual(root.attrib.get("viewBox"), "0 0 128 128")
        self.assertEqual(_png_dimensions(_embedded_svg_png()), (128, 128))

    def test_shared_raster_icons_cover_flatpak_bundle_sizes(self):
        raster = {}
        for size in (64, 128):
            data = (COMMON_DIR / f"{APP_ID}.{size}.png").read_bytes()
            self.assertEqual(_png_dimensions(data), (size, size))
            raster[size] = data

        self.assertEqual(raster[128], _embedded_svg_png())


if __name__ == "__main__":
    unittest.main()
