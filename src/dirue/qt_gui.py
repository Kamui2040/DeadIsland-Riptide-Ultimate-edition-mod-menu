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
    QFileDialog,
    QFormLayout,
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
from .ui_catalog import CHECKBOX_OPTIONS, CHOICE_GROUPS


APP_ID = "io.github.Kamui2040.DIRUELinux"


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


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DIRUE Linux")
        icon = _application_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)
        self.setMinimumSize(760, 640)
        self.resize(940, 800)

        self._checkboxes: dict[str, QCheckBox] = {}
        self._combos: dict[str, QComboBox] = {}
        self._validated_root: Path | None = None

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSpacing(10)

        title = QLabel("Dead Island: Riptide Ultimate Edition — Linux port")
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        steps = QLabel("1. Choose folder   2. Validate   3. Select options   4. Apply changes")
        steps.setWordWrap(True)
        steps.setStyleSheet("font-weight: 600;")
        layout.addWidget(steps)

        game_box = QGroupBox("Game installation")
        game_layout = QVBoxLayout(game_box)
        folder_row = QHBoxLayout()
        self._root_edit = QLineEdit()
        if _running_in_flatpak():
            self._root_edit.setReadOnly(True)
            self._root_edit.setPlaceholderText("Choose the game folder with Browse…")
            self._root_edit.setToolTip(
                "Flatpak uses Browse to grant access to the selected game folder."
            )
        else:
            self._root_edit.setPlaceholderText(
                "Dead Island Riptide Definitive Edition folder"
            )
            self._root_edit.setToolTip("Choose or type the game folder.")
        self._root_edit.textChanged.connect(self._invalidate_validation)
        self._browse_button = QPushButton("Browse…")
        self._browse_button.setToolTip("Choose a folder without validating it yet.")
        self._browse_button.clicked.connect(self._browse)
        self._validate_button = QPushButton("Validate")
        self._validate_button.setToolTip("Validate the selected game folder.")
        self._validate_button.clicked.connect(self._validate_selected_root)
        folder_row.addWidget(self._root_edit, 1)
        folder_row.addWidget(self._browse_button)
        folder_row.addWidget(self._validate_button)
        game_layout.addLayout(folder_row)

        self._status = QLabel("Choose a game folder.")
        self._status.setWordWrap(True)
        game_layout.addWidget(self._status)
        layout.addWidget(game_box)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)

        sections = sorted(
            {item.section for item in CHECKBOX_OPTIONS}
            | {group.section for group in CHOICE_GROUPS}
        )
        for section in sections:
            box = QGroupBox(section)
            form = QFormLayout(box)

            for item in CHECKBOX_OPTIONS:
                if item.section != section:
                    continue
                checkbox = QCheckBox(item.label)
                self._checkboxes[item.option] = checkbox
                form.addRow(checkbox)

            for group in CHOICE_GROUPS:
                if group.section != section:
                    continue
                combo = QComboBox()
                for choice in group.choices:
                    combo.addItem(choice.label, choice.option)
                    index = combo.count() - 1
                    model_item = combo.model().item(index)
                    if model_item is not None:
                        model_item.setEnabled(choice.enabled)
                    if choice.note:
                        combo.setItemData(
                            index,
                            choice.note,
                            Qt.ItemDataRole.ToolTipRole,
                        )
                self._combos[group.key] = combo
                form.addRow(group.label + ":", combo)

            options_layout.addWidget(box)

        options_layout.addStretch(1)
        scroll.setWidget(options_widget)
        layout.addWidget(scroll, 1)

        buttons = QHBoxLayout()
        self._apply_button = QPushButton("Apply changes")
        self._apply_button.setToolTip("Apply the selected modifications.")
        self._apply_button.clicked.connect(self._apply)
        self._apply_button.setEnabled(False)
        self._restore_button = QPushButton("Restore pristine")
        self._restore_button.setToolTip("Restore the pristine game data backup.")
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
            f"DIRUE Linux {__version__}. Original DIRUE by FireEyeEian. GPLv3 Linux port; "
            "game assets are not redistributed."
        )
        footer.setWordWrap(True)
        footer_row.addWidget(footer, 1)
        about = QPushButton("About")
        about.setToolTip("Show version, attribution, and license information.")
        about.clicked.connect(self._show_about)
        footer_row.addWidget(about)
        layout.addLayout(footer_row)

        self.setCentralWidget(central)

    def _root(self) -> Path | None:
        value = self._root_edit.text().strip()
        return Path(value).expanduser() if value else None

    def _invalidate_validation(self, _text: str = "") -> None:
        self._validated_root = None
        self._apply_button.setEnabled(False)
        self._restore_button.setEnabled(False)
        self._status.setToolTip("")
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
        if can_apply:
            self._status.setText("Game folder validated.")
        else:
            self._status.setText(
                "Game folder validated. Restore pristine before applying changes."
            )
        self._status.setToolTip("")
        self._apply_button.setEnabled(can_apply)
        self._restore_button.setEnabled(can_restore)
        self._append("Game folder validated.")

    def _validate_selected_root(self) -> None:
        root = self._root()
        if root is None:
            self._invalidate_validation()
            return

        self._validated_root = None
        self._apply_button.setEnabled(False)
        self._restore_button.setEnabled(False)
        self._status.setText("Validating game folder…")
        self._status.setToolTip("")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            status = inspect_game(root)
        except DirueError as exc:
            self._status.setText("Can't validate game folder.")
            self._status.setToolTip(str(exc))
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
                "DIRUE Linux",
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
            QMessageBox.warning(self, "DIRUE Linux", "Select at least one modification.")
            return

        answer = QMessageBox.question(
            self,
            "Apply changes",
            "Apply the selected changes? A pristine backup will be kept for Restore.",
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
            self._validated_root = None
            self._status.setText("Apply failed. Validate the game folder again.")
            self._status.setToolTip(str(exc))
            self._append("Apply failed.")
            QMessageBox.critical(self, "Apply failed", "Changes were not applied.")
        else:
            self._validated_root = root
            self._apply_button.setEnabled(False)
            self._restore_button.setEnabled(True)
            self._status.setText(
                "Changes applied. Restore pristine before applying a different selection."
            )
            self._status.setToolTip("")
            self._append("Changes applied.")
            QMessageBox.information(
                self,
                "Apply complete",
                "Changes applied successfully.",
            )
        finally:
            QApplication.restoreOverrideCursor()

    def _restore(self) -> None:
        root = self._validated_root_for_action()
        if root is None:
            return

        answer = QMessageBox.question(
            self,
            "Restore pristine",
            "Restore the pristine backup?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self._apply_button.setEnabled(False)
        self._restore_button.setEnabled(False)
        self._append("Restoring pristine game data…")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            restore_pristine(root)
        except DirueError as exc:
            self._validated_root = None
            self._status.setText("Restore failed. Validate the game folder again.")
            self._status.setToolTip(str(exc))
            self._append("Restore failed.")
            QMessageBox.critical(self, "Restore failed", "The pristine backup was not restored.")
        else:
            self._validated_root = root
            self._apply_button.setEnabled(True)
            self._restore_button.setEnabled(True)
            self._status.setText("Game folder validated.")
            self._status.setToolTip("")
            self._append("Pristine game data restored.")
            QMessageBox.information(
                self,
                "Restore complete",
                "Pristine game data restored successfully.",
            )
        finally:
            QApplication.restoreOverrideCursor()

    def _show_about(self) -> None:
        QMessageBox.information(
            self,
            "About DIRUE Linux",
            f"DIRUE Linux {__version__}\n\n"
            "Linux port of Dead Island: Riptide Ultimate Edition by FireEyeEian.\n"
            "Licensed under GPLv3. Game assets are not redistributed.",
        )


def run() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
