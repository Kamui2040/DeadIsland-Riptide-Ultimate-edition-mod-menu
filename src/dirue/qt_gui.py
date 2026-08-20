"""PySide6 user interface for the native Linux port."""

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

        title = QLabel("Dead Island: Riptide Ultimate Edition — native Linux port")
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        intro = QLabel(
            "Choose the native Linux game folder, validate it, select the released DIRUE "
            "options you want, then apply them. Changes use the validated transactional "
            "patch engine and retain a pristine backup for restore."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        steps = QLabel("1. Choose folder   2. Validate   3. Select options   4. Apply changes")
        steps.setWordWrap(True)
        steps.setStyleSheet("font-weight: 600;")
        layout.addWidget(steps)

        game_box = QGroupBox("Game installation")
        game_layout = QVBoxLayout(game_box)
        folder_row = QHBoxLayout()
        self._root_edit = QLineEdit()
        self._root_edit.setPlaceholderText(
            "Native Dead Island Riptide Definitive Edition folder"
        )
        self._root_edit.setToolTip(
            "Choose the native Linux Dead Island: Riptide Definitive Edition folder."
        )
        self._root_edit.textChanged.connect(self._invalidate_validation)
        self._browse_button = QPushButton("Browse…")
        self._browse_button.setToolTip("Choose a folder without validating it yet.")
        self._browse_button.clicked.connect(self._browse)
        self._validate_button = QPushButton("Validate")
        self._validate_button.setToolTip(
            "Verify the selected folder and Data0 before enabling actions."
        )
        self._validate_button.clicked.connect(self._validate_selected_root)
        folder_row.addWidget(self._root_edit, 1)
        folder_row.addWidget(self._browse_button)
        folder_row.addWidget(self._validate_button)
        game_layout.addLayout(folder_row)

        self._status = QLabel(
            "Needs validation — choose the native game folder, then select Validate."
        )
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
        self._apply_button.setToolTip(
            "Build, validate, and atomically install the selected modifications."
        )
        self._apply_button.clicked.connect(self._apply)
        self._apply_button.setEnabled(False)
        self._restore_button = QPushButton("Restore pristine")
        self._restore_button.setToolTip(
            "Restore the retained validated pristine Data0 backup."
        )
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
        self._log.setMaximumBlockCount(500)
        self._log.setPlaceholderText("Validation and transaction results appear here.")
        layout.addWidget(self._log)

        footer_row = QHBoxLayout()
        footer = QLabel(
            f"DIRUE Linux {__version__}. Original DIRUE by FireEyeEian. GPLv3 native-Linux "
            "port; game assets are not redistributed."
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
        if self._root() is None:
            self._status.setText(
                "Needs validation — choose the native game folder, then select Validate."
            )
        else:
            self._status.setText(
                "Needs validation — folder selected. Validate it before applying or restoring changes."
            )

    def _browse(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self,
            "Select native DIRDE game folder",
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
            backup_state = "No pristine backup yet; the first apply will create one."
            can_apply = True
            can_restore = False
        elif status.live_matches_backup:
            backup_state = "Live Data0 matches the retained pristine backup."
            can_apply = True
            can_restore = True
        else:
            backup_state = (
                "Live Data0 differs from the retained pristine backup. "
                "Restore pristine before applying a different selection."
            )
            can_apply = False
            can_restore = True

        self._validated_root = root
        self._status.setText(
            f"Ready — native game validated. Data0 has {status.game.archive.entry_count} "
            f"entries. {backup_state}"
        )
        self._apply_button.setEnabled(can_apply)
        self._restore_button.setEnabled(can_restore)
        self._append("VALIDATION PASS")
        self._append(f"Data0 SHA-256: {status.game.archive.sha256}")
        self._append(backup_state)

    def _validate_selected_root(self) -> None:
        root = self._root()
        if root is None:
            self._invalidate_validation()
            return

        self._validated_root = None
        self._apply_button.setEnabled(False)
        self._restore_button.setEnabled(False)
        self._status.setText("Validating — checking the selected native game folder…")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            status = inspect_game(root)
        except DirueError as exc:
            self._status.setText(f"Validation failed — {exc}")
            self._append(f"VALIDATION FAIL: {exc}")
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
                "Validate the currently selected game folder before continuing.",
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
            "Apply modifications",
            "Build a validated candidate, preserve the pristine backup, and atomically "
            "install the selected modifications?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self._apply_button.setEnabled(False)
        self._restore_button.setEnabled(False)
        self._append("APPLY: building validated candidate…")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            result = apply_selection(root, selected)
        except DirueError as exc:
            self._validated_root = None
            self._status.setText(
                "Apply failed — validate the game folder again before retrying."
            )
            self._append(f"APPLY FAIL: {exc}")
            QMessageBox.critical(self, "Apply failed", str(exc))
        else:
            self._validated_root = root
            self._apply_button.setEnabled(False)
            self._restore_button.setEnabled(True)
            self._status.setText(
                "Applied — modifications installed successfully. The pristine backup is "
                "retained; restore it before applying a different selection."
            )
            self._append("APPLY PASS")
            self._append(f"Installed SHA-256: {result.installed_sha256}")
            self._append(f"Pristine backup SHA-256: {result.backup_sha256}")
            self._append("Changed members: " + ", ".join(result.changed_members))
            QMessageBox.information(
                self,
                "Apply complete",
                "The validated candidate was installed successfully. The pristine backup "
                "was retained for restore.",
            )
        finally:
            QApplication.restoreOverrideCursor()

    def _restore(self) -> None:
        root = self._validated_root_for_action()
        if root is None:
            return

        answer = QMessageBox.question(
            self,
            "Restore pristine Data0",
            "Restore the validated retained pristine backup over the live Data0?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self._apply_button.setEnabled(False)
        self._restore_button.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            result = restore_pristine(root)
        except DirueError as exc:
            self._validated_root = None
            self._status.setText(
                "Restore failed — validate the game folder again before retrying."
            )
            self._append(f"RESTORE FAIL: {exc}")
            QMessageBox.critical(self, "Restore failed", str(exc))
        else:
            self._validated_root = root
            self._apply_button.setEnabled(True)
            self._restore_button.setEnabled(True)
            self._status.setText(
                "Ready — pristine Data0 restored successfully. This folder can accept a new selection."
            )
            self._append("RESTORE PASS")
            self._append(f"Restored SHA-256: {result.restored_sha256}")
            QMessageBox.information(
                self,
                "Restore complete",
                "The pristine backup was restored successfully.",
            )
        finally:
            QApplication.restoreOverrideCursor()

    def _show_about(self) -> None:
        QMessageBox.information(
            self,
            "About DIRUE Linux",
            f"DIRUE Linux {__version__}\n\n"
            "Native Linux port of Dead Island: Riptide Ultimate Edition by FireEyeEian.\n"
            "Licensed under GPLv3. Game assets are not redistributed.",
        )


def run() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
