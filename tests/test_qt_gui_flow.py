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

    def test_transactions_do_not_trigger_implicit_revalidation(self):
        for name in ("_apply", "_restore"):
            calls = _call_names(_method(name))
            self.assertNotIn("_validate_selected_root", calls)
            self.assertNotIn("inspect_game", calls)

    def test_stale_forced_spawn_message_is_gone(self):
        self.assertNotIn("unresolved forced-spawn", SOURCE)

    def test_version_and_about_are_visible(self):
        self.assertIn("DIRUE Linux {__version__}", SOURCE)
        self.assertIn("About DIRUE Linux", SOURCE)


if __name__ == "__main__":
    unittest.main()
