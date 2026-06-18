from __future__ import annotations

_COMMON = """
* {
    font-family: "Segoe UI", "Inter", Arial, sans-serif;
    font-size: 16px;
}
QMainWindow, QWidget#rootWidget, QWidget#contentArea {
    background-color: %(bg)s;
    color: %(text)s;
}
QFrame#card, QFrame#statCard {
    background-color: %(card)s;
    border: 1px solid %(border)s;
    border-radius: 12px;
}
QFrame#alertAdded {
    background-color: %(added_bg)s;
    border: 1px solid %(added_border)s;
    border-radius: 12px;
}
QLabel#screenTitle {
    font-size: 24px;
    font-weight: 700;
    color: %(text)s;
}
QLabel#screenSubtitle, QLabel#statSubtitle {
    color: %(muted)s;
    font-size: 16px;
}
QLabel#cardTitle, QLabel#statTitle {
    font-size: 20px;
    font-weight: 600;
    color: %(muted)s;
}
QLabel#statValue {
    font-size: 24px;
    font-weight: 700;
    color: %(text)s;
}
QLabel#brandLabel {
    font-size: 24px;
    font-weight: 700;
    color: %(accent)s;
}
QLineEdit, QComboBox, QTextEdit, QListWidget, QTreeView, QTableWidget {
    background-color: %(input)s;
    color: %(text)s;
    border: 1px solid %(border)s;
    border-radius: 8px;
    padding: 8px;
    font-size: 18px;
    selection-background-color: %(accent)s;
}
QHeaderView::section {
    background-color: %(sidebar)s;
    color: %(text)s;
    border: none;
    padding: 8px;
    font-weight: 600;
}
QTableWidget {
    gridline-color: %(border)s;
    alternate-background-color: %(card)s;
}
QPushButton {
    background-color: %(accent)s;
    color: %(accent_text)s;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 16px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: %(accent_hover)s;
}
QPushButton:disabled {
    background-color: %(disabled)s;
    color: %(muted)s;
}
QPushButton#secondaryButton {
    background-color: transparent;
    color: %(text)s;
    border: 1px solid %(border)s;
}
QPushButton#secondaryButton:hover {
    background-color: %(card)s;
}
QPushButton#navButton {
    background-color: transparent;
    color: %(muted)s;
    border: none;
    border-radius: 8px;
    padding: 12px 14px;
    text-align: left;
    font-weight: 500;
}
QPushButton#navButton:hover {
    background-color: %(nav_hover)s;
    color: %(text)s;
}
QPushButton#navButton[active="true"] {
    background-color: %(nav_active)s;
    color: %(accent)s;
    font-weight: 700;
}
QPushButton#collapseButton {
    background-color: transparent;
    color: %(muted)s;
    border: 1px solid %(border)s;
    padding: 6px 10px;
}
QFrame#sidebar {
    background-color: %(sidebar)s;
    border-right: 1px solid %(border)s;
}
QFrame#topBar {
    background-color: %(card)s;
    border-bottom: 1px solid %(border)s;
}
QLabel#userLabel {
    color: %(muted)s;
    font-size: 10pt;
}
QLabel#statusPill {
    background-color: %(pill_bg)s;
    color: %(pill_text)s;
    border-radius: 14px;
    padding: 4px 12px;
    font-weight: 600;
    font-size: 9.5pt;
}
QLabel#statusPill[status="active"] {
    background-color: #1b5e20;
    color: #c8e6c9;
}
QLabel#statusPill[status="paused"] {
    background-color: #e65100;
    color: #ffe0b2;
}
QLabel#statusPill[status="stopped"], QLabel#statusPill[status="not_started"] {
    background-color: %(pill_bg)s;
    color: %(pill_text)s;
}
QLabel#riskLow {
    background-color: #1b5e20;
    color: #e8f5e9;
    border-radius: 10px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 9pt;
}
QLabel#riskMedium {
    background-color: #e65100;
    color: #fff3e0;
    border-radius: 10px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 9pt;
}
QLabel#riskHigh {
    background-color: #b71c1c;
    color: #ffebee;
    border-radius: 10px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 9pt;
}
QScrollBar:vertical {
    background: transparent;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: %(border)s;
    border-radius: 5px;
    min-height: 24px;
}
QStatusBar {
    background-color: %(sidebar)s;
    color: %(muted)s;
    border-top: 1px solid %(border)s;
}
"""

_LIGHT = {
    "bg": "#eef1f6",
    "text": "#1a2332",
    "muted": "#5c6b7f",
    "card": "#ffffff",
    "border": "#d5dde8",
    "input": "#ffffff",
    "sidebar": "#f8fafc",
    "accent": "#2563eb",
    "accent_hover": "#1d4ed8",
    "accent_text": "#ffffff",
    "disabled": "#c7d2e0",
    "nav_hover": "#e8edf5",
    "nav_active": "#e0eaff",
    "pill_bg": "#e2e8f0",
    "pill_text": "#475569",
    "added_bg": "#e3f2fd",
    "added_border": "#64b5f6",
}

_DARK = {
    "bg": "#0d1117",
    "text": "#e6edf3",
    "muted": "#8b9cb3",
    "card": "#161b22",
    "border": "#30363d",
    "input": "#0d1117",
    "sidebar": "#010409",
    "accent": "#388bfd",
    "accent_hover": "#58a6ff",
    "accent_text": "#0d1117",
    "disabled": "#30363d",
    "nav_hover": "#21262d",
    "nav_active": "#1c2d41",
    "pill_bg": "#21262d",
    "pill_text": "#8b9cb3",
    "added_bg": "#0d2137",
    "added_border": "#1e88e5",
}


def build_theme(name: str) -> str:
    palette = _DARK if name == "dark" else _LIGHT
    return _COMMON % palette


DARK_THEME = build_theme("dark")
LIGHT_THEME = build_theme("light")
