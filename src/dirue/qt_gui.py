"""PySide6 user interface for the Linux port."""

from __future__ import annotations

import os
from pathlib import Path
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from . import __version__
from .application import (
    ApplicationStatus,
    apply_selection,
    inspect_game,
    restore_pristine,
)
from .errors import DirueError
from .ui_catalog import CHECKBOX_OPTIONS, CHOICE_GROUPS, CheckboxOption, ChoiceGroup


APP_ID = "io.github.Kamui2040.DIRUELinux"
APP_SHORT_NAME = "DIRDE UE Linux"
APP_LONG_NAME = "Dead Island: Riptide DE Linux - Ultimate Edition"
PROJECT_URL = "https://kamui2040.github.io/gaming-mods/"
KOFI_URL = "https://ko-fi.com/k2040"
ORIGINAL_MOD_URL = "https://www.nexusmods.com/deadislandriptide/mods/3"
SECTION_ORDER = ("Gameplay", "AI", "Firearms", "Camera", "World")
GAMEPLAY_THEME_ORDER = ("Movement", "Combat", "Gear & loot", "Comfort", "Vehicles")


def _application_icon() -> QIcon:
    icon = QIcon.fromTheme(APP_ID)
    if not icon.isNull():
        return icon

    candidates: list[Path] = []
    appdir = os.environ.get("APPDIR")
    if appdir:
        candidates.append(
            Path(appdir)
            / "usr"
            / "share"
            / "icons"
            / "hicolor"
            / "scalable"
            / "apps"
            / f"{APP_ID}.svg"
        )
    candidates.append(
        Path("/app/share/icons/hicolor/scalable/apps") / f"{APP_ID}.svg"
    )

    for path in candidates:
        if path.is_file():
            return QIcon(str(path))
    return QIcon()


def _running_in_flatpak() -> bool:
    return bool(os.environ.get("FLATPAK_ID")) or Path("/.flatpak-info").is_file()


