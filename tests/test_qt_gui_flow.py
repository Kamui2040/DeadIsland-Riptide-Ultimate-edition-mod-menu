import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
QT_GUI = ROOT / "src" / "dirue" / "qt_gui.py"
SOURCE = QT_GUI.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def _method(name: str) -> ast.FunctionDef:
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"method not found: {name}")


def _call_names(method: ast.FunctionDef) -> list[str]:
    names: list[str] = []
    for node in ast.walk(method):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        if isinstance(target, ast.Name):
            names.append(target.id)
        elif isinstance(target, ast.Attribute):
            names.append(target.attr)
    return names


class QtGuiValidationFlowTests(unittest.TestCase):
    def test_browse_only_selects_folder(self):
        calls = _call_names(_method("_browse"))
        self.assertIn("getExistingDirectory", calls)
        self.assertIn("setText", calls)
        self.assertNotIn("inspect_game", calls)
        self.assertNotIn("_validate_selected_root", calls)

    def test_validate_runs_one_explicit_inspection(self):
        calls = _call_names(_method("_validate_selected_root"))
        self.assertEqual(calls.count("inspect_game"), 1)

    def test_path_changes_invalidate_prior_validation(self):
        self.assertIn(
            "self._root_edit.textChanged.connect(self._invalidate_validation)",
            SOURCE,
        )
        calls = _call_names(_method("_invalidate_validation"))
        self.assertGreaterEqual(calls.count("setEnabled"), 2)
        self.assertIn("self._validated_root = None", SOURCE)

    def test_actions_require_current_validated_root(self):
        for name in ("_apply", "_restore"):
            calls = _call_names(_method(name))
            self.assertIn("_validated_root_for_action", calls)

    def test_transactions_do_not_trigger_implicit_ui_validation(self):
        for name in ("_apply", "_restore"):
            calls = _call_names(_method(name))
            self.assertNotIn("_validate_selected_root", calls)
            self.assertNotIn("inspect_game", calls)

    def test_names_match_maintainer_choice(self):
        self.assertIn('APP_SHORT_NAME = "DIRDE UE Linux"', SOURCE)
        self.assertIn(
            'APP_LONG_NAME = "Dead Island: Riptide DE Linux - Ultimate Edition"',
            SOURCE,
        )
        self.assertIn("self.setWindowTitle(APP_SHORT_NAME)", SOURCE)

    def test_user_facing_native_wording_is_removed(self):
        self.assertNotIn("native", SOURCE.lower())
        self.assertNotIn("transactional patch engine", SOURCE)

    def test_validation_status_is_short(self):
        self.assertIn('self._status.setText("Game folder validated.")', SOURCE)
        self.assertIn('self._status.setText("Can\'t validate game folder.")', SOURCE)
        self.assertNotIn("Data0 SHA-256", SOURCE)
        self.assertNotIn("VALIDATION PASS", SOURCE)
        self.assertNotIn("VALIDATION FAIL", SOURCE)

    def test_flatpak_requires_browse_for_portal_access(self):
        calls = _call_names(_method("_running_in_flatpak"))
        self.assertIn("get", calls)
        self.assertIn("is_file", calls)
        self.assertIn("self._root_edit.setReadOnly(True)", SOURCE)
        self.assertIn("Use Browse so Flatpak can access the folder.", SOURCE)

    def test_activity_is_limited_to_three_lines(self):
        self.assertIn("self._log.setMaximumBlockCount(3)", SOURCE)
        self.assertIn("self._log.setFixedHeight(activity_height)", SOURCE)
        self.assertIn("lineSpacing() * 3", SOURCE)
        self.assertIn("ScrollBarAlwaysOff", SOURCE)

    def test_options_get_more_vertical_space(self):
        self.assertIn("self.resize(1080, 900)", SOURCE)
        self.assertIn("layout.addWidget(scroll, 1)", SOURCE)

    def test_ai_firearms_and_gameplay_use_responsive_layout(self):
        self.assertIn("class _ResponsiveGrid", SOURCE)
        self.assertIn('SECTION_ORDER = ("Gameplay", "AI", "Firearms", "Camera", "World")', SOURCE)
        self.assertIn("GAMEPLAY_THEME_ORDER", SOURCE)
        self.assertIn('if section == "Gameplay":', SOURCE)
        self.assertIn('minimum_width = 220 if section == "AI" else 250', SOURCE)

    def test_dropdowns_fit_longest_item_instead_of_stretching(self):
        method = _method("_build_choice_control")
        calls = _call_names(method)
        self.assertIn("setSizeAdjustPolicy", calls)
        self.assertIn("sizeHint", calls)
        self.assertIn("setFixedWidth", calls)
        self.assertIn(
            "QComboBox.SizeAdjustPolicy.AdjustToContents",
            SOURCE,
        )
        self.assertNotIn("layout.addWidget(combo, 1)", SOURCE)

    def test_noclip_warning_is_embedded(self):
        self.assertIn('item.option == "noclip_vehicles"', SOURCE)
        self.assertIn('QLabel("Warning: This can get you stuck.")', SOURCE)
        self.assertIn("checkbox.toggled.connect(warning.setVisible)", SOURCE)

    def test_restore_uses_original_wording(self):
        self.assertIn('QPushButton("Restore original")', SOURCE)
        self.assertIn('"Restore original",', SOURCE)
        self.assertIn("Original game data restored.", SOURCE)
        self.assertNotIn('QPushButton("Restore pristine")', SOURCE)

    def test_about_lists_authors_and_links(self):
        self.assertIn("FireEyeEian — original Ultimate Edition mod", SOURCE)
        self.assertIn("Kamui2040 — Linux port", SOURCE)
        self.assertIn("https://kamui2040.github.io/gaming-mods/", SOURCE)
        self.assertIn("Project page", SOURCE)
        self.assertIn("https://ko-fi.com/k2040", SOURCE)
        self.assertIn("https://www.nexusmods.com/deadislandriptide/mods/3", SOURCE)
        self.assertIn("setOpenExternalLinks(True)", SOURCE)

    def test_packaged_window_icon_uses_shared_app_identity(self):
        self.assertIn('APP_ID = "io.github.Kamui2040.DIRUELinux"', SOURCE)
        calls = _call_names(_method("_application_icon"))
        self.assertIn("fromTheme", calls)
        self.assertIn("is_file", calls)
        self.assertIn("APPDIR", SOURCE)
        self.assertIn("/app/share/icons/hicolor/scalable/apps", SOURCE)


if __name__ == "__main__":
    unittest.main()
