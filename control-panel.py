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
    QGridLayout, QSizePolicy, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QColor, QPalette, QBrush, QPixmap, QImage, QIcon, QAction
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

# ─────────────────────────────────────────────────────────────────────────────
# Sysfs helpers (Ported from original)
# ─────────────────────────────────────────────────────────────────────────────

LED_BASE = "/sys/class/leds"
HWMON_BASE = "/sys/class/hwmon"
ZONE_NAMES = ("left", "middle", "right", "corners")

POWER_PLANS = {
    1: ("High Performance", ""),
    2: ("Gaming", ""),
    3: ("Office", ""),
    4: ("Battery Boost", ""),
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
QMainWindow {
    background-color: #0d0d0d;
}

QTabWidget::pane {
    border: 1px solid #1a1a2e;
    background: transparent;
}

QTabBar::tab {
    background: #1a1a2e;
    color: #888;
    padding: 10px 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background: #2a2a4e;
    color: cyan;
    border-bottom: 2px solid cyan;
}

QLabel {
    color: white;
}

.title {
    font-weight: bold;
    color: cyan;
    font-size: 16px;
}

.muted {
    color: #888;
}

QFrame.panel {
    border: 1px solid #333;
    border-radius: 8px;
    background-color: rgba(26, 26, 46, 180);
}

QPushButton {
    background-color: #1a1a2e;
    color: white;
    border: 1px solid #333;
    padding: 8px;
    border-radius: 4px;
}

QPushButton:hover {
    background-color: #2a2a4e;
    border-color: cyan;
}

QPushButton.active-btn {
    background-color: cyan;
    color: black;
    font-weight: bold;
}

QPushButton.apply-btn {
    background-color: #008888;
    font-weight: bold;
}

QComboBox {
    background-color: #1a1a2e;
    color: white;
    border: 1px solid #333;
    padding: 5px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollArea > QWidget > QWidget {
    background: transparent;
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Custom Widgets
# ─────────────────────────────────────────────────────────────────────────────

class FanGauge(QFrame):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setObjectName("FanGauge")
        self.setProperty("class", "panel")
        self.setFixedSize(250, 120)
        
        layout = QVBoxLayout(self)
        self.label = QLabel(label)
        self.label.setProperty("class", "muted")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.rpm_label = QLabel("0 RPM")
        self.rpm_label.setStyleSheet("font-size: 20px;")
        self.rpm_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.bar = QLabel("                    ")
        self.bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bar.setStyleSheet("font-family: monospace;")
        
        layout.addWidget(self.label)
        layout.addWidget(self.rpm_label)
        layout.addWidget(self.bar)

    def update_rpm(self, rpm):
        self.rpm_label.setText(f"{rpm:,} RPM")
        
        color = "cyan"
        if rpm == 0: color = "#555"
        elif rpm < 2000: color = "green"
        elif rpm < 4000: color = "yellow"
        else: color = "red"
        
        self.rpm_label.setStyleSheet(f"font-size: 20px; color: {color};")
        
        max_rpm = 6000
        filled = int((min(rpm, max_rpm) / max_rpm) * 15)
        bar_text = "■" * filled + " " * (15 - filled)
        self.bar.setText(bar_text)
        self.bar.setStyleSheet(f"font-family: monospace; color: {color};")

class ColorSwatch(QPushButton):
    selected = pyqtSignal(str, str)
    
    def __init__(self, name, hex_color, parent=None):
        super().__init__(name[:2], parent)
        self._name = name
        self._hex = hex_color
        self.setFixedSize(40, 40)
        
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        text_color = "black" if lum > 128 else "white"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #{hex_color};
                color: {text_color};
                border: 2px solid transparent;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid cyan;
            }}
        """)
        self.clicked.connect(lambda: self.selected.emit(self._name, self._hex))

    def set_selected(self, is_selected):
        if is_selected:
            self.setStyleSheet(self.styleSheet() + "border: 2px solid white;")
        else:
            self.setStyleSheet(self.styleSheet().replace("border: 2px solid white;", "border: 2px solid transparent;"))

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

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab 1: Dashboard
        self.tabs.addTab(self.create_dashboard_tab(), "Fan")
        
        # Tab 2: Lighting
        self.tabs.addTab(self.create_lighting_tab(), "Keyboard Lighting")
        
        # Tab 3: Power
        self.tabs.addTab(self.create_power_tab(), "Power Plan")
        
        # Tab 5: About
        self.tabs.addTab(self.create_about_tab(), "About")

        self.status_bar = QLabel("Ready")
        self.status_bar.setStyleSheet("color: #888; padding: 5px;")
        main_layout.addWidget(self.status_bar)

    def create_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Fan Section
        fan_title = QLabel("Fan Speeds")
        fan_title.setProperty("class", "muted")
        layout.addWidget(fan_title)
        
        fan_layout = QHBoxLayout()
        self.cpu_gauge = FanGauge("󱑲  CPU Fan")
        self.gpu_gauge = FanGauge("󱑳  GPU Fan")
        fan_layout.addWidget(self.cpu_gauge)
        fan_layout.addWidget(self.gpu_gauge)
        self.cpu_gauge.setStyleSheet("font-size: 16px")
        self.gpu_gauge.setStyleSheet("font-size: 16px")
        layout.addLayout(fan_layout)
        
        # Power Plan Section
        layout.addSpacing(20)
        pp_panel = QFrame()
        pp_panel.setProperty("class", "panel")
        pp_layout = QVBoxLayout(pp_panel)
        pp_layout.addWidget(QLabel("Power Plan", objectName="plan-title"))
        
        btn_layout = QHBoxLayout()
        self.plan_buttons = {}
        for num, (name, icon) in POWER_PLANS.items():
            btn = QPushButton(f"{icon} {name}")
            btn.clicked.connect(lambda checked, n=num: self.set_power_plan(n))
            self.plan_buttons[num] = btn
            btn_layout.addWidget(btn)
        pp_layout.addLayout(btn_layout)
        layout.addWidget(pp_panel)
        
        layout.addStretch()
        return tab

    def create_lighting_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        
        panel = QFrame()
        panel.setProperty("class", "panel")
        panel_layout = QVBoxLayout(panel)
        
        title = QLabel("Keyboard Lighting")
        title.setProperty("class", "title")
        panel_layout.addWidget(title)
        
        # Zone Selection
        panel_layout.addWidget(QLabel("Zone"))
        self.zone_combo = QComboBox()
        self.zone_combo.addItems(["Left", "Middle", "Right", "Corners", "All"])
        panel_layout.addWidget(self.zone_combo)
        
        # Mode Selection
        panel_layout.addWidget(QLabel("Mode"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([m.capitalize() for m in self.modes])
        panel_layout.addWidget(self.mode_combo)
        
        # Color Presets
        panel_layout.addWidget(QLabel("Color Presets"))
        color_grid = QGridLayout()
        for i, (name, hex_color) in enumerate(COLOR_PRESETS):
            swatch = ColorSwatch(name, hex_color)
            swatch.selected.connect(self.on_color_selected)
            self.swatches[hex_color] = swatch
            color_grid.addWidget(swatch, i // 6, i % 6)
        panel_layout.addLayout(color_grid)
        
        # Color Preview
        self.preview_label = QLabel("  FFFFFF — White  ")
        self.preview_label.setMinimumHeight(40)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #FFFFFF; color: black; border-radius: 4px;")
        panel_layout.addWidget(self.preview_label)
        
        # Brightness
        panel_layout.addWidget(QLabel("Brightness"))
        bright_layout = QHBoxLayout()
        self.bright_buttons = []
        for i, label in enumerate(["○ Off", "◑ Medium", "● Full"]):
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, idx=i: self.set_brightness_ui(idx))
            self.bright_buttons.append(btn)
            bright_layout.addWidget(btn)
        panel_layout.addLayout(bright_layout)
        
        # Apply Button
        apply_btn = QPushButton("Apply Lighting")
        apply_btn.setProperty("class", "apply-btn")
        apply_btn.clicked.connect(self.apply_lighting)
        panel_layout.addWidget(apply_btn)
        
        layout.addWidget(panel)
        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def create_power_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("Power Management")
        title.setProperty("class", "title")
        layout.addWidget(title)
        
        pp_panel = QFrame()
        pp_panel.setProperty("class", "panel")
        pp_layout = QVBoxLayout(pp_panel)
        
        # Re-use plan buttons or sync them?
        # For simplicity, we can have another set and sync them.
        self.plan_buttons_tab3 = {}
        btn_layout = QVBoxLayout()
        for num, (name, icon) in POWER_PLANS.items():
            btn = QPushButton(f"{icon} {name}")
            btn.clicked.connect(lambda checked, n=num: self.set_power_plan(n))
            self.plan_buttons_tab3[num] = btn
            btn_layout.addWidget(btn)
        pp_layout.addLayout(btn_layout)
        layout.addWidget(pp_panel)
        
        info = QLabel(
            "\nChanging the power plan immediately alters the firmware fan curves.\n"
            "High Power and Gaming modes will increase fan noise and performance.\n"
            "Text Mode and Low Power prioritise battery life and quiet operation."
        )
        info.setProperty("class", "muted")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        layout.addStretch()
        return tab

    def create_about_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        logo = QLabel(ASCII_LOGO)
        logo.setStyleSheet("font-family: monospace; color: cyan;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        
        hwmon = self.hwmon_path or "NOT FOUND"
        status = "Loaded Successfully ✓" if self.hwmon_path else "Not Detected ×"
        
        info = QLabel(
            f"<b>Excalibur-WMI</b> Control Center<br><br>"
            f"Driver status : <span style='color: {'green' if self.hwmon_path else 'red'}'>{status}</span><br>"
            f"hwmon path    : <span style='color: cyan'>{hwmon}</span><br>"
            f"LED base      : <span style='color: cyan'>{LED_BASE}/excalibur::kbd_backlight-*</span><br><br>"
            f"<i style='color: #888'>Source: github.com/TeknoAnka/excalibur-vmi-lupus<br>"
            f"License: GPL-2.0-or-later</i>"
        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
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
        self.preview_label.setStyleSheet(f"background-color: #{hex_color}; color: {text_color}; border-radius: 4px;")

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
        self.set_brightness_ui(2)
        self.on_color_selected("White", "FFFFFF")

    def update_fans(self):
        if not self.hwmon_path: return
        
        cpu_raw = _read(f"{self.hwmon_path}/fan1_input")
        gpu_raw = _read(f"{self.hwmon_path}/fan2_input")
        
        cpu_rpm = int(cpu_raw) if cpu_raw and cpu_raw.isdigit() else 0
        gpu_rpm = int(gpu_raw) if gpu_raw and gpu_raw.isdigit() else 0
        
        self.cpu_gauge.update_rpm(cpu_rpm)
        self.gpu_gauge.update_rpm(gpu_rpm)

    def update_plan_ui(self, plan):
        for p_map in [self.plan_buttons, self.plan_buttons_tab3]:
            for num, btn in p_map.items():
                if num == plan:
                    btn.setProperty("class", "active-btn")
                else:
                    btn.setProperty("class", "")
                btn.style().unpolish(btn)
                btn.style().polish(btn)

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
        color = "green" if ok else "red"
        self.status_bar.setText(msg)
        self.status_bar.setStyleSheet(f"color: {color}; font-weight: bold; padding: 5px;")
        QTimer.singleShot(3000, lambda: self.status_bar.setStyleSheet("color: #888; padding: 5px;"))

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