class _ResponsiveGrid(QWidget):
    """Keep compact groups side by side and wrap them when space gets tight."""

    def __init__(
        self,
        widgets: list[QWidget],
        *,
        minimum_item_width: int,
        max_columns: int | None = None,
    ) -> None:
        super().__init__()
        self._widgets = widgets
        self._minimum_item_width = minimum_item_width
        self._max_columns = max_columns or max(1, len(widgets))
        self._columns = 0
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setHorizontalSpacing(8)
        self._grid.setVerticalSpacing(8)
        self._reflow(10_000)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._reflow(event.size().width())

    def _reflow(self, width: int) -> None:
        if not self._widgets:
            return
        columns = max(1, width // self._minimum_item_width)
        columns = min(columns, self._max_columns, len(self._widgets))
        if columns == self._columns:
            return
        self._columns = columns
        for widget in self._widgets:
            self._grid.removeWidget(widget)
        for index, widget in enumerate(self._widgets):
            self._grid.addWidget(widget, index // columns, index % columns)
        for column in range(self._max_columns):
            self._grid.setColumnStretch(column, 1 if column < columns else 0)


class _AboutDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_SHORT_NAME}")
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        title = QLabel(f"<b>{APP_LONG_NAME}</b><br>{APP_SHORT_NAME} {__version__}")
        title.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(title)

        credits = QLabel(
            "Authors:<br>"
            "• FireEyeEian — original Ultimate Edition mod<br>"
            "• Kamui2040 — Linux port"
        )
        credits.setWordWrap(True)
        layout.addWidget(credits)

        links = QLabel(
            f'<a href="{PROJECT_URL}">Project page</a><br>'
            f'<a href="{KOFI_URL}">Support Kamui2040 on Ko-fi</a><br>'
            f'<a href="{ORIGINAL_MOD_URL}">Original mod on Nexus Mods</a>'
        )
        links.setTextFormat(Qt.TextFormat.RichText)
        links.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        links.setOpenExternalLinks(True)
        layout.addWidget(links)

        license_text = QLabel("GPLv3. Game assets are not included.")
        license_text.setWordWrap(True)
        layout.addWidget(license_text)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_SHORT_NAME)
        icon = _application_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)
        self.setMinimumSize(780, 700)
        self.resize(1080, 900)

        self._checkboxes: dict[str, QCheckBox] = {}
        self._combos: dict[str, QComboBox] = {}
        self._validated_root: Path | None = None
        self._noclip_warning: QLabel | None = None

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 8)
        layout.setSpacing(8)

        title = QLabel(APP_LONG_NAME)
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        steps = QLabel("1. Choose folder   2. Validate   3. Select options   4. Apply changes")
        steps.setWordWrap(True)
        layout.addWidget(steps)

        layout.addWidget(self._build_game_box())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(8)

        for section in SECTION_ORDER:
            section_widget = self._build_option_section(section)
            if section_widget is not None:
                options_layout.addWidget(section_widget)

        options_layout.addStretch(1)
        scroll.setWidget(options_widget)
        layout.addWidget(scroll, 1)

        buttons = QHBoxLayout()
        self._apply_button = QPushButton("Apply changes")
        self._apply_button.setToolTip("Apply the selected changes.")
        self._apply_button.clicked.connect(self._apply)
        self._apply_button.setEnabled(False)
        self._restore_button = QPushButton("Restore original")
        self._restore_button.setToolTip("Restore the original game data from the backup.")
        self._restore_button.clicked.connect(self._restore)
        self._restore_button.setEnabled(False)
        buttons.addWidget(self._apply_button)
        buttons.addStretch(1)
        buttons.addWidget(self._restore_button)
        layout.addLayout(buttons)

        activity = QLabel("Activity")
        activity.setStyleSheet("font-weight: 600;")
        layout.addWidget(activity)

        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(3)
        self._log.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._log.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._log.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._log.setPlaceholderText("Recent activity appears here.")
        activity_height = self._log.fontMetrics().lineSpacing() * 3 + 16
        self._log.setFixedHeight(activity_height)
        layout.addWidget(self._log)

        footer_row = QHBoxLayout()
        footer = QLabel(
            f"{APP_SHORT_NAME} {__version__} · FireEyeEian + Kamui2040 · GPLv3"
        )
        footer.setWordWrap(True)
        footer_row.addWidget(footer, 1)
        about = QPushButton("About")
        about.setToolTip("Credits, links, version, and license.")
        about.clicked.connect(self._show_about)
        footer_row.addWidget(about)
        layout.addLayout(footer_row)

        self.setCentralWidget(central)

    def _build_game_box(self) -> QGroupBox:
        game_box = QGroupBox("Game installation")
        game_layout = QVBoxLayout(game_box)
        game_layout.setSpacing(6)

        folder_row = QHBoxLayout()
        self._root_edit = QLineEdit()
        if _running_in_flatpak():
            self._root_edit.setReadOnly(True)
            self._root_edit.setPlaceholderText("Choose the game folder with Browse…")
            self._root_edit.setToolTip("Use Browse so Flatpak can access the folder.")
        else:
            self._root_edit.setPlaceholderText("Dead Island Riptide Definitive Edition folder")
            self._root_edit.setToolTip("Choose or type the game folder.")
        self._root_edit.textChanged.connect(self._invalidate_validation)

        self._browse_button = QPushButton("Browse…")
        self._browse_button.setToolTip("Choose the game folder.")
        self._browse_button.clicked.connect(self._browse)
        self._validate_button = QPushButton("Validate")
        self._validate_button.setToolTip("Check that this is the right game folder.")
        self._validate_button.clicked.connect(self._validate_selected_root)

        folder_row.addWidget(self._root_edit, 1)
        folder_row.addWidget(self._browse_button)
        folder_row.addWidget(self._validate_button)
        game_layout.addLayout(folder_row)

        self._status = QLabel("Choose a game folder.")
        self._status.setWordWrap(True)
        game_layout.addWidget(self._status)
        return game_box

    def _build_option_section(self, section: str) -> QGroupBox | None:
        checkbox_items = [item for item in CHECKBOX_OPTIONS if item.section == section]
        choice_groups = [group for group in CHOICE_GROUPS if group.section == section]
        if not checkbox_items and not choice_groups:
            return None

        box = QGroupBox(section)
        outer = QVBoxLayout(box)
        outer.setContentsMargins(8, 10, 8, 8)

        if section == "Gameplay":
            theme_boxes = []
            for theme in GAMEPLAY_THEME_ORDER:
                items = [item for item in checkbox_items if item.theme == theme]
                if items:
                    theme_boxes.append(self._build_gameplay_theme(theme, items))
            outer.addWidget(
                _ResponsiveGrid(
                    theme_boxes,
                    minimum_item_width=195,
                    max_columns=len(theme_boxes),
                )
            )
            return box

        controls: list[QWidget] = []
        for item in checkbox_items:
            controls.append(self._build_checkbox_control(item))
        for group in choice_groups:
            controls.append(self._build_choice_control(group))

        minimum_width = 220 if section == "AI" else 250
        outer.addWidget(
            _ResponsiveGrid(
                controls,
                minimum_item_width=minimum_width,
                max_columns=len(controls),
            )
        )
        return box

    def _build_gameplay_theme(
        self,
        theme: str,
        items: list[CheckboxOption],
    ) -> QGroupBox:
        box = QGroupBox(theme)
        layout = QVBoxLayout(box)
        layout.setSpacing(4)
        for item in items:
            checkbox = self._make_checkbox(item)
            layout.addWidget(checkbox)
            if item.option == "noclip_vehicles":
                warning = QLabel("Warning: This can get you stuck.")
                warning.setWordWrap(True)
                warning.setStyleSheet("font-weight: 600;")
                warning.setVisible(False)
                checkbox.toggled.connect(warning.setVisible)
                self._noclip_warning = warning
                layout.addWidget(warning)
        layout.addStretch(1)
        return box

    def _build_checkbox_control(self, item: CheckboxOption) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self._make_checkbox(item))
        layout.addStretch(1)
        return container

    def _make_checkbox(self, item: CheckboxOption) -> QCheckBox:
        checkbox = QCheckBox(item.label)
        checkbox.setToolTip(item.help_text)
        self._checkboxes[item.option] = checkbox
        return checkbox

    def _build_choice_control(self, group: ChoiceGroup) -> QWidget:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(6)

        label = QLabel(group.label + ":")
        label.setToolTip(group.help_text)
        combo = QComboBox()
        combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        combo.setToolTip(group.help_text)
        for choice in group.choices:
            combo.addItem(choice.label, choice.option)
            index = combo.count() - 1
            model_item = combo.model().item(index)
            if model_item is not None:
                model_item.setEnabled(choice.enabled)
            combo.setItemData(index, choice.note, Qt.ItemDataRole.ToolTipRole)
        combo.setFixedWidth(combo.sizeHint().width())
        self._combos[group.key] = combo

        layout.addWidget(label)
        layout.addWidget(combo)
        layout.addStretch(1)
        return container

    def _root(self) -> Path | None:
        value = self._root_edit.text().strip()
        return Path(value).expanduser() if value else None

    def _invalidate_validation(self, _text: str = "") -> None:
        self._validated_root = None
        self._apply_button.setEnabled(False)
        self._restore_button.setEnabled(False)
        if self._root() is None:
            self._status.setText("Choose a game folder.")
        else:
            self._status.setText("Select Validate.")

    def _browse(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self,
            "Select DIRDE game folder",
            str(Path.home()),
        )
        if selected:
            self._root_edit.setText(selected)

    def _selected_options(self) -> tuple[str, ...]:
        selected = [
            option
            for option, checkbox in self._checkboxes.items()
            if checkbox.isChecked()
        ]
        for combo in self._combos.values():
            option = combo.currentData()
            if option is not None:
                selected.append(str(option))
        return tuple(selected)

    def _append(self, text: str) -> None:
        self._log.appendPlainText(text)

    def _render_validated_status(self, root: Path, status: ApplicationStatus) -> None:
        if status.backup is None:
            can_apply = True
            can_restore = False
        elif status.live_matches_backup:
            can_apply = True
            can_restore = True
        else:
            can_apply = False
            can_restore = True

        self._validated_root = root
        self._status.setText("Game folder validated.")
        self._apply_button.setEnabled(can_apply)
        self._restore_button.setEnabled(can_restore)
        self._append("Game folder validated.")
        if not can_apply:
            self._append("Restore original before applying different changes.")

    def _validate_selected_root(self) -> None:
        root = self._root()
        if root is None:
            self._invalidate_validation()
            return

        self._validated_root = None
        self._apply_button.setEnabled(False)
        self._restore_button.setEnabled(False)
        self._status.setText("Validating game folder…")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            status = inspect_game(root)
        except DirueError as exc:
            print(f"Validation failed: {exc}", file=sys.stderr)
            self._status.setText("Can't validate game folder.")
            self._append("Can't validate game folder.")
        else:
            self._render_validated_status(root, status)
        finally:
            QApplication.restoreOverrideCursor()

    def _validated_root_for_action(self) -> Path | None:
        root = self._root()
        if root is None or self._validated_root is None or root != self._validated_root:
            QMessageBox.warning(
                self,
                APP_SHORT_NAME,
                "Validate the selected game folder before continuing.",
            )
            return None
        return root

    def _apply(self) -> None:
        root = self._validated_root_for_action()
        if root is None:
            return

        selected = self._selected_options()
        if not selected:
            QMessageBox.warning(self, APP_SHORT_NAME, "Select at least one change.")
            return

        answer = QMessageBox.question(
            self,
            "Apply changes",
            "Apply the selected changes? A backup of the original game data will be kept for Restore.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self._apply_button.setEnabled(False)
        self._restore_button.setEnabled(False)
        self._append("Applying changes…")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            apply_selection(root, selected)
        except DirueError as exc:
            print(f"Apply failed: {exc}", file=sys.stderr)
            self._validated_root = None
            self._status.setText("Apply failed. Validate the game folder again.")
            self._append("Apply failed.")
            QMessageBox.critical(self, "Apply failed", "Changes were not applied.")
        else:
            self._validated_root = root
            self._apply_button.setEnabled(False)
            self._restore_button.setEnabled(True)
            self._status.setText("Changes applied.")
            self._append("Changes applied.")
            QMessageBox.information(self, "Apply complete", "Changes applied successfully.")
        finally:
            QApplication.restoreOverrideCursor()

    def _restore(self) -> None:
        root = self._validated_root_for_action()
        if root is None:
            return

        answer = QMessageBox.question(
            self,
            "Restore original",
            "Restore the original game data from the backup?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self._apply_button.setEnabled(False)
        self._restore_button.setEnabled(False)
        self._append("Restoring original game data…")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            restore_pristine(root)
        except DirueError as exc:
            print(f"Restore failed: {exc}", file=sys.stderr)
            self._validated_root = None
            self._status.setText("Restore failed. Validate the game folder again.")
            self._append("Restore failed.")
            QMessageBox.critical(self, "Restore failed", "The original game data was not restored.")
        else:
            self._validated_root = root
            self._apply_button.setEnabled(True)
            self._restore_button.setEnabled(True)
            self._status.setText("Game folder validated.")
            self._append("Original game data restored.")
            QMessageBox.information(
                self,
                "Restore complete",
                "Original game data restored successfully.",
            )
        finally:
            QApplication.restoreOverrideCursor()

    def _show_about(self) -> None:
        _AboutDialog(self).exec()


def run() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()