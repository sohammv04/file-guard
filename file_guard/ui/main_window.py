from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from .. import APP_NAME
from .app_controller import AppController
from .sidebar import Sidebar
from .screens.alerts_screen import AlertsScreen
from .screens.auth_screen import AuthScreen
from .screens.dashboard_screen import DashboardScreen
from .screens.logs_screen import LogsScreen
from .screens.reports_screen import ReportsScreen
from .screens.selection_screen import SelectionScreen
from .screens.settings_screen import SettingsScreen
from .theme import DARK_THEME, LIGHT_THEME


class AppShell(QWidget):
    def __init__(self, controller: AppController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("rootWidget")

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.navigation_changed.connect(self._on_navigate)

        content_wrapper = QWidget()
        content_wrapper.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_wrapper)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 12, 20, 12)

        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("screenTitle")
        top_layout.addWidget(self.page_title)
        top_layout.addStretch()

        self.user_label = QLabel()
        self.user_label.setObjectName("userLabel")
        top_layout.addWidget(self.user_label)

        self.theme_button = QPushButton("Light Mode")
        self.theme_button.setObjectName("secondaryButton")
        self.theme_button.clicked.connect(self._toggle_theme)
        top_layout.addWidget(self.theme_button)

        self.logout_button = QPushButton("Logout")
        self.logout_button.setObjectName("secondaryButton")
        self.logout_button.clicked.connect(self._logout)
        top_layout.addWidget(self.logout_button)

        self.stack = QStackedWidget()
        self.screens = [
            DashboardScreen(controller),
            SelectionScreen(controller),
            AlertsScreen(controller),
            LogsScreen(controller),
            ReportsScreen(controller),
            SettingsScreen(controller),
        ]
        for screen in self.screens:
            self.stack.addWidget(screen)

        content_layout.addWidget(top_bar)
        content_layout.addWidget(self.stack, stretch=1)

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(content_wrapper, stretch=1)

        controller.navigate_requested.connect(self._on_navigate)
        controller.data_changed.connect(self._refresh_header)
        controller.theme_changed.connect(self._sync_theme_button)
        self._refresh_header()
        self._sync_theme_button(controller.current_theme)

    def _sync_theme_button(self, theme: str) -> None:
        self.theme_button.setText("Light Mode" if theme == "dark" else "Dark Mode")

    def _on_navigate(self, index: int) -> None:
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)
            self.sidebar.set_active(index, emit=False)
            titles = ["Dashboard", "Select Files", "Alerts", "Logs", "Reports", "Settings"]
            self.page_title.setText(titles[index])

    def _refresh_header(self) -> None:
        self.user_label.setText(f"Logged in as {self.controller.get_user_label()}")

    def _toggle_theme(self) -> None:
        new_theme = "light" if self.controller.current_theme == "dark" else "dark"
        self.controller.current_theme = new_theme
        self.controller.theme_changed.emit(new_theme)

    def _logout(self) -> None:
        window = self.window()
        if hasattr(window, "logout"):
            window.logout()  # type: ignore[attr-defined]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.controller = AppController()
        self.setWindowTitle(APP_NAME)
        self.resize(1360, 860)
        self.setMinimumSize(980, 640)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        self.tray_icon.setToolTip(APP_NAME)
        self.tray_icon.show()

        self.root_stack = QStackedWidget()
        self.setCentralWidget(self.root_stack)

        self.auth_screen = AuthScreen(self.controller)
        self.app_shell = AppShell(self.controller)
        self.root_stack.addWidget(self.auth_screen)
        self.root_stack.addWidget(self.app_shell)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.auth_screen.authenticated.connect(self._enter_app)
        self.controller.changes_detected.connect(self._notify_changes)
        self.controller.theme_changed.connect(lambda theme: self._apply_theme(theme, animated=True))
        self.controller.authenticated_changed.connect(self._on_auth_changed)

        self._apply_theme(self.controller.current_theme, animated=False)
        self.root_stack.setCurrentIndex(0)

    def _enter_app(self) -> None:
        self.root_stack.setCurrentIndex(1)
        self.status_bar.showMessage("Authentication successful.", 4000)

    def logout(self) -> None:
        self.controller.logout()
        self.root_stack.setCurrentIndex(0)
        self.status_bar.showMessage("Logged out.", 3000)

    def _on_auth_changed(self, authenticated: bool) -> None:
        if not authenticated:
            self.root_stack.setCurrentIndex(0)

    def _notify_changes(self, changes: list) -> None:
        for change in changes:
            message = (
                f"{change['change_type'].upper()} | {change['risk_level']} | {change['path']}"
            )
            self.tray_icon.showMessage(APP_NAME, message, QSystemTrayIcon.MessageIcon.Warning, 5000)

    def toggle_theme(self) -> None:
        new_theme = "light" if self.controller.current_theme == "dark" else "dark"
        self.controller.current_theme = new_theme
        self.controller.theme_changed.emit(new_theme)

    def _apply_theme(self, theme: str, animated: bool) -> None:
        app = QApplication.instance()
        if app:
            app.setStyleSheet(DARK_THEME if theme == "dark" else LIGHT_THEME)
        if animated:
            animation = QPropertyAnimation(self, b"windowOpacity")
            animation.setDuration(220)
            animation.setStartValue(0.88)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            animation.start()
            self._animation = animation

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.controller.stop_monitoring()
        super().closeEvent(event)
