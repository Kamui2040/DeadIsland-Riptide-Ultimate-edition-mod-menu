from configparser import ConfigParser
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
APP_ID = "io.github.Kamui2040.DIRUELinux"
APP_NAME = "DIRDE UE Linux"
APP_SUMMARY = "Dead Island: Riptide DE Linux - Ultimate Edition"
FLATPAK_DIR = ROOT / "packaging" / "flatpak"
COMMON_DIR = ROOT / "packaging" / "common"
MANIFEST = FLATPAK_DIR / f"{APP_ID}.json"


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
        self.assertEqual(urls["donation"], "https://ko-fi.com/k2040")

    def test_shared_icon_is_custom_dirde_ue_artwork(self):
        icon = (COMMON_DIR / f"{APP_ID}.svg").read_text(encoding="utf-8")
        self.assertIn('aria-label="DIRDE UE Linux"', icon)
        self.assertIn(">UE</text>", icon)
        self.assertNotIn('aria-label="DIRUE Linux"', icon)


if __name__ == "__main__":
    unittest.main()
