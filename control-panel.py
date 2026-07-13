#!/usr/bin/env python3
"""
control-panel.py — PyQt6 GUI control center for the excalibur-wmi kernel driver.

Requires:
    pip install PyQt6

Run:
    sudo python3 control-panel.py
"""

import sys
import os
import glob
from pathlib import Path
from dataclasses import dataclass, field
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QFrame, QTabWidget, QScrollArea,
    QGridLayout, QSizePolicy, QSystemTrayIcon, QMenu, QStackedWidget
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QSettings, QRectF
from PyQt6.QtGui import QFont, QColor, QPalette, QBrush, QPixmap, QImage, QIcon, QAction, QPainter, QPen
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

# ─────────────────────────────────────────────────────────────────────────────
# Sysfs helpers (Ported from original)
# ─────────────────────────────────────────────────────────────────────────────

LED_BASE = "/sys/class/leds"
HWMON_BASE = "/sys/class/hwmon"
ZONE_NAMES = ("left", "middle", "right", "corners")

POWER_PLANS = {
    1: ("High Performance", "⚡", "Maximum cooling and peak processor speeds.", "#00f0ff"),
    2: ("Gaming", "🎮", "Optimized cooling for GPU-heavy gaming loads.", "#ff0055"),
    3: ("Office", "💼", "Quiet cooling curves for productivity and general tasks.", "#00ff66"),
    4: ("Battery Boost", "🔋", "Minimal cooling and power draw for maximum efficiency.", "#9d00ff"),
}

COLOR_PRESETS = [
    ("White", "FFFFFF"),
    ("Red", "FF0000"),
    ("Orange", "FF8000"),
    ("Yellow", "FFFF00"),
    ("Green", "00FF00"),
    ("Cyan", "00FFFF"),
    ("Blue", "0000FF"),
    ("Magenta", "FF00FF"),
    ("Purple", "800080"),
    ("Pink", "FF69B4"),
    ("Off", "000000"),
]

def _read(path: str) -> str | None:
    try:
        return Path(path).read_text().strip()
    except (OSError, PermissionError):
        return None

def _write(path: str, value: str) -> tuple[bool, str]:
    try:
        Path(path).write_text(value)
        return True, ""
    except PermissionError:
        return False, f"Permission denied: {path}\nTry running with sudo."
    except OSError as exc:
        return False, str(exc)

def find_hwmon_path() -> str | None:
    for name_path in glob.glob(f"{HWMON_BASE}/hwmon*/name"):
        val = _read(name_path)
        if val == "excalibur_wmi":
            return str(Path(name_path).parent)
    return None

def led_path(zone: str, attr: str) -> str:
    return f"{LED_BASE}/excalibur::kbd_backlight-{zone}/{attr}"

def get_available_modes(zone: str = "left") -> list[str]:
    raw = _read(led_path(zone, "available_modes"))
    if raw:
        return raw.split()
    return ["off", "static", "blink", "fade", "heartbeat", "wave", "random", "rainbow"]

def get_user_home() -> str:
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        try:
            import pwd
            return pwd.getpwnam(sudo_user).pw_dir
        except Exception:
            return os.path.expanduser(f"~{sudo_user}")
    return os.path.expanduser("~")

def get_icon() -> QIcon:
    local_logo = Path(__file__).parent / "logo.png"
    if local_logo.exists():
        return QIcon(str(local_logo))
    installed_logo = Path("/opt/excalibur-panel/logo.png")
    if installed_logo.exists():
        return QIcon(str(installed_logo))
    icon = QIcon.fromTheme("excalibur-panel")
    if not icon.isNull():
        return icon
    icon = QIcon.fromTheme("input-keyboard")
    if not icon.isNull():
        return icon
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor("cyan"))
    return QIcon(pixmap)

class SingleInstanceHelper:
    def __init__(self, app_name):
        self.app_name = app_name
        self.server = None

    def try_raise_existing(self, args):
        socket = QLocalSocket()
        socket.connectToServer(self.app_name)
        if socket.waitForConnected(500):
            message = "show"
            if "--minimized" in args or "-m" in args:
                message = "minimized"
            socket.write(message.encode('utf-8'))
            socket.waitForBytesWritten(500)
            socket.disconnectFromServer()
            return True
        return False

    def start_server(self, window):
        QLocalServer.removeServer(self.app_name)
        self.server = QLocalServer()
        self.server.newConnection.connect(lambda: self.on_new_connection(window))
        self.server.listen(self.app_name)

    def on_new_connection(self, window):
        socket = self.server.nextPendingConnection()
        if socket:
            if socket.waitForReadyRead(500):
                message = socket.readAll().data().decode('utf-8')
                if message == "show":
                    window.show_and_activate()
            socket.disconnectFromServer()

# ─────────────────────────────────────────────────────────────────────────────
# UI Constants & Styles
# ─────────────────────────────────────────────────────────────────────────────

ASCII_LOGO = r"""
▀█▀ █▀▀ █▄▀ █▄░█ █▀█ ▄▀█ █▄░█ █▄▀ ▄▀█
░█░ ██▄ █░█ █░▀█ █▄█ █▀█ █░▀█ █░█ █▀█
"""

