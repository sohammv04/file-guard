from __future__ import annotations

from PyQt6.QtCore import QDir, Qt
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSplitter,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from ...config import SUPPORTED_HASH_ALGORITHMS
from ..app_controller import AppController
from ..widgets import ScreenHeader, make_card


class SelectionScreen(QWidget):
    def __init__(self, controller: AppController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(
            ScreenHeader("Select Files & Folders", "Browse the filesystem and confirm your monitoring scope.")
        )

        from PyQt6.QtWidgets import QComboBox

        algo_row = QHBoxLayout()
        algo_row.addWidget(QLabel("Hash Algorithm"))
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(SUPPORTED_HASH_ALGORITHMS)
        self.algorithm_combo.setCurrentText(controller.algorithm)
        self.algorithm_combo.currentTextChanged.connect(controller.set_algorithm)
        algo_row.addWidget(self.algorithm_combo)
        algo_row.addStretch()
        layout.addLayout(algo_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        browser_card = make_card("Filesystem")
        browser_layout = browser_card.layout()
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.homePath()))
        self.tree.setAnimated(True)
        self.tree.setSortingEnabled(True)
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)
        browser_layout.addWidget(self.tree)

        selected_card = make_card("Selected Items")
        selected_layout = selected_card.layout()
        self.selected_list = QListWidget()
        selected_layout.addWidget(self.selected_list)

        splitter.addWidget(browser_card)
        splitter.addWidget(selected_card)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, stretch=1)

        buttons = QHBoxLayout()
        self.add_file_button = QPushButton("Add File")
        self.add_folder_button = QPushButton("Add Folder")
        self.add_tree_button = QPushButton("Add From Tree")
        self.remove_button = QPushButton("Remove Selected")
        self.clear_button = QPushButton("Clear All")
        self.confirm_button = QPushButton("Confirm Selection")

        self.add_file_button.clicked.connect(self._add_file_dialog)
        self.add_folder_button.clicked.connect(self._add_folder_dialog)
        self.add_tree_button.clicked.connect(self._add_from_tree)
        self.remove_button.clicked.connect(self._remove_selected)
        self.clear_button.clicked.connect(self._clear_all)
        self.confirm_button.clicked.connect(lambda: self.controller.navigate_requested.emit(0))

        for button in [
            self.add_file_button,
            self.add_folder_button,
            self.add_tree_button,
            self.remove_button,
            self.clear_button,
            self.confirm_button,
        ]:
            buttons.addWidget(button)
        layout.addLayout(buttons)

        self.controller.data_changed.connect(self.refresh)
        self.refresh()

    def refresh(self) -> None:
        self.selected_list.clear()
        for item in self.controller.monitored_items:
            prefix = "File" if item.item_type == "file" else "Folder"
            self.selected_list.addItem(f"{prefix}: {item.path}")
        if self.algorithm_combo.currentText() != self.controller.algorithm:
            self.algorithm_combo.blockSignals(True)
            self.algorithm_combo.setCurrentText(self.controller.algorithm)
            self.algorithm_combo.blockSignals(False)

    def _add_file_dialog(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(self, "Select file to monitor")
        if selected:
            self.controller.add_file(selected)

    def _add_folder_dialog(self) -> None:
        selected = QFileDialog.getExistingDirectory(self, "Select folder to monitor")
        if selected:
            self.controller.add_folder(selected)

    def _add_from_tree(self) -> None:
        index = self.tree.currentIndex()
        if not index.isValid():
            return
        path = self.model.filePath(index)
        if self.model.isDir(index):
            self.controller.add_folder(path)
        else:
            self.controller.add_file(path)

    def _remove_selected(self) -> None:
        row = self.selected_list.currentRow()
        if row >= 0:
            self.controller.remove_item(row)

    def _clear_all(self) -> None:
        self.controller.clear_selection()
