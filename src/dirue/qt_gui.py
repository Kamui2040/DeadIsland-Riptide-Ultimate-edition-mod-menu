"""PySide6 user interface for the native Linux port."""

from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtCore import Qt
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

from .application import apply_selection, inspect_game, restore_pristine
from .errors import DirueError
from .ui_catalog import CHECKBOX_OPTIONS, CHOICE_GROUPS


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DIRUE Linux")
        self.resize(900, 760)

        self._checkboxes: dict[str, QCheckBox] = {}
        self._combos: dict[str, QComboBox] = {}

        central = QWidget()
        layout = QVBoxLayout(central)

        title = QLabel("Dead Island: Riptide Ultimate Edition — native Linux port")
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(title)

        intro = QLabel(
            "Select the native Linux game folder. Candidate construction and installation "
            "use the validated transactional patch engine."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        folder_row = QHBoxLayout()
        self._root_edit = QLineEdit()
        self._root_edit.setPlaceholderText("Native Dead Island Riptide Definitive Edition folder")
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse)
        validate = QPushButton("Validate")
        validate.clicked.connect(self._refresh_status)
        folder_row.addWidget(self._root_edit, 1)
        folder_row.addWidget(browse)
        folder_row.addWidget(validate)
        layout.addLayout(folder_row)

        self._status = QLabel("No game folder validated.")
        self._status.setWordWrap(True)
        layout.addWidget(self._status)

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
        self._apply_button = QPushButton("Apply selected modifications")
        self._apply_button.clicked.connect(self._apply)
        self._apply_button.setEnabled(False)
        self._restore_button = QPushButton("Restore pristine Data0")
        self._restore_button.clicked.connect(self._restore)
        self._restore_button.setEnabled(False)
        buttons.addWidget(self._apply_button)
        buttons.addWidget(self._restore_button)
        layout.addLayout(buttons)

        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(500)
        self._log.setPlaceholderText("Validation and transaction results appear here.")
        layout.addWidget(self._log)

        footer = QLabel(
            "DIRUE was created by FireEyeEian. This is a GPLv3 native-Linux port. "
            "Game assets are not redistributed."
        )
        footer.setWordWrap(True)
        layout.addWidget(footer)

        self.setCentralWidget(central)

    def _root(self) -> Path | None:
        value = self._root_edit.text().strip()
        return Path(value).expanduser() if value else None

    def _browse(self) -> None:
        selected = QFileDialog.getExistingDirectory(
            self,
            "Select native DIRDE game folder",
            str(Path.home()),
        )
        if selected:
            self._root_edit.setText(selected)
            self._refresh_status()

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

    def _refresh_status(self) -> None:
        root = self._root()
        if root is None:
            self._status.setText("No game folder selected.")
            self._apply_button.setEnabled(False)
            self._restore_button.setEnabled(False)
            return

        try:
            status = inspect_game(root)
        except DirueError as exc:
            self._status.setText(f"Validation failed: {exc}")
            self._apply_button.setEnabled(False)
            self._restore_button.setEnabled(False)
            self._append(f"VALIDATION FAIL: {exc}")
            return

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

        self._status.setText(
            f"Validated native game. Data0: {status.game.archive.entry_count} entries, "
            f"SHA-256 {status.game.archive.sha256}. {backup_state}"
        )
        self._apply_button.setEnabled(can_apply)
        self._restore_button.setEnabled(can_restore)
        self._append("VALIDATION PASS")
        self._append(f"Data0 SHA-256: {status.game.archive.sha256}")
        self._append(backup_state)

    def _apply(self) -> None:
        root = self._root()
        if root is None:
            QMessageBox.warning(self, "DIRUE Linux", "Select and validate a game folder first.")
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
        self._append("APPLY: building validated candidate…")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            result = apply_selection(root, selected)
        except DirueError as exc:
            self._append(f"APPLY FAIL: {exc}")
            QMessageBox.critical(self, "Apply failed", str(exc))
        else:
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
            self._refresh_status()

    def _restore(self) -> None:
        root = self._root()
        if root is None:
            QMessageBox.warning(self, "DIRUE Linux", "Select and validate a game folder first.")
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

        self._restore_button.setEnabled(False)
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            result = restore_pristine(root)
        except DirueError as exc:
            self._append(f"RESTORE FAIL: {exc}")
            QMessageBox.critical(self, "Restore failed", str(exc))
        else:
            self._append("RESTORE PASS")
            self._append(f"Restored SHA-256: {result.restored_sha256}")
            QMessageBox.information(
                self,
                "Restore complete",
                "The pristine backup was restored successfully.",
            )
        finally:
            QApplication.restoreOverrideCursor()
            self._refresh_status()


def run() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