STYLESHEET = """
/* Main window background */
QMainWindow {
    background-color: #0c0e12;
}

/* Sidebar styling */
QFrame#Sidebar {
    background-color: #080a0f;
    border-right: 1px solid #1c212a;
}

/* Content Area */
QWidget#ContentArea {
    background-color: #05070a;
}

/* Common panels */
QFrame.panel {
    border: 1px solid #1c212a;
    border-radius: 14px;
    background-color: #0f131a;
}
QFrame.panel:hover {
    border-color: #2b3342;
}

/* General labels */
QLabel {
    color: #c9d1d9;
    font-family: "Segoe UI", "Inter", -apple-system, sans-serif;
}
QLabel.title {
    font-size: 22px;
    font-weight: bold;
    color: #ffffff;
}
QLabel.section-title {
    font-size: 11px;
    font-weight: 800;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}
QLabel.muted {
    color: #6e7681;
    font-size: 12px;
}
QLabel[objectName="form-label"] {
    font-size: 11px;
    font-weight: bold;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Modern buttons */
QPushButton {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #21262d;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: bold;
    font-family: "Segoe UI", "Inter", sans-serif;
}
QPushButton:hover {
    background-color: #21262d;
    border-color: #30363d;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #0d1117;
}

/* Sidebar Button Styling */
QPushButton.sidebar-btn {
    background-color: transparent;
    color: #8b949e;
    border: none;
    border-left: 4px solid transparent;
    padding: 12px 20px;
    text-align: left;
    font-size: 13px;
    font-weight: bold;
    border-radius: 0px;
}
QPushButton.sidebar-btn:hover {
    color: #ffffff;
    background-color: #0f131a;
}
QPushButton.sidebar-btn:checked {
    color: #00f0ff;
    background-color: #161b22;
    border-left: 4px solid #00f0ff;
}

/* Highlighted Action Buttons */
QPushButton.active-btn {
    background-color: rgba(0, 240, 255, 0.1);
    color: #00f0ff;
    border: 1px solid rgba(0, 240, 255, 0.4);
}
QPushButton.active-btn:hover {
    background-color: rgba(0, 240, 255, 0.2);
    border-color: #00f0ff;
}

QPushButton.apply-btn {
    background-color: #00f0ff;
    color: #05070a;
    border: none;
    font-size: 14px;
    padding: 12px 24px;
    border-radius: 8px;
}
QPushButton.apply-btn:hover {
    background-color: #80f5ff;
}
QPushButton.apply-btn:pressed {
    background-color: #00b0cc;
}

/* Combobox */
QComboBox {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 8px 12px;
    color: #c9d1d9;
    min-width: 140px;
}
QComboBox:hover {
    border-color: #30363d;
}
QComboBox:on {
    border-color: #00f0ff;
}
QComboBox QAbstractItemView {
    background-color: #0f131a;
    border: 1px solid #21262d;
    selection-background-color: #161b22;
    selection-color: #00f0ff;
    color: #c9d1d9;
    outline: none;
}

/* Scroll Area */
QScrollArea {
    border: none;
    background: transparent;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}

/* Custom Scrollbar */
QScrollBar:vertical {
    border: none;
    background: #080a0f;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #21262d;
    min-height: 25px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #00f0ff;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Custom Widgets
# ─────────────────────────────────────────────────────────────────────────────

class FanGauge(QWidget):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.label = label
        self.rpm = 0
        self.max_rpm = 6000
        self.setMinimumSize(180, 180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def update_rpm(self, rpm):
        self.rpm = rpm
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        size = min(width, height) - 20
        x = (width - size) / 2
        y = (height - size) / 2
        
        rect = QRectF(x, y, size, size)
        
        # 1. Draw outer track arc (270 degrees)
        track_pen = QPen(QColor(30, 35, 45, 120), 10, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 225 * 16, -270 * 16)
        
        # Determine gauge color based on RPM
        if self.rpm == 0:
            color = QColor(80, 85, 95)
        elif self.rpm < 2000:
            color = QColor(0, 240, 102) # Neon Green
        elif self.rpm < 4000:
            color = QColor(0, 240, 255) # Cyan
        elif self.rpm < 5000:
            color = QColor(255, 170, 0) # Orange
        else:
            color = QColor(255, 0, 85) # Neon Red
            
        # Draw active arc
        percent = min(self.rpm, self.max_rpm) / self.max_rpm
        span_angle = -int(270 * percent * 16)
        
        if percent > 0:
            # Draw glow
            glow_pen = QPen(QColor(color.red(), color.green(), color.blue(), 40), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(glow_pen)
            painter.drawArc(rect, 225 * 16, span_angle)
            
            # Draw main arc
            active_pen = QPen(color, 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(active_pen)
            painter.drawArc(rect, 225 * 16, span_angle)
        
        # Draw text
        painter.setPen(QColor(255, 255, 255))
        font_val = QFont("sans-serif", 16, QFont.Weight.Bold)
        painter.setFont(font_val)
        rpm_text = f"{self.rpm:,}"
        rpm_rect = QRectF(x, y + size/2 - 25, size, 30)
        painter.drawText(rpm_rect, Qt.AlignmentFlag.AlignCenter, rpm_text)
        
        painter.setPen(color)
        font_lbl = QFont("sans-serif", 8, QFont.Weight.Bold)
        painter.setFont(font_lbl)
        lbl_rect = QRectF(x, y + size/2 + 5, size, 15)
        painter.drawText(lbl_rect, Qt.AlignmentFlag.AlignCenter, "RPM")
        
        painter.setPen(QColor(139, 148, 158))
        font_outer = QFont("sans-serif", 10, QFont.Weight.Bold)
        painter.setFont(font_outer)
        outer_rect = QRectF(x - 20, y + size - 10, size + 40, 20)
        painter.drawText(outer_rect, Qt.AlignmentFlag.AlignCenter, self.label)

class ColorSwatch(QPushButton):
    selected = pyqtSignal(str, str)
    
    def __init__(self, name, hex_color, parent=None):
        super().__init__(parent)
        self._name = name
        self._hex = hex_color
        self.setFixedSize(36, 36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(name)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #{hex_color};
                border: 2px solid #21262d;
                border-radius: 18px;
            }}
            QPushButton:hover {{
                border: 2px solid #00f0ff;
            }}
        """)
        self.clicked.connect(lambda: self.selected.emit(self._name, self._hex))

    def set_selected(self, is_selected):
        if is_selected:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #{self._hex};
                    border: 3px solid #ffffff;
                    border-radius: 18px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #{self._hex};
                    border: 2px solid #21262d;
                    border-radius: 18px;
                }}
                QPushButton:hover {{
                    border: 2px solid #00f0ff;
                }}
            """)

class PowerPlanCard(QFrame):
    clicked = pyqtSignal(int)
    
    def __init__(self, plan_id, name, description, icon, color, parent=None):
        super().__init__(parent)
        self.plan_id = plan_id
        self.color = color
        self.setObjectName("PowerPlanCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.is_active = False
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet(f"font-size: 22px; color: {color};")
        layout.addWidget(self.icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        self.title_label = QLabel(name)
        self.title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff;")
        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("font-size: 10px; color: #8b949e;")
        self.desc_label.setWordWrap(True)
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.desc_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        self.update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.plan_id)

    def set_active(self, active):
        self.is_active = active
        self.update_style()

    def update_style(self):
        if self.is_active:
            self.setStyleSheet(f"""
                QFrame#PowerPlanCard {{
                    background-color: rgba({QColor(self.color).red()}, {QColor(self.color).green()}, {QColor(self.color).blue()}, 0.08);
                    border: 2px solid {self.color};
                    border-radius: 8px;
                }}
            """)
        else:
            self.setStyleSheet("""
                QFrame#PowerPlanCard {
                    background-color: #161b22;
                    border: 1px solid #21262d;
                    border-radius: 8px;
                }
                QFrame#PowerPlanCard:hover {
                    border: 1px solid #00f0ff;
                    background-color: #1c212a;
                }
            """)

class VirtualKeyboard(QWidget):
    zone_selected = pyqtSignal(str) # Emits zone name ("left", "middle", "right", "corners")
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(420, 160)
        self.active_zone = "all"
        self.zone_colors = {
            "left": QColor("#ffffff"),
            "middle": QColor("#ffffff"),
            "right": QColor("#ffffff"),
            "corners": QColor("#ffffff")
        }
        
    def set_zone_color(self, zone, color_hex):
        color = QColor(f"#{color_hex}")
        if zone == "all":
            for z in self.zone_colors:
                self.zone_colors[z] = color
        else:
            self.zone_colors[zone] = color
        self.update()
        
    def set_active_zone(self, zone):
        self.active_zone = zone.lower()
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background keyboard shell
        shell_rect = QRectF(15, 15, 390, 130)
        painter.setPen(QPen(QColor("#30363d"), 2))
        painter.setBrush(QBrush(QColor("#0d1117")))
        painter.drawRoundedRect(shell_rect, 10, 10)
        
        # Left, Middle, Right zone boundary rects for drawing keys
        zones = {
            "left": QRectF(25, 25, 110, 110),
            "middle": QRectF(145, 25, 130, 110),
            "right": QRectF(285, 25, 110, 110)
        }
        
        # Draw keys inside Left, Middle, Right zones
        for zone_name, rect in zones.items():
            color = self.zone_colors[zone_name]
            
            # If this zone is currently selected or we are in "all", highlight it
            is_selected = (self.active_zone == zone_name or self.active_zone == "all")
            
            bg_color = QColor(color.red(), color.green(), color.blue(), 255 if is_selected else 60)
            glow_color = QColor(color.red(), color.green(), color.blue(), 100 if is_selected else 20)
            
            # Draw glow underlay if active
            if is_selected:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(glow_color))
                painter.drawRoundedRect(rect.adjusted(-3, -3, 3, 3), 6, 6)
                
            # Draw individual key caps inside this zone
            rows = 5
            cols = 6 if zone_name != "middle" else 7
            key_w = (rect.width() - (cols - 1) * 4) / cols
            key_h = (rect.height() - (rows - 1) * 4) / rows
            
            painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 180 if is_selected else 60), 1))
            
            for r in range(rows):
                for c in range(cols):
                    # Slight layout offset to mimic keyboard staggered rows
                    offset_x = (r * 2) if zone_name == "left" else 0
                    k_x = rect.x() + c * (key_w + 4) + offset_x
                    k_y = rect.y() + r * (key_h + 4)
                    
                    if k_x + key_w > rect.x() + rect.width():
                        continue
                        
                    # Key cap base
                    key_rect = QRectF(k_x, k_y, key_w, key_h)
                    painter.setBrush(QBrush(QColor("#161b22")))
                    painter.drawRoundedRect(key_rect, 2, 2)
                    
                    # Key cap legend / center glow
                    painter.setBrush(QBrush(bg_color))
                    painter.drawRoundedRect(key_rect.adjusted(2, 2, -2, -2), 1, 1)

            # Draw zone highlight outline if active_zone == zone_name
            if self.active_zone == zone_name:
                painter.setPen(QPen(QColor("#00f0ff"), 1.5, Qt.PenStyle.DashLine))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(rect.adjusted(-5, -5, 5, 5), 8, 8)

        # Draw Corners
        corner_rects = {
            "left_corner": QRectF(5, 50, 6, 60),
            "right_corner": QRectF(409, 50, 6, 60)
        }
        
        corner_color = self.zone_colors["corners"]
        is_corner_active = (self.active_zone == "corners" or self.active_zone == "all")
        c_color = QColor(corner_color.red(), corner_color.green(), corner_color.blue(), 255 if is_corner_active else 60)
        c_glow = QColor(corner_color.red(), corner_color.green(), corner_color.blue(), 100 if is_corner_active else 20)
        
        for name, rect in corner_rects.items():
            if is_corner_active:
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(c_glow))
                painter.drawRoundedRect(rect.adjusted(-2, -2, 2, 2), 3, 3)
                
            painter.setPen(QPen(c_color, 1))
            painter.setBrush(QBrush(c_color))
            painter.drawRoundedRect(rect, 3, 3)
            
        if self.active_zone == "corners":
            painter.setPen(QPen(QColor("#00f0ff"), 1.5, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(2, 45, 12, 70), 4, 4)
            painter.drawRoundedRect(QRectF(406, 45, 12, 70), 4, 4)

    def mousePressEvent(self, event):
        pos = event.position()
        x, y = pos.x(), pos.y()
        
        if 25 <= x <= 135 and 25 <= y <= 135:
            self.zone_selected.emit("left")
        elif 145 <= x <= 275 and 25 <= y <= 135:
            self.zone_selected.emit("middle")
        elif 285 <= x <= 395 and 25 <= y <= 135:
            self.zone_selected.emit("right")
        elif (0 <= x <= 20 and 45 <= y <= 125) or (400 <= x <= 420 and 45 <= y <= 125):
            self.zone_selected.emit("corners")

# ─────────────────────────────────────────────────────────────────────────────
# Main Application
# ─────────────────────────────────────────────────────────────────────────────

class ExcaliburControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LupuS Excalibur WMI Control Center")
        self.setFixedSize(1000, 700)
        self.setWindowIcon(get_icon())
        
        self.hwmon_path = find_hwmon_path()
        self.modes = get_available_modes()
        self.selected_color = "FFFFFF"
        self.selected_brightness = 2
        self.swatches = {}

        self.settings = QSettings("LupuS", "ExcaliburControlPanel")
        self.close_to_tray = self.settings.value("close_to_tray", True, type=bool)
        self.setup_tray_icon()

        self.init_ui()
        self.setStyleSheet(STYLESHEET)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_fans)
        self.timer.start(1000)
        
        self.load_initial_state()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Sidebar Layout
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)
        
        # Logo & Title
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(20, 0, 20, 20)
        
        title_label = QLabel("EXCALIBUR")
        title_label.setStyleSheet("font-size: 20px; font-weight: 800; color: #00f0ff; letter-spacing: 2px;")
        subtitle_label = QLabel("CONTROL CENTER")
        subtitle_label.setStyleSheet("font-size: 9px; font-weight: bold; color: #8b949e; letter-spacing: 1px;")
        
        logo_layout.addWidget(title_label)
        logo_layout.addWidget(subtitle_label)
        sidebar_layout.addWidget(logo_container)
        
        # Sidebar Menu Buttons
        self.btn_dashboard = QPushButton("  Dashboard")
        self.btn_dashboard.setProperty("class", "sidebar-btn")
        self.btn_dashboard.setCheckable(True)
        self.btn_dashboard.setChecked(True)
        self.btn_dashboard.setAutoExclusive(True)
        
        self.btn_lighting = QPushButton("  Keyboard Lighting")
        self.btn_lighting.setProperty("class", "sidebar-btn")
        self.btn_lighting.setCheckable(True)
        self.btn_lighting.setAutoExclusive(True)
        
        self.btn_power = QPushButton("  Power Plan")
        self.btn_power.setProperty("class", "sidebar-btn")
        self.btn_power.setCheckable(True)
        self.btn_power.setAutoExclusive(True)
        
        self.btn_about = QPushButton("  Info")
        self.btn_about.setProperty("class", "sidebar-btn")
        self.btn_about.setCheckable(True)
        self.btn_about.setAutoExclusive(True)
        
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_lighting)
        sidebar_layout.addWidget(self.btn_power)
        sidebar_layout.addWidget(self.btn_about)
        
        sidebar_layout.addStretch()
        
        main_layout.addWidget(sidebar, 0)
        
        # 2. Content Area
        content_container = QWidget()
        content_container.setObjectName("ContentArea")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(30, 30, 30, 20)
        content_layout.setSpacing(15)
        
        self.pages = QStackedWidget()
        self.pages.addWidget(self.create_dashboard_page())
        self.pages.addWidget(self.create_lighting_page())
        self.pages.addWidget(self.create_power_page())
        self.pages.addWidget(self.create_about_page())
        
        content_layout.addWidget(self.pages, 1)
        
        # Status Bar
        self.status_bar = QLabel("Ready")
        self.status_bar.setStyleSheet("color: #8b949e; padding: 5px; font-size: 11px;")
        content_layout.addWidget(self.status_bar, 0)
        
        main_layout.addWidget(content_container, 1)
        
        # Navigation connections
        self.btn_dashboard.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.btn_lighting.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        self.btn_power.clicked.connect(lambda: self.pages.setCurrentIndex(2))
        self.btn_about.clicked.connect(lambda: self.pages.setCurrentIndex(3))

    def create_dashboard_page(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        page_title = QLabel("System Dashboard")
        page_title.setProperty("class", "title")
        header_layout.addWidget(page_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Fan Gauges panel
        fans_panel = QFrame()
        fans_panel.setProperty("class", "panel")
        fans_layout = QVBoxLayout(fans_panel)
        fans_layout.setContentsMargins(20, 20, 20, 20)
        
        fans_title = QLabel("COOLING FANS")
        fans_title.setProperty("class", "section-title")
        fans_layout.addWidget(fans_title)
        
        gauge_layout = QHBoxLayout()
        gauge_layout.setSpacing(35)
        self.cpu_gauge = FanGauge("CPU FAN")
        self.gpu_gauge = FanGauge("GPU FAN")
        gauge_layout.addWidget(self.cpu_gauge)
        gauge_layout.addWidget(self.gpu_gauge)
        fans_layout.addLayout(gauge_layout)
        layout.addWidget(fans_panel)
        
        # Quick Power Plan panel
        pp_panel = QFrame()
        pp_panel.setProperty("class", "panel")
        pp_layout = QVBoxLayout(pp_panel)
        pp_layout.setContentsMargins(20, 20, 20, 20)
        
        pp_title = QLabel("CURRENT POWER PLAN")
        pp_title.setProperty("class", "section-title")
        pp_layout.addWidget(pp_title)
        
        # Active Plan Card
        self.dashboard_plan_card = QFrame()
        self.dashboard_plan_card.setStyleSheet("background-color: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 8px; padding: 15px;")
        dp_layout = QHBoxLayout(self.dashboard_plan_card)
        dp_layout.setContentsMargins(15, 12, 15, 12)
        
        self.db_plan_icon = QLabel("⚡")
        self.db_plan_icon.setStyleSheet("font-size: 24px;")
        self.db_plan_title = QLabel("High Performance")
        self.db_plan_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff;")
        self.db_plan_desc = QLabel("Maximum performance, increased fan speed.")
        self.db_plan_desc.setStyleSheet("font-size: 11px; color: #8b949e;")
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.addWidget(self.db_plan_title)
        text_layout.addWidget(self.db_plan_desc)
        
        dp_layout.addWidget(self.db_plan_icon)
        dp_layout.addLayout(text_layout)
        dp_layout.addStretch()
        
        # Shortcut to Plan Selection page
        go_to_power_btn = QPushButton("Change Plan")
        go_to_power_btn.setStyleSheet("font-size: 11px; padding: 6px 12px;")
        go_to_power_btn.clicked.connect(lambda: self.btn_power.click())
        dp_layout.addWidget(go_to_power_btn)
        
        pp_layout.addWidget(self.dashboard_plan_card)
        layout.addWidget(pp_panel)
        
        layout.addStretch()
        return tab

    def create_lighting_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        page_title = QLabel("Keyboard Lighting")
        page_title.setProperty("class", "title")
        header_layout.addWidget(page_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 1. Interactive Visualizer Panel
        vis_panel = QFrame()
        vis_panel.setProperty("class", "panel")
        vis_layout = QVBoxLayout(vis_panel)
        vis_layout.setContentsMargins(15, 12, 15, 12)
        vis_layout.setSpacing(8)
        
        vis_title_layout = QHBoxLayout()
        vis_title = QLabel("INTERACTIVE KEYBOARD VISUALIZER")
        vis_title.setProperty("class", "section-title")
        vis_desc = QLabel("Click a zone to select and customize its color")
        vis_desc.setStyleSheet("font-size: 10px; color: #6e7681;")
        vis_title_layout.addWidget(vis_title)
        vis_title_layout.addStretch()
        vis_title_layout.addWidget(vis_desc)
        vis_layout.addLayout(vis_title_layout)
        
        self.kbd_visualizer = VirtualKeyboard()
        self.kbd_visualizer.zone_selected.connect(self.on_kbd_zone_clicked)
        
        # Center visualizer in layout
        vis_row = QHBoxLayout()
        vis_row.addStretch()
        vis_row.addWidget(self.kbd_visualizer)
        vis_row.addStretch()
        vis_layout.addLayout(vis_row)
        layout.addWidget(vis_panel)
        
        # 2. Config Panel
        panel = QFrame()
        panel.setProperty("class", "panel")
        panel_layout = QHBoxLayout(panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.setSpacing(35)
        
        # Left side: Config Controls
        left_col = QVBoxLayout()
        left_col.setSpacing(15)
        
        left_col.addWidget(QLabel("Zone Selection", objectName="form-label"))
        self.zone_combo = QComboBox()
        self.zone_combo.addItems(["Left", "Middle", "Right", "Corners", "All"])
        self.zone_combo.currentTextChanged.connect(self.on_zone_combo_changed)
        left_col.addWidget(self.zone_combo)
        
        left_col.addWidget(QLabel("Lighting Effect Mode", objectName="form-label"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([m.capitalize() for m in self.modes])
        left_col.addWidget(self.mode_combo)
        
        left_col.addWidget(QLabel("Brightness Level", objectName="form-label"))
        bright_layout = QHBoxLayout()
        self.bright_buttons = []
        for i, label in enumerate(["Off", "Medium", "Full"]):
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, idx=i: self.set_brightness_ui(idx))
            self.bright_buttons.append(btn)
            bright_layout.addWidget(btn)
        left_col.addLayout(bright_layout)
        
        left_col.addStretch()
        
        # Right side: Color presets
        right_col = QVBoxLayout()
        right_col.setSpacing(15)
        
        right_col.addWidget(QLabel("Color Presets", objectName="form-label"))
        color_grid = QGridLayout()
        color_grid.setSpacing(8)
        for i, (name, hex_color) in enumerate(COLOR_PRESETS):
            swatch = ColorSwatch(name, hex_color)
            swatch.selected.connect(self.on_color_selected)
            self.swatches[hex_color] = swatch
            color_grid.addWidget(swatch, i // 6, i % 6)
        right_col.addLayout(color_grid)
        
        right_col.addWidget(QLabel("Color Preview", objectName="form-label"))
        self.preview_label = QLabel("  FFFFFF — White  ")
        self.preview_label.setMinimumHeight(42)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #FFFFFF; color: black; border-radius: 6px; font-weight: bold; border: 1px solid #30363d;")
        right_col.addWidget(self.preview_label)
        
        right_col.addStretch()
        
        panel_layout.addLayout(left_col, 1)
        panel_layout.addLayout(right_col, 1)
        layout.addWidget(panel)
        
        # Large Apply Button at bottom
        apply_btn = QPushButton("Apply Keyboard Settings")
        apply_btn.setProperty("class", "apply-btn")
        apply_btn.clicked.connect(self.apply_lighting)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def create_power_page(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        page_title = QLabel("Power Management")
        page_title.setProperty("class", "title")
        header_layout.addWidget(page_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        info = QLabel(
            "Select a power profile. Changing the power plan immediately alters the firmware fan curves "
            "and performance characteristics of the Excalibur WMI interface."
        )
        info.setProperty("class", "muted")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Grid of PowerPlanCards
        self.plan_cards = {}
        grid = QGridLayout()
        grid.setSpacing(15)
        
        for idx, (num, (name, icon, desc, color)) in enumerate(POWER_PLANS.items()):
            card = PowerPlanCard(num, name, desc, icon, color)
            card.clicked.connect(self.set_power_plan)
            self.plan_cards[num] = card
            grid.addWidget(card, idx // 2, idx % 2)
            
        layout.addLayout(grid)
        
        # Warning Info box
        warning_box = QFrame()
        warning_box.setStyleSheet("background-color: rgba(255, 170, 0, 0.05); border: 1px solid rgba(255, 170, 0, 0.2); border-radius: 8px; padding: 15px;")
        warn_layout = QHBoxLayout(warning_box)
        warn_layout.setContentsMargins(15, 12, 15, 12)
        warn_layout.setSpacing(12)
        
        warn_icon = QLabel("⚠️")
        warn_icon.setStyleSheet("font-size: 20px;")
        warn_text = QLabel(
            "High Power and Gaming modes will increase fan speed, noise, and power usage.\n"
            "Office and Battery Boost modes prioritize silent operation and battery conservation."
        )
        warn_text.setStyleSheet("font-size: 11px; color: #ffaa00;")
        warn_text.setWordWrap(True)
        
        warn_layout.addWidget(warn_icon)
        warn_layout.addWidget(warn_text, 1)
        
        layout.addWidget(warning_box)
        layout.addStretch()
        return tab

    def create_about_page(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        page_title = QLabel("Information")
        page_title.setProperty("class", "title")
        header_layout.addWidget(page_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Info panel
        panel = QFrame()
        panel.setProperty("class", "panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(25, 25, 25, 25)
        panel_layout.setSpacing(20)
        
        logo = QLabel(ASCII_LOGO)
        logo.setStyleSheet("font-family: monospace; color: #00f0ff; font-size: 12px; font-weight: bold; background-color: #07090c; padding: 15px; border-radius: 8px; border: 1px solid #21262d;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(logo)
        
        # Driver Status Banner
        hwmon = self.hwmon_path or "NOT FOUND"
        status_text = "DRIVER ACTIVE ✓" if self.hwmon_path else "DRIVER INACTIVE ×"
        status_color = "#00ff66" if self.hwmon_path else "#ff0055"
        status_bg = "rgba(0, 255, 102, 0.08)" if self.hwmon_path else "rgba(255, 0, 85, 0.08)"
        status_border = "rgba(0, 255, 102, 0.2)" if self.hwmon_path else "rgba(255, 0, 85, 0.2)"
        
        driver_status_banner = QFrame()
        driver_status_banner.setStyleSheet("""
            background-color: transparent;
            border: none;
            padding: 5px;
        """)

        dsb_layout = QHBoxLayout(driver_status_banner)
        dsb_layout.setContentsMargins(15, 10, 15, 10)
        dsb_layout.setSpacing(12)
        
        logo_path = Path(__file__).parent / "logo.png"
        if not logo_path.exists():
            logo_path = Path("/opt/excalibur-panel/logo.png")
            
        dsb_icon = QLabel()
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path)).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            dsb_icon.setPixmap(pixmap)
            dsb_icon.setFixedSize(70, 70)
            dsb_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            #dsb_icon.setStyleSheet(f"padding-right: 15px;")
        else:
            dsb_icon.setText("🛡️")
            dsb_icon.setStyleSheet("font-size: 20px;")
        
        dsb_text_layout = QVBoxLayout()
        dsb_text_layout.setSpacing(2)
        
        dsb_status = QLabel(status_text)
        dsb_status.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {status_color}; letter-spacing: 1px;")
        
        dsb_desc = QLabel("Excalibur ACPI/WMI driver interface is fully loaded and active." if self.hwmon_path else "The excalibur-wmi driver could not be detected. Please ensure it is installed.")
        dsb_desc.setStyleSheet("font-size: 11px; color: #8b949e;")
        
        dsb_text_layout.addWidget(dsb_status)
        dsb_text_layout.addWidget(dsb_desc)
        
        dsb_layout.addWidget(dsb_icon)
        dsb_layout.addLayout(dsb_text_layout)
        dsb_layout.addStretch()
        
        panel_layout.addWidget(driver_status_banner)
        
        # System Detail Grid
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 10, 0, 10)
        grid.setSpacing(12)
        
        def add_row(row, name, val, is_code=False):
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet("font-weight: bold; color: #8b949e;")
            lbl_val = QLabel(val)
            if is_code:
                lbl_val.setStyleSheet("font-family: monospace; color: #00f0ff; background-color: #1c212a; padding: 2px 6px; border-radius: 4px;")
            else:
                lbl_val.setStyleSheet("color: #ffffff;")
            grid.addWidget(lbl_name, row, 0)
            grid.addWidget(lbl_val, row, 1)
            
        add_row(0, "Application Name:", "Excalibur-WMI Control Center")
        add_row(1, "hwmon path:", hwmon, is_code=True)
        add_row(2, "LED Base path:", f"{LED_BASE}/excalibur::kbd_backlight-*", is_code=True)
        add_row(3, "Available Modes:", ", ".join(self.modes), is_code=True)
        
        panel_layout.addWidget(grid_widget)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #21262d; max-height: 1px; border: none;")
        panel_layout.addWidget(separator)
        
        footer = QLabel(
            "<b>Excalibur-WMI Control Center</b> is an open-source system utility for Excalibur laptops.<br>"
            "Designed to control fan performance curves and RGB lighting zones under Linux.<br><br>"
            "<span style='color: #8b949e;'>Source Code: github.com/TeknoAnka/excalibur-wmi-lupus<br>"
            "License: GPL-2.0-or-later</span>"
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setWordWrap(True)
        panel_layout.addWidget(footer)
        
        layout.addWidget(panel)
        layout.addStretch()
        return tab

    def on_color_selected(self, name, hex_color):
        self.selected_color = hex_color
        for s in self.swatches.values():
            s.set_selected(False)
        self.swatches[hex_color].set_selected(True)
        
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        text_color = "black" if lum > 128 else "white"
        
        self.preview_label.setText(f"  #{hex_color} — {name}  ")
        self.preview_label.setStyleSheet(f"background-color: #{hex_color}; color: {text_color}; border-radius: 6px; font-weight: bold;")
        
        # Sync the visualizer color!
        zone = self.zone_combo.currentText().lower()
        self.kbd_visualizer.set_zone_color(zone, hex_color)

    def on_zone_combo_changed(self, text):
        self.kbd_visualizer.set_active_zone(text.lower())

    def on_kbd_zone_clicked(self, zone_name):
        # Translate zone click to combo selection
        index = self.zone_combo.findText(zone_name.capitalize())
        if index >= 0:
            self.zone_combo.setCurrentIndex(index)

    def set_brightness_ui(self, level):
        self.selected_brightness = level
        for i, btn in enumerate(self.bright_buttons):
            if i == level:
                btn.setProperty("class", "active-btn")
            else:
                btn.setProperty("class", "")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def load_initial_state(self):
        self.update_fans()
        if self.hwmon_path:
            raw = _read(f"{self.hwmon_path}/pwm1")
            if raw:
                try:
                    self.update_plan_ui(int(raw))
                except ValueError: pass
        else:
            self.update_plan_ui(3)
        self.set_brightness_ui(2)
        self.on_color_selected("White", "FFFFFF")
        self.kbd_visualizer.set_zone_color("all", "FFFFFF")

    def update_fans(self):
        if not self.hwmon_path: return
        
        cpu_raw = _read(f"{self.hwmon_path}/fan1_input")
        gpu_raw = _read(f"{self.hwmon_path}/fan2_input")
        
        cpu_rpm = int(cpu_raw) if cpu_raw and cpu_raw.isdigit() else 0
        gpu_rpm = int(gpu_raw) if gpu_raw and gpu_raw.isdigit() else 0
        
        self.cpu_gauge.update_rpm(cpu_rpm)
        self.gpu_gauge.update_rpm(gpu_rpm)

    def update_plan_ui(self, plan):
        # 1. Update power plan cards
        for num, card in self.plan_cards.items():
            card.set_active(num == plan)
            
        # 2. Update dashboard summary card
        if plan in POWER_PLANS:
            name, icon, desc, color = POWER_PLANS[plan]
            self.db_plan_title.setText(name)
            self.db_plan_desc.setText(desc)
            self.db_plan_icon.setText(icon)
            self.db_plan_icon.setStyleSheet(f"font-size: 24px; color: {color};")
            self.dashboard_plan_card.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba({QColor(color).red()}, {QColor(color).green()}, {QColor(color).blue()}, 0.05);
                    border: 1px solid rgba({QColor(color).red()}, {QColor(color).green()}, {QColor(color).blue()}, 0.2);
                    border-radius: 8px;
                    padding: 15px;
                }}
            """)

    def set_power_plan(self, plan):
        if not self.hwmon_path:
            self.show_status("Error: Driver not found", False)
            return
            
        ok, err = _write(f"{self.hwmon_path}/pwm1", str(plan))
        if ok:
            self.update_plan_ui(plan)
            self.show_status(f"Power plan set to {POWER_PLANS[plan][0]}")
        else:
            self.show_status(f"Error: {err}", False)

    def apply_lighting(self):
        zone = self.zone_combo.currentText().lower()
        mode = self.mode_combo.currentText().lower()
        color = self.selected_color
        bright = self.selected_brightness
        
        zones_to_write = list(ZONE_NAMES) if zone == "all" else [zone]
        errors = []
        
        for z in zones_to_write:
            for attr, value in [("color", color), ("mode", mode)]:
                ok, err = _write(led_path(z, attr), value)
                if not ok:
                    errors.append(err)
                    break
        
        if errors:
            self.show_status(f"Error: {errors[0]}", False)
            return

        # Brightness logic (mirrored from original)
        if zone == "all":
            ok, err = _write(led_path("left", "brightness"), str(bright))
            if ok:
                _write(led_path("corners", "brightness"), str(bright))
            else:
                errors.append(err)
        elif zone == "corners":
            _write(led_path("corners", "brightness"), str(bright))
            
        if errors:
            self.show_status(f"Error: {errors[0]}", False)
        else:
            msg = f"Applied to {zone.capitalize()}: {mode}"
            if zone in ("left", "middle", "right"):
                msg += " (use All for brightness)"
            self.show_status(msg)

    def show_status(self, msg, ok=True):
        color = "#00ff66" if ok else "#ff0055"
        self.status_bar.setText(msg)
        self.status_bar.setStyleSheet(f"color: {color}; font-weight: bold; padding: 5px;")
        QTimer.singleShot(3000, lambda: self.status_bar.setStyleSheet("color: #8b949e; padding: 5px;"))

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(get_icon())
        self.tray_icon.setToolTip("Control Center")
        
        tray_menu = QMenu(self)
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_and_activate)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_and_activate()

    def show_and_activate(self):
        self.show()
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def quit_app(self):
        self.really_quit = True
        self.close()
        QApplication.quit()

    def closeEvent(self, event):
        if self.close_to_tray and hasattr(self, "tray_icon") and self.tray_icon.isVisible() and not getattr(self, "really_quit", False):
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Control Center",
                "The app continues to run in the background.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            event.accept()

if __name__ == "__main__":
    try:
        import setproctitle
        setproctitle.setproctitle("excalibur-control-panel")
    except ImportError:
        pass

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    app.setApplicationName("Excalibur Control Center")
    # Single instance check
    helper = SingleInstanceHelper("excalibur_control_panel_socket")
    if helper.try_raise_existing(sys.argv):
        print("Another instance is already running. Exiting.")
        sys.exit(0)
        
    # Check driver
    led_glob = glob.glob(f"{LED_BASE}/excalibur::kbd_backlight-*")
    if not led_glob and not find_hwmon_path():
        print("Warning: excalibur-wmi driver not found.")
        
    window = ExcaliburControlPanel()
    helper.start_server(window)
    
    # Check if starting minimized
    if "--minimized" not in sys.argv and "-m" not in sys.argv:
        window.show()
        
    sys.exit(app.exec())
