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
    QGridLayout, QSizePolicy, QSystemTrayIcon, QMenu, QStackedWidget,
    QColorDialog, QCheckBox, QInputDialog, QLineEdit, QSpinBox,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QSettings, QRectF, QPointF
from PyQt6.QtGui import QFont, QColor, QPalette, QBrush, QPixmap, QImage, QIcon, QAction, QPainter, QPen, QPainterPath
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

# ─────────────────────────────────────────────────────────────────────────────
# Localization Support (Turkish & English)
# ─────────────────────────────────────────────────────────────────────────────
import locale
LANG = "en"
try:
    sys_lang = locale.getlocale()[0]
    if not sys_lang:
        import os
        sys_lang = os.environ.get("LANG", "en")
    LANG = sys_lang.split('_')[0].lower()
except Exception:
    import os
    env_lang = os.environ.get("LANG", "en")
    LANG = env_lang.split('_')[0].split('.')[0].lower()

if LANG not in ("tr", "en"):
    LANG = "en"

TRANSLATIONS = {
    "tr": {
        # General & Navigation
        "  Dashboard": "  Panel",
        "  Keyboard Lighting": "  Klavye Aydınlatması",
        "  Power Plan": "  Güç Planı",
        "  Settings": "  Ayarlar",
        "  Info": "  Bilgi",
        "  Fan Curve": "  Fan Eğrisi",
        "Excalibur Control Center": "Excalibur Kontrol Merkezi",
        "CONTROL CENTER": "KONTROL MERKEZİ",
        "Ready": "Hazır",
        "Warning: excalibur-wmi driver not found.": "Uyarı: excalibur-wmi sürücüsü bulunamadı.",
        "Another instance is already running. Exiting.": "Başka bir örnek zaten çalışıyor. Çıkılıyor.",

        # Dashboard Tab
        "System Dashboard": "Sistem Paneli",
        "COOLING & TEMPERATURES": "SOĞUTMA & SICAKLIKLAR",
        "SYSTEM MONITORING": "SİSTEM İZLEME",
        "Power Profile": "Güç Profili",
        "POWER SOURCE": "GÜÇ KAYNAĞI",
        "AC STATUS": "AC DURUMU",
        "🔌 AC Powered": "🔌 Şebeke Gücü",
        "⚡ Charging — {}%": "⚡ Şarj Oluyor — {}%",
        "Connected to AC power": "Şebeke gücüne bağlı",
        "Disconnected from AC power": "Şebeke gücü bağlı değil",
        "Capped / Fully Charged — {}%": "Sınırlandırılmış / Tam Dolu — {}%",
        "CPU TEMPERATURE": "CPU SICAKLIĞI",
        "GPU TEMPERATURE": "GPU SICAKLIĞI",
        "CPU FAN SPEED": "CPU FAN HIZI",
        "GPU FAN SPEED": "GPU FAN HIZI",
        "GPU LOAD": "GPU YÜKÜ",
        "GPU VRAM": "GPU VRAM",
        "CURRENT POWER PLAN": "MEVCUT GÜÇ PLANI",
        "Change Plan": "Planı Değiştir",
        "SYSTEM METRICS HISTORY": "SİSTEM METRİKLERİ GEÇMİŞİ",
        "TEMPERATURE HISTORY (°C)": "SICAKLIK GEÇMİŞİ (°C)",
        "FAN SPEED HISTORY (RPM)": "FAN HIZI GEÇMİŞİ (RPM)",
        "CPU & GPU Temperature History": "CPU & GPU Sıcaklık Geçmişi",
        "Fan Speed History (RPM)": "Fan Hızı Geçmişi (RPM)",
        "SESSION STATISTICS": "OTURUM İSTATİSTİKLERİ",
        "CPU Peak: {}°C | Avg: {}°C": "CPU Zirve: {}°C | Ort: {}°C",
        "GPU Peak: {}°C | Avg: {}°C": "GPU Zirve: {}°C | Ort: {}°C",
        "CPU Fan Max: {:,} RPM | Avg: {:,} RPM": "CPU Fan En Yüksek: {:,} RPM | Ort: {:,} RPM",
        "GPU Fan Max: {:,} RPM | Avg: {:,} RPM": "GPU Fan En Yüksek: {:,} RPM | Ort: {:,} RPM",
        "Power Plan Switches: {}": "Güç Planı Değişikliği: {}",
        "Export Session Stats to CSV…": "Oturum İstatistiklerini CSV Olarak Dışa Aktar…",
        "High Performance": "Yüksek Performans",
        "Maximum performance, increased fan speed.": "Maksimum performans, artırılmış fan hızı.",

        # Keyboard Lighting Tab
        "Keyboard Lighting": "Klavye Aydınlatması",
        "INTERACTIVE KEYBOARD VISUALIZER": "ETKİLEŞİMLİ KLAVYE GÖRSELLEŞTİRİCİSİ",
        "Click a zone to select and customize its color": "Renk seçmek için bir bölgeye tıklayın",
        "LIGHTING PROFILES": "AYDINLATMA PROFİLLERİ",
        "Zone Selection": "Bölge Seçimi",
        "Lighting Effect Mode": "Aydınlatma Efekt Modu",
        "Brightness Level": "Parlaklık Seviyesi",
        "Off": "Kapalı",
        "Medium": "Orta",
        "Full": "Tam",
        "Color Presets": "Renk Ön Ayarları",
        "Color Preview": "Renk Önizleme",
        "KEYBOARD LED CONTROL": "KLAVYE LED KONTROLÜ",
        "Select Profile:": "Profil Seçin:",
        "Save Current Profile": "Mevcut Profili Kaydet",
        "Delete Profile": "Profili Sil",
        "Import…": "İçe Aktar…",
        "Export…": "Dışa Aktar…",
        "Select Zone:": "Bölge Seçin:",
        "Select Effect Mode:": "Efekt Modu Seçin:",
        "Brightness:": "Parlaklık:",
        "○ Off": "○ Kapalı",
        "◑ Medium": "◑ Orta",
        "● Full": "● Tam",
        "✦ Apply Lighting": "✦ Aydınlatmayı Uygula",
        "Apply Keyboard Settings": "Klavye Ayarlarını Uygula",
        "Keyboard Lighting Visualizer Preview": "Klavye Aydınlatma Önizlemesi",
        "Double-click to clear curve points.": "Noktaları temizlemek için çift tıklayın.",
        "Select a profile...": "Profil seçin...",

        # Power Plan Tab
        "Power Management": "Güç Yönetimi",
        "Select a power profile. Changing the power plan immediately alters the firmware fan curves "
        "and performance characteristics of the Excalibur WMI interface.": "Bir güç profili seçin. Güç planını değiştirmek, Excalibur WMI arayüzünün donanım yazılımı fan eğrilerini ve performans özelliklerini anında değiştirir.",
        "Select a power profile. Changing the power plan immediately alters the firmware fan curves and performance characteristics of the Excalibur WMI interface.": "Bir güç profili seçin. Güç planını değiştirmek, Excalibur WMI arayüzünün donanım yazılımı fan eğrilerini ve performans özelliklerini anında değiştirir.",
        "High Power and Gaming modes will increase fan speed, noise, and power usage.\nOffice and Battery Boost modes prioritize silent operation and battery conservation.": "Yüksek Güç ve Oyun modları fan hızını, gürültüyü ve güç tüketimini artırır.\nOfis ve Pil Tasarrufu modları sessiz çalışmaya ve pil tasarrufuna öncelik verir.",
        "Gaming": "Oyun",
        "Office": "Ofis",
        "Battery Boost": "Pil Tasarrufu",
        "Maximum cooling and peak processor speeds.": "Maksimum soğutma ve zirve işlemci hızları.",
        "Optimized cooling for GPU-heavy gaming loads.": "GPU yoğun oyun yükleri için optimize edilmiş soğutma.",
        "Quiet cooling curves for productivity and general tasks.": "Üretkenlik ve genel görevler için sessiz soğutma eğrileri.",
        "Minimal cooling and power draw for maximum efficiency.": "Maksimum verimlilik için minimum soğutma ve güç tüketimi.",

        # Fan Curve Tab
        "Fan Curve Editor": "Fan Eğrisi Düzenleyicisi",
        "CUSTOM FAN CURVE": "ÖZEL FAN EĞRİSİ",
        "🖱  Click to add a point · Drag to move · Double-click to remove a point.\nThe red dashed line shows the current live CPU temperature.\nNote: This curve is stored as a profile. Applying it requires a supported fan control daemon.": "🖱  Nokta eklemek için tıkla · Taşımak için sürükle · Silmek için çift tıkla.\nKırmızı kesikli çizgi anlık CPU sıcaklığını gösterir.\nNot: Bu eğri profil olarak kaydedilir. Uygulamak için desteklenen bir fan kontrol servisi gerekir.",
        "FAN CURVE EDITOR": "FAN EĞRİSİ DÜZENLEYİCİSİ",
        "CPU Fan Curve": "CPU Fan Eğrisi",
        "GPU Fan Curve": "GPU Fan Eğrisi",
        "Drag points to edit. Double-click to add/remove points.": "Düzenlemek için noktaları sürükleyin. Nokta eklemek/silmek için çift tıklayın.",
        "Reset to Default": "Varsayılana Sıfırla",
        "Save Curve": "Eğriyi Kaydet",
        "Export Curve…": "Eğriyi Dışa Aktar…",
        "Import Curve…": "Eğriyi İçe Aktar…",
        "Apply Custom Curves": "Özel Eğrileri Uygula",
        "Active Custom Curve Settings": "Aktif Özel Eğri Ayarları",
        "Apply Custom Fan Curve immediately on profile switch": "Profil geçişinde Özel Fan Eğrisini hemen uygula",
        "Custom curves immediately set the hardware fan curves.": "Özel eğriler donanım fan eğrilerini anında ayarlar.",

        # Settings Tab
        "Settings & Preferences": "Ayarlar & Tercihler",
        "APPLICATION PREFERENCES": "UYGULAMA TERCİHLERİ",
        "APPLICATION SETTINGS": "UYGULAMA AYARLARI",
        "Launch on system startup (Autostart)": "Sistem başlangıcında çalıştır (Otomatik Başlatma)",
        "Close window to system tray": "Pencereyi sistem tepsisine küçült",
        "Start minimized in system tray": "Sistem tepsisinde küçültülmüş başlat",
        "Monitoring Refresh Interval:": "İzleme Yenileme Aralığı:",
        "1 second": "1 saniye",
        "2 seconds": "2 saniye",
        "3 seconds": "3 saniye",
        "5 seconds": "5 saniye",
        "SYSTEM PERMISSIONS": "SİSTEM İZİNLERİ",
        "Udev rules allow running this control panel as a normal user without root privileges (sudo).\nIf you see a permission warning at launch, install the rules below.": "Udev kuralları, bu kontrol panelini kök ayrıcalıkları (sudo) olmadan normal kullanıcı olarak çalıştırmanıza olanak tanır.\nBaşlangıçta bir izin uyarısı görüyorsanız aşağıdaki kuralları yükleyin.",
        "ALERT THRESHOLDS": "UYARI EŞİKLERİ",
        "CPU Temperature Warning:": "CPU Sıcaklık Uyarısı:",
        "GPU Temperature Warning:": "GPU Sıcaklık Uyarısı:",
        "Fan Speed Warning:": "Fan Hızı Uyarısı:",
        "POWER PLAN SCHEDULE": "GÜÇ PLANI PROGRAMI",
        "Automatically switch power plans at specific times of day.\nFormat: HH:MM  →  Power Plan": "Günün belirli saatlerinde güç planlarını otomatik olarak değiştirin.\nFormat: SS:DD  →  Güç Planı",
        "No entries. Add one below.": "Kayıt yok. Aşağıdan ekleyin.",
        "Time:": "Saat:",
        "Plan:": "Plan:",
        "Add": "Ekle",
        "Clear All": "Tümünü Temizle",
        "GAME PROFILE LAUNCHER": "OYUN PROFİLİ BAŞLATICI",
        "Automatically switch power plan and keyboard color when a specific\nprocess (game/app) is detected as running.": "Belirli bir işlem (oyun/uygulama) çalışırken algılandığında güç planını ve klavye rengini otomatik olarak değiştirin.",
        "No game profiles. Add one below.": "Oyun profili yok. Aşağıdan ekleyin.",
        "Process:": "İşlem:",
        "Process name (e.g. steam, cs2)": "İşlem adı (örn. steam, cs2)",
        "EXTERNAL MONITOR DETECTION": "HARİCİ MONİTÖR ALGILAMA",
        "Auto-switch plan when external monitor connects/disconnects": "Harici monitör bağlandığında/çıkarıldığında planı otomatik değiştir",
        "On connect:": "Bağlandığında:",
        "On disconnect:": "Çıkarıldığında:",
        "TDP POWER LIMITS": "TDP GÜÇ SINIRLARI",
        "Limit CPU Power Consumption (TDP) in Watts. "
        "Requires ryzenadj (AMD) or Intel RAPL powercap interface.": "CPU güç tüketimini (TDP) Watt cinsinden sınırlayın. ryzenadj (AMD) veya Intel RAPL powercap arayüzü gerektirir.",
        "Limit CPU Power Consumption (TDP) in Watts. Requires ryzenadj (AMD) or Intel RAPL powercap interface.": "CPU güç tüketimini (TDP) Watt cinsinden sınırlayın. ryzenadj (AMD) veya Intel RAPL powercap arayüzü gerektirir.",
        "Target TDP Limit:": "Hedef TDP Sınırı:",
        "Startup & Window Settings": "Başlangıç & Pencere Ayarları",
        "Start Minimized in System Tray": "Sistem Tepsisinde Küçültülmüş Olarak Başlat",
        "Close to System Tray instead of exiting": "Çıkmak yerine Sistem Tepsisine Küçült",
        "Hardware Diagnostics": "Donanım Teşhisi",
        "Perform internal self-tests for ACPI, WMI, temperature sensors, and LED control paths.": "ACPI, WMI, sıcaklık sensörleri ve LED kontrol yolları için dahili kendi kendini test etmeyi gerçekleştirin.",
        "Run System Diagnostics": "Sistem Teşhisini Çalıştır",
        "Custom Alert Thresholds": "Özel Uyarı Eşikleri",
        "CPU Temp Threshold (°C):": "CPU Sıcaklık Eşiği (°C):",
        "GPU Temp Threshold (°C):": "GPU Sıcaklık Eşiği (°C):",
        "Fan Speed Threshold (RPM):": "Fan Hızı Eşiği (RPM):",
        "AC & BATTERY AUTO POWER PLAN": "AC & PİL OTOMATİK GÜÇ PLANI",
        "Auto-switch power plan on AC connect/disconnect": "AC takıldığında/çıkarıldığında güç planını otomatik değiştir",
        "On AC connected:": "AC bağlandığında:",
        "On AC disconnected (Battery):": "AC çıkarıldığında (Pil):",
        "TDP CONTROL (EXPERIMENTAL)": "TDP KONTROLÜ (DENEYSEL)",
        "Adjust CPU Power Limit (Watts):": "CPU Güç Sınırını Ayarla (Watt):",
        "Apply TDP Limit": "TDP Sınırını Uygula",
        "Configure Udev Rules (No Sudo)": "Udev Kurallarını Yapılandır (Sudo İhtiyacı Yok)",
        "Allow running control panel without root permissions (sudo). This configures udev rules for led backlight and hwmon.": "Kontrol panelinin kök izinleri (sudo) olmadan çalıştırılmasına izin verin. Bu, led arka ışığı ve hwmon için udev kurallarını yapılandırır.",
        "Install Udev Rules (Requires Privileges)": "Udev Kurallarını Yükle (Yetki Gerektirir)",

        # Info Tab
        "Information": "Bilgi",
        "SYSTEM DIAGNOSTICS": "SİSTEM TANI",
        "Click the button below to run system diagnostics...": "Sistem tanılarını çalıştırmak için aşağıdaki düğmeye tıklayın...",
        "Running diagnostics...": "Tanı çalıştırılıyor...",
        "Excalibur ACPI/WMI driver interface is fully loaded and active.": "Excalibur ACPI/WMI sürücü arayüzü tamamen yüklü ve aktif.",
        "The excalibur-wmi driver could not be detected. Please ensure it is installed.": "excalibur-wmi sürücüsü tespit edilemedi. Lütfen yüklü olduğundan emin olun.",
        "DRIVER ACTIVE ✓": "SÜRÜCÜ AKTİF ✓",
        "DRIVER INACTIVE ×": "SÜRÜCÜ PASİF ×",
        "Application Name:": "Uygulama Adı:",
        "Excalibur-WMI Control Center": "Excalibur-WMI Kontrol Merkezi",
        "hwmon path:": "hwmon yolu:",
        "LED Base path:": "LED Taban yolu:",
        "Available Modes:": "Kullanılabilir Modlar:",
        "<b>Excalibur-WMI Control Center</b> is an open-source system utility for Excalibur laptops.<br>Designed to control fan performance curves and RGB lighting zones under Linux.<br><br><span style='color: #8b949e;'>Source Code: github.com/Antolun/excalibur-wmi-lupus<br>License: GPL-2.0-or-later</span>": "<b>Excalibur-WMI Kontrol Merkezi</b>, Excalibur dizüstü bilgisayarlar için açık kaynaklı bir sistem aracıdır.<br>Linux altında fan performans eğrilerini ve RGB aydınlatma bölgelerini kontrol etmek için tasarlanmıştır.<br><br><span style='color: #8b949e;'>Kaynak Kod: github.com/Antolun/excalibur-wmi-lupus<br>Lisans: GPL-2.0-or-later</span>",

        # System Tray Messages & Messages
        "Show": "Göster",
        "Hide": "Gizle",
        "Exit": "Çıkış",
        "Power Plan": "Güç Planı",
        "Control Center": "Kontrol Merkezi",
        "Monitor Detected": "Monitör Algılandı",
        "The app continues to run in the background.": "Uygulama arka planda çalışmaya devam ediyor.",
        "Power Source Changed": "Güç Kaynağı Değişti",
        "Error: Driver not found": "Hata: Sürücü bulunamadı",
        "Error: {}": "Hata: {}",
        "Applied to {}: {}": "{}: {} uygulandı",
        "(use All for brightness)": "(parlaklık için Tümü'nü kullanın)",
        "Udev rules installed! Please re-login/reboot.": "Udev kuralları yüklendi! Lütfen yeniden giriş yapın veya yeniden başlatın.",
        "Udev rules installed successfully!": "Udev kuralları başarıyla yüklendi!",
        "Installation cancelled or failed.": "Kurulum iptal edildi veya başarısız oldu.",
        "TDP limit set to {}W via ryzenadj": "TDP sınırı ryzenadj üzerinden {}W olarak ayarlandı",
        "Failed to set TDP: {}": "TDP ayarlanamadı: {}",
        "TDP apply error: {}": "TDP uygulama hatası: {}",
        "TDP limit set to {}W via Intel RAPL": "TDP sınırı Intel RAPL üzerinden {}W olarak ayarlandı",
        "TDP limit set to {}W via Intel RAPL (authenticated)": "TDP sınırı Intel RAPL üzerinden yetkilendirilmiş olarak {}W olarak ayarlandı",
        "RAPL write error: {}": "RAPL yazma hatası: {}",
        "TDP write cancelled or failed": "TDP yazma iptal edildi veya başarısız oldu",
        "TDP control not supported (ryzenadj or intel-rapl not found)": "TDP kontrolü desteklenmiyor (ryzenadj veya intel-rapl bulunamadı)",
        "Invalid profile name": "Geçersiz profil adı",
        "Sensors and plan status refreshed": "Sensörler ve plan durumu yenilendi",
        "Schedule cleared": "Program temizlendi",
        "Game profiles cleared": "Oyun profilleri temizlendi",
        "Invalid format": "Geçersiz format",

        # Dialogs / Errors
        "Confirm Delete": "Silmeyi Onayla",
        "Are you sure you want to delete profile '{}'?": "'{}' profilini silmek istediğinizden emin misiniz?",
        "Profile Deleted": "Profil Silindi",
        "Save Profile": "Profili Kaydet",
        "Enter profile name:": "Profil adı girin:",
        "Profile saved successfully!": "Profil başarıyla kaydedildi!",
        "Export Profiles": "Profilleri Dışa Aktar",
        "No profiles to export.": "Dışa aktarılacak profil yok.",
        "Export Lighting Profiles": "Aydınlatma Profillerini Dışa Aktar",
        "Exported {} profile(s) to {}": "{} profil {} konumuna aktarıldı",
        "Export failed: {}": "Dışa aktarma başarısız: {}",
        "Import Lighting Profiles": "Aydınlatma Profillerini İçe Aktar",
        "Imported {} profile(s)!": "{} profil içe aktarıldı!",
        "Import failed: {}": "İçe aktarma başarısız: {}",
        "Export Session Statistics": "Oturum İstatistiklerini Dışa Aktar",
        "Export Fan Curve": "Fan Eğrisini Dışa Aktar",
        "Import Fan Curve": "Fan Eğrisini İçe Aktar",
        "Diagnostics": "Teşhis",
        "Checking ACPI/WMI paths...\n": "ACPI/WMI yolları kontrol ediliyor...\n",
        "✓ Found active hwmon at {}\n": "✓ Etkin hwmon bulundu: {}\n",
        "✗ No hwmon found! Fan control unavailable.\n": "✗ hwmon bulunamadı! Fan kontrolü kullanılamıyor.\n",
        "Checking Keyboard RGB controller...\n": "Klavye RGB denetleyicisi kontrol ediliyor...\n",
        "✓ RGB path active: {}\n": "✓ RGB yolu aktif: {}\n",
        "✗ RGB controller not detected under {}\n": "✗ RGB denetleyicisi tespit edilemedi: {}\n",
        "Diagnostics Complete! All interfaces healthy.": "Teşhis Tamamlandı! Tüm arayüzler sağlıklı.",
        "Diagnostics Complete! Some components failed.": "Teşhis Tamamlandı! Bazı bileşenler başarısız oldu.",
        "Warning": "Uyarı",
        "Save Fan Curve": "Fan Eğrisini Kaydet",
        "Save CPU Fan Curve": "CPU Fan Eğrisini Kaydet",
        "Save GPU Fan Curve": "GPU Fan Eğrisini Kaydet",
        "Invalid Curve File": "Geçersiz Eğri Dosyası",
        "File '{}' does not contain a valid fan curve.": "'{}' dosyası geçerli bir fan eğrisi içermiyor.",
        "Fan curve saved.": "Fan eğrisi kaydedildi.",
        "Fan curve reset to default.": "Fan eğrisi varsayılana sıfırlandı.",
        "Active": "Aktif",
        "Inactive": "Pasif",
        "Temperature": "Sıcaklık",
        "Speed": "Hız",
        "Time": "Zaman",
        "CPU Temp": "CPU Sıcaklığı",
        "GPU Temp": "GPU Sıcaklığı",
        "CPU Fan": "CPU Fanı",
        "GPU Fan": "GPU Fanı",
        "System Tray": "Sistem Tepsisi",
        "Excalibur Alert": "Excalibur Uyarısı",
        "AC connected": "AC bağlandı",
        "AC disconnected": "AC kesildi",
        "Left": "Sol",
        "Middle": "Orta",
        "Right": "Sağ",
        "Corners": "Köşeler",
        "All": "Tümü",
        "Static": "Sabit",
        "Blink": "Nefes Alma/Göz Kırpma",
        "Fade": "Yavaşça Kararma",
        "Heartbeat": "Kalp Atışı",
        "Wave": "Dalga",
        "Random": "Rastgele",
        "Rainbow": "Gökkuşağı",
        "Thermal Sync": "Termal Senkronizasyon",
        "AppTitle": "Excalibur Control Center",

        # Color names
        "Red": "Kırmızı",
        "Green": "Yeşil",
        "Blue": "Mavi",
        "Cyan": "Camgöbeği",
        "Magenta": "Eflatun",
        "Yellow": "Sarı",
        "Orange": "Turuncu",
        "Pink": "Pembe",
        "Purple": "Mor",
        "White": "Beyaz",

        # Settings toggle messages
        "Autostart enabled": "Otomatik başlatma etkinleştirildi",
        "Autostart disabled": "Otomatik başlatma devre dışı bırakıldı",
        "Close to tray enabled": "Tepside küçültme etkinleştirildi",
        "Close to tray disabled": "Tepside küçültme devre dışı bırakıldı",
        "Start minimized enabled": "Küçültülmüş başlatma etkinleştirildi",
        "Start minimized disabled": "Küçültülmüş başlatma devre dışı bırakıldı",

        # Sidebar & Stat labels
        "Session Uptime:": "Oturum Süresi:",
        "Avg CPU Temp:": "Ort. CPU Sıcaklığı:",
        "Peak CPU Temp:": "Zirve CPU Sıcaklığı:",
        "Avg GPU Temp:": "Ort. GPU Sıcaklığı:",
        "Peak GPU Temp:": "Zirve GPU Sıcaklığı:",
        "Avg CPU Fan:": "Ort. CPU Fanı:",
        "Peak CPU Fan:": "Zirve CPU Fanı:",
        "Power Plan Changes:": "Güç Planı Değişiklikleri:",
    }
}

def tr(text):
    if LANG == "tr":
        import re
        
        # Match pattern: "External display (connected|disconnected). Switched to (.*) plan."
        m = re.match(r"External display (connected|disconnected)\. Switched to (.*) plan\.", text)
        if m:
            label_eng = m.group(1)
            plan_eng = m.group(2)
            label_tr = "bağlandı" if label_eng == "connected" else "kesildi"
            plan_tr = TRANSLATIONS["tr"].get(plan_eng, plan_eng)
            return f"Harici ekran {label_tr}. {plan_tr} planına geçildi."
            
        # Match pattern: "(AC connected|AC disconnected)\. Switched to (.*) plan\."
        m = re.match(r"(AC connected|AC disconnected)\. Switched to (.*) plan\.", text)
        if m:
            label_eng = m.group(1)
            plan_eng = m.group(2)
            label_tr = "AC bağlandı" if label_eng == "AC connected" else "AC kesildi"
            plan_tr = TRANSLATIONS["tr"].get(plan_eng, plan_eng)
            return f"{label_tr}. {plan_tr} planına geçildi."
            
        # Match pattern: "Applied to (.*): (.*)"
        m = re.match(r"Applied to (\w+): ([\w\s_]+)(.*)", text)
        if m:
            zone_eng = m.group(1)
            mode_eng = m.group(2).strip()
            extra = m.group(3) or ""
            zone_tr = TRANSLATIONS["tr"].get(zone_eng, zone_eng)
            mode_tr = TRANSLATIONS["tr"].get(mode_eng.capitalize(), mode_eng).lower()
            extra_tr = ""
            if "use All for brightness" in extra:
                extra_tr = " " + TRANSLATIONS["tr"].get("(use All for brightness)", "(use All for brightness)")
            return f"{zone_tr} bölgesine uygulandı: {mode_tr}{extra_tr}"

        # Match pattern: "Power plan set to (.*)"
        m = re.match(r"Power plan set to (.*)", text)
        if m:
            plan_eng = m.group(1)
            plan_tr = TRANSLATIONS["tr"].get(plan_eng, plan_eng)
            return f"Güç planı {plan_tr} olarak ayarlandı."

        # Match pattern: "TDP limit set to (\d+)W via (.*)"
        m = re.match(r"TDP limit set to (\d+)W via (.*)", text)
        if m:
            watts = m.group(1)
            via = m.group(2)
            return f"TDP sınırı {via} aracılığıyla {watts}W olarak ayarlandı."

        # Match pattern: "Exported (\d+) profile\(s\) to (.*)"
        m = re.match(r"Exported (\d+) profile\(s\) to (.*)", text)
        if m:
            count = m.group(1)
            path = m.group(2)
            return f"{count} profil {path} konumuna aktarıldı."

        # Match pattern: "Imported (\d+) profile\(s\)!"
        m = re.match(r"Imported (\d+) profile\(s\)!", text)
        if m:
            count = m.group(1)
            return f"{count} profil başarıyla içe aktarıldı!"

        # Match pattern: "File '(.*)' does not contain a valid fan curve."
        m = re.match(r"File '(.*)' does not contain a valid fan curve\.", text)
        if m:
            path = m.group(1)
            return f"'{path}' dosyası geçerli bir fan eğrisi içermiyor."

        # Match pattern: "Are you sure you want to delete profile '(.*)'\?"
        m = re.match(r"Are you sure you want to delete profile '(.*)'\?", text)
        if m:
            name = m.group(1)
            return f"'{name}' profilini silmek istediğinizden emin misiniz?"

        # Match pattern: "CPU Temp: (\d+)°C \(threshold: (\d+)°C\)"
        m = re.match(r"CPU Temp: (\d+)°C \(threshold: (\d+)°C\)", text)
        if m:
            temp = m.group(1)
            thresh = m.group(2)
            return f"CPU Sıcaklığı: {temp}°C (eşik: {thresh}°C)"
            
        m = re.match(r"GPU Temp: (\d+)°C \(threshold: (\d+)°C\)", text)
        if m:
            temp = m.group(1)
            thresh = m.group(2)
            return f"GPU Sıcaklığı: {temp}°C (eşik: {thresh}°C)"
            
        m = re.match(r"CPU Fan: ([\d,]+) RPM \(threshold: ([\d,]+)\)", text)
        if m:
            val = m.group(1)
            thresh = m.group(2)
            return f"CPU Fanı: {val} RPM (eşik: {thresh})"
            
        m = re.match(r"GPU Fan: ([\d,]+) RPM \(threshold: ([\d,]+)\)", text)
        if m:
            val = m.group(1)
            thresh = m.group(2)
            return f"GPU Fanı: {val} RPM (eşik: {thresh})"

        # Prefix checks
        if text.startswith("Error: "):
            return "Hata: " + TRANSLATIONS["tr"].get(text[7:], text[7:])
        if text.startswith("Failed to set TDP: "):
            return "TDP ayarlanamadı: " + TRANSLATIONS["tr"].get(text[19:], text[19:])
        if text.startswith("TDP Apply error: "):
            return "TDP Uygulama hatası: " + text[17:]
        if text.startswith("TDP apply error: "):
            return "TDP Uygulama hatası: " + text[17:]
        if text.startswith("RAPL write error: "):
            return "RAPL yazma hatası: " + text[18:]

        return TRANSLATIONS["tr"].get(text, text)
    return text

# Monkey patching PyQt6 widgets for global translation support
from PyQt6.QtWidgets import QAbstractButton, QLabel, QWidget, QMenu, QMessageBox, QFileDialog, QSystemTrayIcon
from PyQt6.QtGui import QAction

# 1. Patch QAbstractButton (QPushButton, QCheckBox, etc.)
_orig_QAbstractButton_init = QAbstractButton.__init__
def _new_QAbstractButton_init(self, *args, **kwargs):
    if args and isinstance(args[0], str):
        args = (tr(args[0]),) + args[1:]
    elif "text" in kwargs and isinstance(kwargs["text"], str):
        kwargs["text"] = tr(kwargs["text"])
    _orig_QAbstractButton_init(self, *args, **kwargs)
QAbstractButton.__init__ = _new_QAbstractButton_init

_orig_QAbstractButton_setText = QAbstractButton.setText
def _new_QAbstractButton_setText(self, text):
    _orig_QAbstractButton_setText(self, tr(text))
QAbstractButton.setText = _new_QAbstractButton_setText

# 2. Patch QLabel
_orig_QLabel_init = QLabel.__init__
def _new_QLabel_init(self, *args, **kwargs):
    if args and isinstance(args[0], str):
        args = (tr(args[0]),) + args[1:]
    elif "text" in kwargs and isinstance(kwargs["text"], str):
        kwargs["text"] = tr(kwargs["text"])
    _orig_QLabel_init(self, *args, **kwargs)
QLabel.__init__ = _new_QLabel_init

_orig_QLabel_setText = QLabel.setText
def _new_QLabel_setText(self, text):
    _orig_QLabel_setText(self, tr(text))
QLabel.setText = _new_QLabel_setText

# 3. Patch QAction
_orig_QAction_init = QAction.__init__
def _new_QAction_init(self, *args, **kwargs):
    if args and isinstance(args[0], str):
        args = (tr(args[0]),) + args[1:]
    elif "text" in kwargs and isinstance(kwargs["text"], str):
        kwargs["text"] = tr(kwargs["text"])
    _orig_QAction_init(self, *args, **kwargs)
QAction.__init__ = _new_QAction_init

_orig_QAction_setText = QAction.setText
def _new_QAction_setText(self, text):
    _orig_QAction_setText(self, tr(text))
QAction.setText = _new_QAction_setText

# 4. Patch QWidget.setWindowTitle
_orig_QWidget_setWindowTitle = QWidget.setWindowTitle
def _new_QWidget_setWindowTitle(self, title):
    _orig_QWidget_setWindowTitle(self, tr(title))
QWidget.setWindowTitle = _new_QWidget_setWindowTitle

# 5. Patch QWidget.setToolTip
_orig_QWidget_setToolTip = QWidget.setToolTip
def _new_QWidget_setToolTip(self, text):
    _orig_QWidget_setToolTip(self, tr(text))
QWidget.setToolTip = _new_QWidget_setToolTip

# 6. Patch QMenu.addMenu & addAction
_orig_QMenu_addMenu = QMenu.addMenu
def _new_QMenu_addMenu(self, *args, **kwargs):
    if args and isinstance(args[0], str):
        args = (tr(args[0]),) + args[1:]
    return _orig_QMenu_addMenu(self, *args, **kwargs)
QMenu.addMenu = _new_QMenu_addMenu

_orig_QMenu_addAction = QMenu.addAction
def _new_QMenu_addAction(self, *args, **kwargs):
    if args and isinstance(args[0], str):
        args = (tr(args[0]),) + args[1:]
    return _orig_QMenu_addAction(self, *args, **kwargs)
QMenu.addAction = _new_QMenu_addAction

# 7. Patch QMessageBox static methods
_orig_QMessageBox_information = QMessageBox.information
def _new_QMessageBox_information(parent, title, text, *args, **kwargs):
    return _orig_QMessageBox_information(parent, tr(title), tr(text), *args, **kwargs)
QMessageBox.information = _new_QMessageBox_information

_orig_QMessageBox_warning = QMessageBox.warning
def _new_QMessageBox_warning(parent, title, text, *args, **kwargs):
    return _orig_QMessageBox_warning(parent, tr(title), tr(text), *args, **kwargs)
QMessageBox.warning = _new_QMessageBox_warning

_orig_QMessageBox_critical = QMessageBox.critical
def _new_QMessageBox_critical(parent, title, text, *args, **kwargs):
    return _orig_QMessageBox_critical(parent, tr(title), tr(text), *args, **kwargs)
QMessageBox.critical = _new_QMessageBox_critical

_orig_QMessageBox_question = QMessageBox.question
def _new_QMessageBox_question(parent, title, text, *args, **kwargs):
    return _orig_QMessageBox_question(parent, tr(title), tr(text), *args, **kwargs)
QMessageBox.question = _new_QMessageBox_question

# 8. Patch QFileDialog static methods
_orig_QFileDialog_getSaveFileName = QFileDialog.getSaveFileName
def _new_QFileDialog_getSaveFileName(parent, caption="", directory="", filter="", *args, **kwargs):
    return _orig_QFileDialog_getSaveFileName(parent, tr(caption), directory, tr(filter), *args, **kwargs)
QFileDialog.getSaveFileName = _new_QFileDialog_getSaveFileName

_orig_QFileDialog_getOpenFileName = QFileDialog.getOpenFileName
def _new_QFileDialog_getOpenFileName(parent, caption="", directory="", filter="", *args, **kwargs):
    return _orig_QFileDialog_getOpenFileName(parent, tr(caption), directory, tr(filter), *args, **kwargs)
QFileDialog.getOpenFileName = _new_QFileDialog_getOpenFileName

# 9. Patch QSystemTrayIcon.setToolTip & showMessage
_orig_QSystemTrayIcon_setToolTip = QSystemTrayIcon.setToolTip
def _new_QSystemTrayIcon_setToolTip(self, text):
    _orig_QSystemTrayIcon_setToolTip(self, tr(text))
QSystemTrayIcon.setToolTip = _new_QSystemTrayIcon_setToolTip

_orig_QSystemTrayIcon_showMessage = QSystemTrayIcon.showMessage
def _new_QSystemTrayIcon_showMessage(self, title, message, *args, **kwargs):
    return _orig_QSystemTrayIcon_showMessage(self, tr(title), tr(message), *args, **kwargs)
QSystemTrayIcon.showMessage = _new_QSystemTrayIcon_showMessage

LED_BASE = "/sys/class/leds"
HWMON_BASE = "/sys/class/hwmon"
ZONE_NAMES = ("left", "middle", "right", "corners")

POWER_PLANS = {
    1: (tr("High Performance"), "⚡", tr("Maximum cooling and peak processor speeds."), "#00f0ff"),
    2: (tr("Gaming"), "🎮", tr("Optimized cooling for GPU-heavy gaming loads."), "#ff0055"),
    3: (tr("Office"), "💼", tr("Quiet cooling curves for productivity and general tasks."), "#00ff66"),
    4: (tr("Battery Boost"), "🔋", tr("Minimal cooling and power draw for maximum efficiency."), "#9d00ff"),
}

COLOR_PRESETS = [
    (tr("White"), "FFFFFF"),
    (tr("Red"), "FF0000"),
    (tr("Orange"), "FF8000"),
    (tr("Yellow"), "FFFF00"),
    (tr("Green"), "00FF00"),
    (tr("Cyan"), "00FFFF"),
    (tr("Blue"), "0000FF"),
    (tr("Magenta"), "FF00FF"),
    (tr("Purple"), "800080"),
    (tr("Pink"), "FF69B4"),
    (tr("Off"), "000000"),
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

def get_colored_tray_icon(color_hex: str) -> QIcon:
    logo_path = Path(__file__).parent / "logo.png"
    if not logo_path.exists():
        logo_path = Path("/opt/excalibur-panel/logo.png")
        
    if logo_path.exists():
        pixmap = QPixmap(str(logo_path)).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    else:
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#30363d"), 2))
        painter.setBrush(QBrush(QColor("#0d1117")))
        painter.drawRoundedRect(2, 6, 28, 20, 4, 4)
        painter.end()
        
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor("#0c0e12"), 1.5))
    painter.setBrush(QBrush(QColor(color_hex)))
    painter.drawEllipse(20, 20, 10, 10)
    painter.end()
    
    return QIcon(pixmap)

UDEV_RULES_CONTENT = r"""# excalibur-wmi udev rules
# Grants write access to LED zones and power plan for wheel/sudo group members,
# allowing the control panel to run without sudo.

# Keyboard LED zones
SUBSYSTEM=="leds", KERNEL=="excalibur*", \
    RUN+="/bin/sh -c 'chown root:wheel /sys%p/brightness /sys%p/color /sys%p/mode /sys%p/raw 2>/dev/null; chmod g+w /sys%p/brightness /sys%p/color /sys%p/mode /sys%p/raw 2>/dev/null'", \
    RUN+="/bin/sh -c 'chown root:sudo  /sys%p/brightness /sys%p/color /sys%p/mode /sys%p/raw 2>/dev/null; chmod g+w /sys%p/brightness /sys%p/color /sys%p/mode /sys%p/raw 2>/dev/null'"

# hwmon (fan speeds + power plan)
SUBSYSTEM=="hwmon", ATTR{name}=="excalibur_wmi", \
    RUN+="/bin/sh -c 'chown root:wheel /sys%p/pwm1 /sys%p/fan1_input /sys%p/fan2_input 2>/dev/null; chmod g+rw /sys%p/pwm1 2>/dev/null'", \
    RUN+="/bin/sh -c 'chown root:sudo  /sys%p/pwm1 /sys%p/fan1_input /sys%p/fan2_input 2>/dev/null; chmod g+rw /sys%p/pwm1 2>/dev/null'"
"""

def get_gpu_load() -> tuple[int, int]:
    """Returns (gpu_load_percent, vram_used_mb). Tries nvidia-smi then rocm-smi."""
    import subprocess
    # NVIDIA
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=2
        )
        if res.returncode == 0:
            parts = res.stdout.strip().split(",")
            load = int(parts[0].strip())
            vram = int(parts[1].strip())
            return load, vram
    except Exception:
        pass
    # AMD (rocm-smi)
    try:
        res = subprocess.run(
            ["rocm-smi", "--showuse", "--csv"],
            capture_output=True, text=True, timeout=2
        )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if line.startswith("card"):
                    parts = line.split(",")
                    if len(parts) >= 2:
                        load = int(float(parts[1].strip().replace("%", "")))
                        return load, 0
    except Exception:
        pass
    # Fallback: /sys/class/drm AMD
    try:
        for card in glob.glob("/sys/class/drm/card*/device/gpu_busy_percent"):
            val = _read(card)
            if val and val.isdigit():
                return int(val), 0
    except Exception:
        pass
    return 0, 0


def get_battery_status() -> tuple[bool, int]:
    """Returns (is_on_ac, capacity_percent). Reads /sys/class/power_supply."""
    is_on_ac = False
    ac_found = False
    for ac in glob.glob("/sys/class/power_supply/AC*") + glob.glob("/sys/class/power_supply/ADP*"):
        online_raw = _read(f"{ac}/online")
        if online_raw:
            ac_found = True
            if online_raw.strip() == "1":
                is_on_ac = True
                break
                
    cap = 100
    for ps in glob.glob("/sys/class/power_supply/BAT*"):
        cap_raw = _read(f"{ps}/capacity")
        if cap_raw and cap_raw.isdigit():
            cap = int(cap_raw)
        if not ac_found:
            status_raw = _read(f"{ps}/status")
            if status_raw:
                is_on_ac = (status_raw.strip().lower() not in ("discharging",))
                
    if not ac_found and not glob.glob("/sys/class/power_supply/BAT*"):
        is_on_ac = True
        
    return is_on_ac, cap


def get_temperatures() -> tuple[int, int]:
    cpu_temp = 0
    gpu_temp = 0
    # CPU temperature search
    # Method A: thermal zones
    for tz in glob.glob("/sys/class/thermal/thermal_zone*"):
        tz_type = _read(f"{tz}/type")
        if tz_type and any(x in tz_type.lower() for x in ("cpu", "pkg", "acpi", "intel")):
            raw = _read(f"{tz}/temp")
            if raw and raw.isdigit():
                cpu_temp = int(raw) // 1000
                break
    # Method B fallback: hwmon coretemp/k10temp
    if cpu_temp == 0:
        for hw in glob.glob("/sys/class/hwmon/hwmon*"):
            name = _read(f"{hw}/name")
            if name and name.lower() in ("coretemp", "k10temp", "cpu_thermal"):
                for temp_input in glob.glob(f"{hw}/temp*_input"):
                    raw = _read(temp_input)
                    if raw and raw.isdigit():
                        cpu_temp = int(raw) // 1000
                        break
                if cpu_temp > 0:
                    break
    
    # GPU temperature search
    for hw in glob.glob("/sys/class/hwmon/hwmon*"):
        name = _read(f"{hw}/name")
        if name and name.lower() in ("amdgpu", "nouveau", "radeon", "nvme"):
            raw = _read(f"{hw}/temp1_input")
            if raw and raw.isdigit():
                gpu_temp = int(raw) // 1000
                break
    return cpu_temp, gpu_temp

def is_autostart_enabled() -> bool:
    try:
        autostart_file = Path(get_user_home()) / ".config" / "autostart" / "excalibur-control-center.desktop"
        return autostart_file.exists()
    except Exception:
        return False

def set_autostart(enabled: bool):
    autostart_dir = Path(get_user_home()) / ".config" / "autostart"
    autostart_file = autostart_dir / "excalibur-control-center.desktop"
    if enabled:
        try:
            autostart_dir.mkdir(parents=True, exist_ok=True)
            if Path("/usr/local/bin/excalibur-panel").exists():
                exec_path = "excalibur-panel --minimized"
            else:
                exec_path = f"{sys.executable} {os.path.abspath(__file__)} --minimized"
            
            icon_path = "/opt/excalibur-panel/logo.png"
            if not Path(icon_path).exists():
                icon_path = str(Path(__file__).parent / "logo.png")

            content = f"""[Desktop Entry]
Type=Application
Exec={exec_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Excalibur Control Center
Comment=Start Excalibur Control Center minimized in tray
Icon={icon_path}
"""
            autostart_file.write_text(content)
        except Exception as e:
            print(f"Failed to enable autostart: {e}")
    else:
        try:
            if autostart_file.exists():
                autostart_file.unlink()
        except Exception as e:
            print(f"Failed to disable autostart: {e}")

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
 ▗▄▖ ▗▖  ▗▖▗▄▄▄▖▗▄▖ ▗▖   ▗▖ ▗▖▗▖  ▗▖
▐▌ ▐▌▐▛▚▖▐▌  █ ▐▌ ▐▌▐▌   ▐▌ ▐▌▐▛▚▖▐▌
▐▛▀▜▌▐▌ ▝▜▌  █ ▐▌ ▐▌▐▌   ▐▌ ▐▌▐▌ ▝▜▌
▐▌ ▐▌▐▌  ▐▌  █ ▝▚▄▞▘▐▙▄▄▖▝▚▄▞▘▐▌  ▐▌
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

/* QCheckBox */
QCheckBox {
    color: #c9d1d9;
    font-size: 13px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #30363d;
    background-color: #161b22;
}
QCheckBox::indicator:checked {
    background-color: #00f0ff;
    border-color: #00f0ff;
}
QCheckBox::indicator:hover {
    border-color: #00f0ff;
}

/* QSpinBox */
QSpinBox {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 6px;
    padding: 5px 8px;
    color: #c9d1d9;
    font-size: 13px;
}
QSpinBox:hover {
    border-color: #30363d;
}
QSpinBox:focus {
    border-color: #00f0ff;
}
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #21262d;
    border: none;
    width: 18px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #30363d;
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Custom Widgets
# ─────────────────────────────────────────────────────────────────────────────

class FanGauge(QWidget):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.label = tr(label)
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

class TempGauge(QWidget):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.label = tr(label)
        self.temp = 0
        self.max_temp = 100
        self.setMinimumSize(180, 180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
    def update_temp(self, temp):
        self.temp = temp
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
        
        # Draw track
        track_pen = QPen(QColor(30, 35, 45, 120), 10, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(rect, 225 * 16, -270 * 16)
        
        # Color based on temp
        if self.temp == 0:
            color = QColor(80, 85, 95)
        elif self.temp < 50:
            color = QColor(0, 240, 102)
        elif self.temp < 75:
            color = QColor(0, 240, 255)
        elif self.temp < 85:
            color = QColor(255, 170, 0)
        else:
            color = QColor(255, 0, 85)
            
        percent = min(self.temp, self.max_temp) / self.max_temp
        span_angle = -int(270 * percent * 16)
        
        if percent > 0:
            glow_pen = QPen(QColor(color.red(), color.green(), color.blue(), 40), 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(glow_pen)
            painter.drawArc(rect, 225 * 16, span_angle)
            
            active_pen = QPen(color, 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(active_pen)
            painter.drawArc(rect, 225 * 16, span_angle)
        
        painter.setPen(QColor(255, 255, 255))
        font_val = QFont("sans-serif", 16, QFont.Weight.Bold)
        painter.setFont(font_val)
        temp_text = f"{self.temp}"
        rpm_rect = QRectF(x, y + size/2 - 25, size, 30)
        painter.drawText(rpm_rect, Qt.AlignmentFlag.AlignCenter, temp_text)
        
        painter.setPen(color)
        font_lbl = QFont("sans-serif", 8, QFont.Weight.Bold)
        painter.setFont(font_lbl)
        lbl_rect = QRectF(x, y + size/2 + 5, size, 15)
        painter.drawText(lbl_rect, Qt.AlignmentFlag.AlignCenter, "°C")
        
        painter.setPen(QColor(139, 148, 158))
        font_outer = QFont("sans-serif", 10, QFont.Weight.Bold)
        painter.setFont(font_outer)
        outer_rect = QRectF(x - 20, y + size - 10, size + 40, 20)
        painter.drawText(outer_rect, Qt.AlignmentFlag.AlignCenter, self.label)

class TelemetryChart(QWidget):
    def __init__(self, chart_type, title, max_val, unit, parent=None):
        super().__init__(parent)
        self.chart_type = chart_type
        self.title = tr(title)
        self.max_val = max_val
        self.unit = unit
        self.cpu_history = [0] * 60
        self.gpu_history = [0] * 60
        self.setMinimumHeight(180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def add_data(self, cpu_val, gpu_val):
        self.cpu_history.pop(0)
        self.cpu_history.append(cpu_val)
        self.gpu_history.pop(0)
        self.gpu_history.append(gpu_val)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        painter.setPen(QPen(QColor("#1c212a"), 1))
        painter.setBrush(QBrush(QColor("#0d1117")))
        painter.drawRoundedRect(0, 0, w, h, 8, 8)

        pad_left, pad_right = 45, 15
        pad_top, pad_bottom = 30, 20
        chart_w = w - pad_left - pad_right
        chart_h = h - pad_top - pad_bottom

        # Title
        painter.setPen(QColor("#8b949e"))
        font_title = QFont("sans-serif", 9, QFont.Weight.Bold)
        painter.setFont(font_title)
        painter.drawText(15, 20, self.title)

        # Horizontal grid lines
        grid_pen = QPen(QColor("#1c212a"), 1, Qt.PenStyle.DashLine)
        font_grid = QFont("sans-serif", 7)
        for i in range(4):
            y_val = i * (self.max_val / 3)
            y_pos = h - pad_bottom - (i * (chart_h / 3))
            painter.setPen(grid_pen)
            painter.drawLine(pad_left, int(y_pos), w - pad_right, int(y_pos))
            painter.setPen(QColor("#6e7681"))
            painter.setFont(font_grid)
            painter.drawText(3, int(y_pos) + 4, f"{int(y_val)}")

        # Plot lines
        def draw_line(history, color_hex):
            path = QPainterPath()
            for idx, val in enumerate(history):
                x = pad_left + idx * (chart_w / 59)
                norm = min(val, self.max_val) / self.max_val if self.max_val else 0
                y = h - pad_bottom - (norm * chart_h)
                if idx == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            pen = QPen(QColor(color_hex), 2, Qt.PenStyle.SolidLine,
                       Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)

        draw_line(self.cpu_history, "#00f0ff")
        draw_line(self.gpu_history, "#ff0055")

        # Legend
        painter.setPen(QPen(QColor("#00f0ff"), 3))
        painter.drawLine(w - 150, 15, w - 135, 15)
        painter.setPen(QColor("#8b949e"))
        painter.setFont(QFont("sans-serif", 8))
        painter.drawText(w - 130, 19, "CPU")
        painter.setPen(QPen(QColor("#ff0055"), 3))
        painter.drawLine(w - 90, 15, w - 75, 15)
        painter.setPen(QColor("#8b949e"))
        painter.drawText(w - 70, 19, "GPU")

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

class CustomColorSwatch(QPushButton):
    selected = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._name = "Custom"
        self._hex = "FFFFFF"
        self.setFixedSize(36, 36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Custom Color...")
        self.setText("🎨")
        
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 red, stop:0.2 yellow, stop:0.4 green, stop:0.6 cyan, stop:0.8 blue, stop:1 magenta);
                border: 2px solid #21262d;
                border-radius: 18px;
                font-size: 14px;
                color: white;
            }
            QPushButton:hover {
                border: 2px solid #00f0ff;
            }
        """)
        self.clicked.connect(self.choose_color)
        
    def choose_color(self):
        color = QColorDialog.getColor(QColor(f"#{self._hex}"), self, "Select Custom Color")
        if color.isValid():
            self._hex = color.name().lstrip("#").upper()
            self.selected.emit(self._name, self._hex)

    def set_selected(self, is_selected):
        if is_selected:
            self.setText("")
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #{self._hex};
                    border: 3px solid #ffffff;
                    border-radius: 18px;
                }}
            """)
        else:
            self.setText("🎨")
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 red, stop:0.2 yellow, stop:0.4 green, stop:0.6 cyan, stop:0.8 blue, stop:1 magenta);
                    border: 2px solid #21262d;
                    border-radius: 18px;
                    font-size: 14px;
                    color: white;
                }
                QPushButton:hover {
                    border: 2px solid #00f0ff;
                }
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

class GpuLoadBar(QWidget):
    """Compact horizontal bar showing GPU load% and VRAM."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load = 0
        self.vram_mb = 0
        self.setMinimumHeight(48)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def update_data(self, load: int, vram_mb: int):
        self.load = load
        self.vram_mb = vram_mb
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#0d1117")))
        painter.drawRoundedRect(0, 0, w, h, 6, 6)

        # Color by load
        if self.load < 40:
            color = QColor(0, 240, 102)
        elif self.load < 70:
            color = QColor(0, 240, 255)
        elif self.load < 90:
            color = QColor(255, 170, 0)
        else:
            color = QColor(255, 0, 85)

        bar_w = int((w - 4) * min(self.load, 100) / 100)
        # Glow
        glow = QColor(color.red(), color.green(), color.blue(), 50)
        painter.setBrush(QBrush(glow))
        painter.drawRoundedRect(2, 2, bar_w, h - 4, 4, 4)
        # Bar
        painter.setBrush(QBrush(color))
        painter.drawRoundedRect(2, 2, bar_w, h - 4, 4, 4)

        # Text
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("sans-serif", 9, QFont.Weight.Bold))
        label = f"GPU  {self.load}%"
        if self.vram_mb:
            label += f"   VRAM {self.vram_mb:,} MB"
        painter.drawText(8, 0, w - 8, h, Qt.AlignmentFlag.AlignVCenter, label)


class FanCurveEditor(QWidget):
    """
    Interactive fan curve editor.
    X axis = CPU temperature (0-100°C), Y axis = Fan speed percent (0-100%).
    Up to 6 draggable control points define the curve.
    """
    curve_changed = pyqtSignal(list)  # emits list of (temp, pct) tuples

    DEFAULT_POINTS = [(30, 10), (50, 25), (65, 50), (75, 70), (85, 90), (95, 100)]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.points = list(self.DEFAULT_POINTS)
        self.drag_idx = -1
        self.setMinimumSize(480, 260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.current_temp = 0  # live CPU temp overlay

    def set_current_temp(self, temp: int):
        self.current_temp = temp
        self.update()

    # ── coordinate mapping ──────────────────────────────────────────────────
    @property
    def _pad(self):
        return (40, 20, 20, 30)  # left, top, right, bottom

    def _chart_rect(self):
        pl, pt, pr, pb = self._pad
        return QRectF(pl, pt, self.width() - pl - pr, self.height() - pt - pb)

    def _to_screen(self, temp, pct):
        r = self._chart_rect()
        x = r.x() + (temp / 100.0) * r.width()
        y = r.y() + r.height() - (pct / 100.0) * r.height()
        return QPointF(x, y)

    def _from_screen(self, sx, sy):
        r = self._chart_rect()
        temp = max(0, min(100, int((sx - r.x()) / r.width() * 100)))
        pct  = max(0, min(100, int((1 - (sy - r.y()) / r.height()) * 100)))
        return temp, pct

    # ── painting ────────────────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self._chart_rect()

        # Background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor("#0d1117")))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 8, 8)

        # Grid lines
        grid_pen = QPen(QColor("#1c212a"), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        font_g = QFont("sans-serif", 7)
        painter.setFont(font_g)
        for i in range(0, 101, 25):
            # horizontal (pct)
            sp = self._to_screen(0, i)
            ep = self._to_screen(100, i)
            painter.drawLine(sp, ep)
            painter.setPen(QColor("#6e7681"))
            painter.drawText(QRectF(0, sp.y() - 8, r.x() - 4, 16),
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             f"{i}%")
            painter.setPen(grid_pen)
            # vertical (temp)
            sp2 = self._to_screen(i, 0)
            ep2 = self._to_screen(i, 100)
            painter.drawLine(sp2, ep2)
            painter.setPen(QColor("#6e7681"))
            painter.drawText(QRectF(sp2.x() - 15, r.y() + r.height() + 4, 30, 14),
                             Qt.AlignmentFlag.AlignCenter, f"{i}°C")
            painter.setPen(grid_pen)

        # Filled area under curve
        if len(self.points) >= 2:
            path_fill = QPainterPath()
            sorted_pts = sorted(self.points, key=lambda p: p[0])
            sp0 = self._to_screen(*sorted_pts[0])
            path_fill.moveTo(self._to_screen(sorted_pts[0][0], 0))
            path_fill.lineTo(sp0)
            for pt in sorted_pts[1:]:
                path_fill.lineTo(self._to_screen(*pt))
            last = sorted_pts[-1]
            path_fill.lineTo(self._to_screen(last[0], 0))
            path_fill.closeSubpath()
            fill_color = QColor(0, 240, 255, 25)
            painter.setBrush(QBrush(fill_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(path_fill)

            # Curve line
            path_line = QPainterPath()
            path_line.moveTo(sp0)
            for pt in sorted_pts[1:]:
                path_line.lineTo(self._to_screen(*pt))
            painter.setPen(QPen(QColor("#00f0ff"), 2.5, Qt.PenStyle.SolidLine,
                                Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path_line)

        # Live temp vertical line
        if self.current_temp > 0:
            lx = self._to_screen(self.current_temp, 0)
            painter.setPen(QPen(QColor("#ff0055"), 1.5, Qt.PenStyle.DashLine))
            painter.drawLine(QPointF(lx.x(), r.y()), QPointF(lx.x(), r.y() + r.height()))
            painter.setPen(QColor("#ff0055"))
            painter.setFont(QFont("sans-serif", 8, QFont.Weight.Bold))
            painter.drawText(QRectF(lx.x() + 3, r.y() + 2, 50, 12),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             f"{self.current_temp}°C")

        # Control points
        sorted_pts = sorted(self.points, key=lambda p: p[0])
        for i, pt in enumerate(sorted_pts):
            sp = self._to_screen(*pt)
            orig_idx = self.points.index(pt)
            is_drag = (orig_idx == self.drag_idx)
            outer_color = QColor("#ffffff") if is_drag else QColor("#00f0ff")
            inner_color = QColor("#00f0ff") if is_drag else QColor("#0d1117")
            painter.setPen(QPen(outer_color, 2))
            painter.setBrush(QBrush(inner_color))
            painter.drawEllipse(sp, 7, 7)
            # Label
            painter.setPen(QColor("#8b949e"))
            painter.setFont(QFont("sans-serif", 7))
            painter.drawText(QRectF(sp.x() - 20, sp.y() - 22, 40, 14),
                             Qt.AlignmentFlag.AlignCenter, f"{pt[1]}%")

    def _nearest_point(self, pos, threshold=12):
        """Return the index of the point nearest to screen position pos, or -1."""
        best_idx = -1
        best_dist = threshold
        for i, pt in enumerate(self.points):
            sp = self._to_screen(*pt)
            dist = ((sp.x() - pos.x()) ** 2 + (sp.y() - pos.y()) ** 2) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best_idx = i
        return best_idx

    # ── mouse interaction ───────────────────────────────────────────────────
    def mousePressEvent(self, event):
        pos = event.position()
        idx = self._nearest_point(pos)
        if idx >= 0:
            self.drag_idx = idx
        else:
            # Add new point
            t, p = self._from_screen(pos.x(), pos.y())
            self.points.append((t, p))
            self.drag_idx = len(self.points) - 1
        self.update()

    def mouseMoveEvent(self, event):
        if self.drag_idx < 0:
            return
        t, p = self._from_screen(event.position().x(), event.position().y())
        self.points[self.drag_idx] = (t, p)
        self.update()

    def mouseReleaseEvent(self, event):
        self.drag_idx = -1
        self.points.sort(key=lambda p: p[0])
        self.curve_changed.emit(self.points)
        self.update()

    def mouseDoubleClickEvent(self, event):
        # Double-click removes nearest point (keep at least 2)
        if len(self.points) <= 2:
            return
        idx = self._nearest_point(event.position())
        if idx >= 0:
            self.points.pop(idx)
            self.drag_idx = -1
            self.update()
            self.curve_changed.emit(self.points)

    def get_curve(self):
        return sorted(self.points, key=lambda p: p[0])

    def set_curve(self, points):
        self.points = list(points)
        self.update()

    def reset_default(self):
        self.points = list(self.DEFAULT_POINTS)
        self.drag_idx = -1
        self.update()
        self.curve_changed.emit(self.points)


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
        self.effect_mode = "static"
        self.tick = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_tick)
        self.timer.start(50)  # 50ms tick
        
    def animate_tick(self):
        self.tick += 1
        if self.effect_mode != "static" and self.effect_mode != "off":
            self.update()

    def set_effect_mode(self, mode):
        self.effect_mode = mode.lower().strip()
        self.update()

    def get_animated_color(self, zone_name, r, c):
        base_color = self.zone_colors.get(zone_name, QColor(255, 255, 255))
        if self.effect_mode == "off":
            return QColor(0, 0, 0)
        elif self.effect_mode == "static":
            return base_color
        elif self.effect_mode == "blink":
            visible = (self.tick // 10) % 2 == 0
            return base_color if visible else QColor(0, 0, 0)
        elif self.effect_mode == "fade":
            import math
            factor = (math.sin(self.tick * 0.15) + 1.0) / 2.0
            return QColor(
                int(base_color.red() * factor),
                int(base_color.green() * factor),
                int(base_color.blue() * factor)
            )
        elif self.effect_mode == "heartbeat":
            import math
            t = self.tick % 60
            if t < 10:
                factor = math.sin(t * math.pi / 10)
            elif 12 < t < 22:
                factor = 0.8 * math.sin((t - 12) * math.pi / 10)
            else:
                factor = 0.0
            return QColor(
                int(base_color.red() * factor),
                int(base_color.green() * factor),
                int(base_color.blue() * factor)
            )
        elif self.effect_mode == "wave":
            import math
            if zone_name == "left":
                col_val = c
            elif zone_name == "middle":
                col_val = 6 + c
            elif zone_name == "right":
                col_val = 13 + c
            else:
                col_val = 0
            factor = (math.sin(self.tick * 0.2 - col_val * 0.4) + 1.0) / 2.0
            return QColor(
                int(base_color.red() * factor),
                int(base_color.green() * factor),
                int(base_color.blue() * factor)
            )
        elif self.effect_mode == "random":
            seed = (self.tick // 6) + r * 7 + c * 13 + hash(zone_name)
            rng_r = (seed * 1103515245 + 12345) & 0xffffffff
            rng_g = (rng_r * 1103515245 + 12345) & 0xffffffff
            rng_b = (rng_g * 1103515245 + 12345) & 0xffffffff
            return QColor(rng_r % 256, rng_g % 256, rng_b % 256)
        elif self.effect_mode == "rainbow":
            if zone_name == "left":
                col_val = c
            elif zone_name == "middle":
                col_val = 6 + c
            elif zone_name == "right":
                col_val = 13 + c
            else:
                col_val = 0
            hue = (self.tick * 3 + col_val * 15) % 360
            color = QColor()
            color.setHsv(hue, 255, 255)
            return color
        elif self.effect_mode == "thermal sync":
            import math
            factor = (math.sin(self.tick * 0.1) + 1.0) / 2.0
            return QColor(int(255 * factor), 0, int(255 * (1 - factor)))
        return base_color

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
            is_selected = (self.active_zone == zone_name or self.active_zone == "all")
            
            # Draw glow underlay if active
            if is_selected:
                glow_base = self.get_animated_color(zone_name, 0, 0)
                glow_color = QColor(glow_base.red(), glow_base.green(), glow_base.blue(), 100)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(glow_color))
                painter.drawRoundedRect(rect.adjusted(-3, -3, 3, 3), 6, 6)
                
            # Draw individual key caps inside this zone
            rows = 5
            cols = 6 if zone_name != "middle" else 7
            key_w = (rect.width() - (cols - 1) * 4) / cols
            key_h = (rect.height() - (rows - 1) * 4) / rows
            
            for r in range(rows):
                for c in range(cols):
                    # Slight layout offset to mimic keyboard staggered rows
                    offset_x = (r * 2) if zone_name == "left" else 0
                    k_x = rect.x() + c * (key_w + 4) + offset_x
                    k_y = rect.y() + r * (key_h + 4)
                    
                    if k_x + key_w > rect.x() + rect.width():
                        continue
                        
                    color_base = self.get_animated_color(zone_name, r, c)
                    
                    # Key cap base
                    key_rect = QRectF(k_x, k_y, key_w, key_h)
                    painter.setPen(QPen(QColor(color_base.red(), color_base.green(), color_base.blue(), 180 if is_selected else 60), 1))
                    painter.setBrush(QBrush(QColor("#161b22")))
                    painter.drawRoundedRect(key_rect, 2, 2)
                    
                    # Key cap legend / center glow
                    bg_color = QColor(color_base.red(), color_base.green(), color_base.blue(), 255 if is_selected else 60)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QBrush(bg_color))
                    painter.drawRoundedRect(key_rect.adjusted(2, 2, -2, -2), 1, 1)

            # Draw zone highlight outline if active_zone == zone_name
            if self.active_zone == zone_name:
                painter.setPen(QPen(QColor("#00f0ff"), 1.5, Qt.PenStyle.DashLine))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(rect.adjusted(-5, -5, 5, 5), 8, 8)
        corner_rects = {
            "left_corner": QRectF(5, 50, 6, 60),
            "right_corner": QRectF(409, 50, 6, 60)
        }
        
        corner_color = self.get_animated_color("corners", 0, 0)
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
        self.setWindowTitle(tr("AppTitle"))
        self.setFixedSize(1200, 850)
        self.setWindowIcon(get_icon())
        
        self.hwmon_path = find_hwmon_path()
        self.modes = get_available_modes()
        self.selected_color = "FFFFFF"
        self.selected_brightness = 2
        self.swatches = {}
        self.active_software_modes = {z: None for z in ZONE_NAMES}

        # Session stats
        self.session_cpu_temps = []
        self.session_gpu_temps = []
        self.session_cpu_rpms = []
        self.session_gpu_rpms = []
        self.session_plan_changes = 0
        self.session_start_time = __import__('time').time()
        self._last_active_plan = -1

        self.settings = QSettings("LupuS", "ExcaliburControlPanel")
        self.close_to_tray = self.settings.value("close_to_tray", True, type=bool)
        self.setup_tray_icon()

        self.init_ui()
        self.setStyleSheet(STYLESHEET)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_fans)
        curr_int = self.settings.value("refresh_interval", 1, type=int)
        self.timer.start(curr_int * 1000)
        
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

        self.btn_settings = QPushButton("  Settings")
        self.btn_settings.setProperty("class", "sidebar-btn")
        self.btn_settings.setCheckable(True)
        self.btn_settings.setAutoExclusive(True)
        
        self.btn_about = QPushButton("  Info")
        self.btn_about.setProperty("class", "sidebar-btn")
        self.btn_about.setCheckable(True)
        self.btn_about.setAutoExclusive(True)
        
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_lighting)
        sidebar_layout.addWidget(self.btn_power)
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addWidget(self.btn_about)

        self.btn_fancurve = QPushButton("  Fan Curve")
        self.btn_fancurve.setProperty("class", "sidebar-btn")
        self.btn_fancurve.setCheckable(True)
        self.btn_fancurve.setAutoExclusive(True)
        sidebar_layout.addWidget(self.btn_fancurve)
        
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
        self.pages.addWidget(self.create_settings_page())
        self.pages.addWidget(self.create_about_page())
        self.pages.addWidget(self.create_fancurve_page())  # index 5
        
        content_layout.addWidget(self.pages, 1)
        
        # Status Bar
        self.status_bar = QLabel(tr("Ready"))
        self.status_bar.setStyleSheet("color: #8b949e; padding: 5px; font-size: 11px;")
        content_layout.addWidget(self.status_bar, 0)
        
        main_layout.addWidget(content_container, 1)
        
        # Navigation connections
        self.btn_dashboard.clicked.connect(lambda: self.pages.setCurrentIndex(0))
        self.btn_lighting.clicked.connect(lambda: self.pages.setCurrentIndex(1))
        self.btn_power.clicked.connect(lambda: self.pages.setCurrentIndex(2))
        self.btn_settings.clicked.connect(lambda: self.pages.setCurrentIndex(3))
        self.btn_about.clicked.connect(lambda: self.pages.setCurrentIndex(4))
        self.btn_fancurve.clicked.connect(lambda: self.pages.setCurrentIndex(5))

    def create_dashboard_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        page_title = QLabel(tr("System Dashboard"))
        page_title.setProperty("class", "title")
        header_layout.addWidget(page_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Telemetry panel
        fans_panel = QFrame()
        fans_panel.setProperty("class", "panel")
        fans_layout = QVBoxLayout(fans_panel)
        fans_layout.setContentsMargins(20, 20, 20, 20)
        
        fans_title = QLabel(tr("COOLING & TEMPERATURES"))
        fans_title.setProperty("class", "section-title")
        fans_layout.addWidget(fans_title)
        
        gauge_layout = QHBoxLayout()
        gauge_layout.setSpacing(15)
        self.cpu_gauge = FanGauge("CPU FAN")
        self.gpu_gauge = FanGauge("GPU FAN")
        self.cpu_temp_gauge = TempGauge("CPU TEMP")
        self.gpu_temp_gauge = TempGauge("GPU TEMP")
        gauge_layout.addWidget(self.cpu_gauge)
        gauge_layout.addWidget(self.gpu_gauge)
        gauge_layout.addWidget(self.cpu_temp_gauge)
        gauge_layout.addWidget(self.gpu_temp_gauge)
        fans_layout.addLayout(gauge_layout)
        layout.addWidget(fans_panel)

        # Real-time Charts Panel
        charts_panel = QWidget()
        charts_layout = QHBoxLayout(charts_panel)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(15)
        
        self.temp_chart = TelemetryChart("temp", "TEMPERATURE HISTORY (°C)", 100, "°C")
        self.fan_chart = TelemetryChart("fan", "FAN SPEED HISTORY (RPM)", 6000, "RPM")
        charts_layout.addWidget(self.temp_chart)
        charts_layout.addWidget(self.fan_chart)
        layout.addWidget(charts_panel)

        # GPU Load + Battery Status row
        gpu_bat_row = QHBoxLayout()
        gpu_bat_row.setSpacing(15)

        # GPU Load panel
        gpu_panel = QFrame()
        gpu_panel.setProperty("class", "panel")
        gpu_panel_layout = QVBoxLayout(gpu_panel)
        gpu_panel_layout.setContentsMargins(20, 15, 20, 15)
        gpu_panel_layout.setSpacing(8)
        gpu_panel_title = QLabel(tr("GPU LOAD"))
        gpu_panel_title.setProperty("class", "section-title")
        gpu_panel_layout.addWidget(gpu_panel_title)
        self.gpu_load_bar = GpuLoadBar()
        gpu_panel_layout.addWidget(self.gpu_load_bar)
        gpu_bat_row.addWidget(gpu_panel, 3)

        # Battery Status panel
        bat_panel = QFrame()
        bat_panel.setProperty("class", "panel")
        bat_layout = QVBoxLayout(bat_panel)
        bat_layout.setContentsMargins(20, 15, 20, 15)
        bat_layout.setSpacing(6)
        bat_title = QLabel(tr("POWER SOURCE"))
        bat_title.setProperty("class", "section-title")
        bat_layout.addWidget(bat_title)
        self.bat_status_label = QLabel(tr("🔌 AC Powered"))
        self.bat_status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00f0ff;")
        self.bat_cap_label = QLabel("")
        self.bat_cap_label.setStyleSheet("font-size: 11px; color: #8b949e;")
        bat_layout.addWidget(self.bat_status_label)
        bat_layout.addWidget(self.bat_cap_label)
        gpu_bat_row.addWidget(bat_panel, 2)

        layout.addLayout(gpu_bat_row)
        
        # Quick Power Plan panel
        pp_panel = QFrame()
        pp_panel.setProperty("class", "panel")
        pp_layout = QVBoxLayout(pp_panel)
        pp_layout.setContentsMargins(20, 20, 20, 20)
        
        pp_title = QLabel(tr("CURRENT POWER PLAN"))
        pp_title.setProperty("class", "section-title")
        pp_layout.addWidget(pp_title)
        
        # Active Plan Card
        self.dashboard_plan_card = QFrame()
        self.dashboard_plan_card.setStyleSheet("background-color: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 8px; padding: 15px;")
        dp_layout = QHBoxLayout(self.dashboard_plan_card)
        dp_layout.setContentsMargins(15, 12, 15, 12)
        
        self.db_plan_icon = QLabel("⚡")
        self.db_plan_icon.setStyleSheet("font-size: 24px;")
        self.db_plan_title = QLabel(tr("High Performance"))
        self.db_plan_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff;")
        self.db_plan_desc = QLabel(tr("Maximum performance, increased fan speed."))
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

        # Session Stats Panel
        stats_panel = QFrame()
        stats_panel.setProperty("class", "panel")
        stats_plo = QVBoxLayout(stats_panel)
        stats_plo.setContentsMargins(20, 20, 20, 20)
        stats_plo.setSpacing(10)

        stats_title = QLabel(tr("SESSION STATISTICS"))
        stats_title.setProperty("class", "section-title")
        stats_plo.addWidget(stats_title)

        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)

        def stat_row(row, label, key):
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #8b949e; font-size: 11px;")
            val = QLabel("—")
            val.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px;")
            stats_grid.addWidget(lbl, row, 0)
            stats_grid.addWidget(val, row, 1)
            return val

        self.stats_labels = {
            "uptime":      stat_row(0, "Session Uptime:", "uptime"),
            "avg_cpu_t":   stat_row(1, "Avg CPU Temp:", "avg_cpu_t"),
            "peak_cpu_t":  stat_row(2, "Peak CPU Temp:", "peak_cpu_t"),
            "avg_gpu_t":   stat_row(3, "Avg GPU Temp:", "avg_gpu_t"),
            "peak_gpu_t":  stat_row(4, "Peak GPU Temp:", "peak_gpu_t"),
            "avg_cpu_f":   stat_row(5, "Avg CPU Fan:", "avg_cpu_f"),
            "peak_cpu_f":  stat_row(6, "Peak CPU Fan:", "peak_cpu_f"),
            "plan_changes":stat_row(7, "Power Plan Changes:", "plan_changes"),
        }
        stats_plo.addLayout(stats_grid)
        
        export_csv_btn = QPushButton("Export Session Stats to CSV…")
        export_csv_btn.setStyleSheet("font-size: 11px; padding: 6px 12px; margin-top: 10px;")
        export_csv_btn.clicked.connect(self.export_stats_csv)
        stats_plo.addWidget(export_csv_btn)

        layout.addWidget(stats_panel)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def create_lighting_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        page_title = QLabel(tr("Keyboard Lighting"))
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
        vis_title = QLabel(tr("INTERACTIVE KEYBOARD VISUALIZER"))
        vis_title.setProperty("class", "section-title")
        vis_desc = QLabel(tr("Click a zone to select and customize its color"))
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
        
        # 1.5. Profiles Panel
        profile_panel = QFrame()
        profile_panel.setProperty("class", "panel")
        profile_layout = QHBoxLayout(profile_panel)
        profile_layout.setContentsMargins(20, 12, 20, 12)
        profile_layout.setSpacing(15)
        
        profile_title = QLabel(tr("LIGHTING PROFILES"))
        profile_title.setProperty("class", "section-title")
        profile_layout.addWidget(profile_title)
        
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(200)
        self.profile_combo.currentTextChanged.connect(self.on_profile_combo_changed)
        profile_layout.addWidget(self.profile_combo)
        
        save_profile_btn = QPushButton("Save Current Profile")
        save_profile_btn.clicked.connect(self.save_profile)
        profile_layout.addWidget(save_profile_btn)
        
        delete_profile_btn = QPushButton("Delete Profile")
        delete_profile_btn.clicked.connect(self.delete_profile)
        profile_layout.addWidget(delete_profile_btn)

        import_profile_btn = QPushButton("Import…")
        import_profile_btn.clicked.connect(self.import_profiles)
        profile_layout.addWidget(import_profile_btn)

        export_profile_btn = QPushButton("Export…")
        export_profile_btn.clicked.connect(self.export_profiles)
        profile_layout.addWidget(export_profile_btn)
        
        profile_layout.addStretch()
        layout.addWidget(profile_panel)
        
        # 2. Config Panel
        panel = QFrame()
        panel.setProperty("class", "panel")
        panel_layout = QHBoxLayout(panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        panel_layout.setSpacing(35)
        
        # Left side: Config Controls
        left_col = QVBoxLayout()
        left_col.setSpacing(15)
        
        left_col.addWidget(QLabel(tr("Zone Selection"), objectName="form-label"))
        self.zone_combo = QComboBox()
        self.zone_combo.addItem(tr("Left"), "left")
        self.zone_combo.addItem(tr("Middle"), "middle")
        self.zone_combo.addItem(tr("Right"), "right")
        self.zone_combo.addItem(tr("Corners"), "corners")
        self.zone_combo.addItem(tr("All"), "all")
        self.zone_combo.currentIndexChanged.connect(
            lambda: self.on_zone_combo_changed(self.zone_combo.currentData() or "all")
        )
        left_col.addWidget(self.zone_combo)
        
        left_col.addWidget(QLabel(tr("Lighting Effect Mode"), objectName="form-label"))
        self.mode_combo = QComboBox()
        for m in self.modes:
            self.mode_combo.addItem(tr(m.capitalize()), m)
        self.mode_combo.addItem(tr("Thermal Sync"), "thermal_sync")
        self.mode_combo.currentIndexChanged.connect(
            lambda: self.kbd_visualizer.set_effect_mode(self.mode_combo.currentData() or "static")
        )
        left_col.addWidget(self.mode_combo)
        
        left_col.addWidget(QLabel(tr("Brightness Level"), objectName="form-label"))
        bright_layout = QHBoxLayout()
        self.bright_buttons = []
        for i, label in enumerate([tr("Off"), tr("Medium"), tr("Full")]):
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, idx=i: self.set_brightness_ui(idx))
            self.bright_buttons.append(btn)
            bright_layout.addWidget(btn)
        left_col.addLayout(bright_layout)
        
        left_col.addStretch()
        
        # Right side: Color presets
        right_col = QVBoxLayout()
        right_col.setSpacing(15)
        
        right_col.addWidget(QLabel(tr("Color Presets"), objectName="form-label"))
        color_grid = QGridLayout()
        color_grid.setSpacing(8)
        for i, (name, hex_color) in enumerate(COLOR_PRESETS):
            swatch = ColorSwatch(name, hex_color)
            swatch.selected.connect(self.on_color_selected)
            self.swatches[hex_color] = swatch
            color_grid.addWidget(swatch, i // 6, i % 6)
        
        # Add CustomColorSwatch at the 12th slot (row 1, col 5)
        self.custom_swatch = CustomColorSwatch()
        self.custom_swatch.selected.connect(self.on_color_selected)
        color_grid.addWidget(self.custom_swatch, 1, 5)
        
        right_col.addLayout(color_grid)
        
        right_col.addWidget(QLabel(tr("Color Preview"), objectName="form-label"))
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
        page_title = QLabel(tr("Power Management"))
        page_title.setProperty("class", "title")
        header_layout.addWidget(page_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        info = QLabel(
            tr("Select a power profile. Changing the power plan immediately alters the firmware fan curves "
            "and performance characteristics of the Excalibur WMI interface.")
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
            tr("High Power and Gaming modes will increase fan speed, noise, and power usage.\n"
            "Office and Battery Boost modes prioritize silent operation and battery conservation.")
        )
        warn_text.setStyleSheet("font-size: 11px; color: #ffaa00;")
        warn_text.setWordWrap(True)
        
        warn_layout.addWidget(warn_icon)
        warn_layout.addWidget(warn_text, 1)
        
        layout.addWidget(warning_box)
        layout.addStretch()
        return tab

    def create_about_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        page_title = QLabel(tr("Information"))
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
        status_text = tr("DRIVER ACTIVE ✓") if self.hwmon_path else tr("DRIVER INACTIVE ×")
        status_color = "#00ff66" if self.hwmon_path else "#ff0055"
        
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
        else:
            dsb_icon.setText("🛡️")
            dsb_icon.setStyleSheet("font-size: 20px;")
        
        dsb_text_layout = QVBoxLayout()
        dsb_text_layout.setSpacing(2)
        
        dsb_status = QLabel(status_text)
        dsb_status.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {status_color}; letter-spacing: 1px;")

        dsb_desc = QLabel(tr("Excalibur ACPI/WMI driver interface is fully loaded and active.") if self.hwmon_path else tr("The excalibur-wmi driver could not be detected. Please ensure it is installed."))
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
            
        add_row(0, tr("Application Name:"), tr("Excalibur-WMI Control Center"))
        add_row(1, tr("hwmon path:"), hwmon, is_code=True)
        add_row(2, tr("LED Base path:"), f"{LED_BASE}/excalibur::kbd_backlight-*", is_code=True)
        add_row(3, tr("Available Modes:"), ", ".join(self.modes), is_code=True)
        
        panel_layout.addWidget(grid_widget)
        
        # Diagnostics Section
        diag_separator = QFrame()
        diag_separator.setFrameShape(QFrame.Shape.HLine)
        diag_separator.setStyleSheet("background-color: #21262d; max-height: 1px; border: none;")
        panel_layout.addWidget(diag_separator)
        
        diag_title = QLabel(tr("SYSTEM DIAGNOSTICS"))
        diag_title.setProperty("class", "section-title")
        panel_layout.addWidget(diag_title)
        
        self.diag_output = QLabel(tr("Click the button below to run system diagnostics..."))
        self.diag_output.setStyleSheet("font-family: monospace; font-size: 10px; color: #8b949e; background-color: #0c0e12; padding: 10px; border-radius: 6px; border: 1px solid #1c212a;")
        self.diag_output.setWordWrap(True)
        panel_layout.addWidget(self.diag_output)
        
        run_diag_btn = QPushButton("Run System Diagnostics")
        run_diag_btn.clicked.connect(self.update_diagnostics)
        panel_layout.addWidget(run_diag_btn)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #21262d; max-height: 1px; border: none;")
        panel_layout.addWidget(separator)
        
        footer = QLabel(
            "<b>Excalibur-WMI Control Center</b> is an open-source system utility for Excalibur laptops.<br>"
            "Designed to control fan performance curves and RGB lighting zones under Linux.<br><br>"
            "<span style='color: #8b949e;'>Source Code: github.com/Antolun/excalibur-wmi-lupus<br>"
            "License: GPL-2.0-or-later</span>"
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setWordWrap(True)
        panel_layout.addWidget(footer)
        
        layout.addWidget(panel)
        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def on_color_selected(self, name, hex_color):
        self.selected_color = hex_color
        for s in self.swatches.values():
            s.set_selected(False)
        self.custom_swatch.set_selected(False)
        
        if hex_color in self.swatches:
            self.swatches[hex_color].set_selected(True)
        else:
            self.custom_swatch._hex = hex_color
            self.custom_swatch.set_selected(True)
        
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        text_color = "black" if lum > 128 else "white"
        
        self.preview_label.setText(f"  #{hex_color} — {name}  ")
        self.preview_label.setStyleSheet(f"background-color: #{hex_color}; color: {text_color}; border-radius: 6px; font-weight: bold;")
        
        # Sync the visualizer color!
        zone = self.zone_combo.currentData() or "all"
        self.kbd_visualizer.set_zone_color(zone, hex_color)

    def on_zone_combo_changed(self, zone_name):
        self.kbd_visualizer.set_active_zone(zone_name)

    def on_kbd_zone_clicked(self, zone_name):
        # Translate zone click to combo selection
        index = self.zone_combo.findData(zone_name.lower())
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
        self.kbd_visualizer.set_effect_mode(self.mode_combo.currentData() or "static")
        self.populate_profiles()

    def update_fans(self):
        # 1. Read Fan Speeds
        cpu_rpm = 0
        gpu_rpm = 0
        if self.hwmon_path:
            cpu_raw = _read(f"{self.hwmon_path}/fan1_input")
            gpu_raw = _read(f"{self.hwmon_path}/fan2_input")
            cpu_rpm = int(cpu_raw) if cpu_raw and cpu_raw.isdigit() else 0
            gpu_rpm = int(gpu_raw) if gpu_raw and gpu_raw.isdigit() else 0
        
        self.cpu_gauge.update_rpm(cpu_rpm)
        self.gpu_gauge.update_rpm(gpu_rpm)
        
        # 2. Read Temperatures
        cpu_temp, gpu_temp = get_temperatures()
        self.cpu_temp_gauge.update_temp(cpu_temp)
        self.gpu_temp_gauge.update_temp(gpu_temp)
        
        # Update Charts
        if hasattr(self, 'temp_chart'):
            self.temp_chart.add_data(cpu_temp, gpu_temp)
        if hasattr(self, 'fan_chart'):
            self.fan_chart.add_data(cpu_rpm, gpu_rpm)

        # 2b. GPU Load & Battery
        if hasattr(self, 'gpu_load_bar'):
            gpu_load, gpu_vram = get_gpu_load()
            self.gpu_load_bar.update_data(gpu_load, gpu_vram)

        if hasattr(self, 'bat_status_label'):
            is_on_ac, cap = get_battery_status()
            is_charging = False
            for ps in glob.glob("/sys/class/power_supply/BAT*"):
                status_raw = _read(f"{ps}/status")
                if status_raw and status_raw.strip().lower() == "charging":
                    is_charging = True
                    break
            
            if is_on_ac:
                if cap >= 99 or not is_charging:
                    self.bat_status_label.setText(tr("🔌 AC Powered"))
                    self.bat_status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00f0ff;")
                    self.bat_cap_label.setText(tr(f"Capped / Fully Charged — {cap}%") if cap < 99 else "")
                else:
                    self.bat_status_label.setText(tr(f"⚡ Charging — {cap}%"))
                    self.bat_status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ff66;")
                    self.bat_cap_label.setText(tr("Connected to AC power"))
            else:
                icon = "🔋" if cap > 20 else "🪫"
                color = "#ffaa00" if cap > 20 else "#ff0055"
                self.bat_status_label.setText(tr(f"{icon} On Battery — {cap}%") if LANG != "tr" else f"{icon} Pil — {cap}%")
                self.bat_status_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color};")
                self.bat_cap_label.setText(tr("Disconnected from AC power"))

        # 2c. Update fan curve live temp indicator
        if hasattr(self, 'fan_curve_editor'):
            self.fan_curve_editor.set_current_temp(cpu_temp)
            
        # Update Software Modes (Thermal Sync)
        for z in ZONE_NAMES:
            if getattr(self, "active_software_modes", {}).get(z) == "thermal_sync":
                max_t = max(cpu_temp, gpu_temp)
                if max_t < 55:
                    color_hex = "0000FF"
                elif max_t < 65:
                    color_hex = "00FF00"
                elif max_t < 75:
                    color_hex = "FF8000"
                else:
                    color_hex = "FF0000"
                _write(led_path(z, "color"), color_hex)
                self.kbd_visualizer.set_zone_color(z, color_hex)
        
        # 3. Update Tray Icon & Telemetry
        if hasattr(self, 'tray_cpu_status'):
            self.tray_cpu_status.setText(f"CPU: {cpu_rpm:,} RPM | {cpu_temp}°C")
            self.tray_gpu_status.setText(f"GPU: {gpu_rpm:,} RPM | {gpu_temp}°C")
        
        if self.hwmon_path:
            raw = _read(f"{self.hwmon_path}/pwm1")
            try:
                active_plan = int(raw) if raw else 3
            except ValueError:
                active_plan = 3
        else:
            active_plan = 3
        
        plan_name = POWER_PLANS.get(active_plan, ("Office", "💼", "", "#00ff66"))[0]
        color_hex = POWER_PLANS.get(active_plan, ("Office", "💼", "", "#00ff66"))[3]
        if hasattr(self, 'tray_icon'):
            self.tray_icon.setToolTip(f"Excalibur: {plan_name}\nCPU: {cpu_temp}°C | GPU: {gpu_temp}°C")
            self.tray_icon.setIcon(get_colored_tray_icon(color_hex))
        
        if hasattr(self, 'tray_power_actions'):
            for num, act in self.tray_power_actions.items():
                act.setChecked(num == active_plan)
            
        # 4. Custom Alert Threshold Warning
        import time
        current_time = time.time()
        last_warn = getattr(self, "last_temp_warning", 0)
        cpu_thresh = self.settings.value("alert_cpu_temp", 85, type=int)
        gpu_thresh = self.settings.value("alert_gpu_temp", 85, type=int)
        fan_thresh = self.settings.value("alert_fan_rpm", 5500, type=int)
        if ((cpu_temp >= cpu_thresh or gpu_temp >= gpu_thresh or
             cpu_rpm >= fan_thresh or gpu_rpm >= fan_thresh) and
                (current_time - last_warn > 300)):
            self.last_temp_warning = current_time
            msg_parts = []
            if cpu_temp >= cpu_thresh:
                msg_parts.append(f"CPU Temp: {cpu_temp}°C (threshold: {cpu_thresh}°C)")
            if gpu_temp >= gpu_thresh:
                msg_parts.append(f"GPU Temp: {gpu_temp}°C (threshold: {gpu_thresh}°C)")
            if cpu_rpm >= fan_thresh:
                msg_parts.append(f"CPU Fan: {cpu_rpm:,} RPM (threshold: {fan_thresh:,})")
            if gpu_rpm >= fan_thresh:
                msg_parts.append(f"GPU Fan: {gpu_rpm:,} RPM (threshold: {fan_thresh:,})")
            if hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage(
                    "Excalibur Alert",
                    "\n".join(msg_parts),
                    QSystemTrayIcon.MessageIcon.Warning,
                    6000
                )

        # 5. Session Stats Collection
        if cpu_temp > 0:
            self.session_cpu_temps.append(cpu_temp)
        if gpu_temp > 0:
            self.session_gpu_temps.append(gpu_temp)
        if cpu_rpm > 0:
            self.session_cpu_rpms.append(cpu_rpm)
        if gpu_rpm > 0:
            self.session_gpu_rpms.append(gpu_rpm)
        if active_plan != self._last_active_plan and self._last_active_plan != -1:
            self.session_plan_changes += 1
        self._last_active_plan = active_plan
        if hasattr(self, 'stats_labels'):
            self._refresh_stats_labels()

        # 6. Game Profile Launcher — process watch
        self._check_game_profiles()

        # 7. Power Schedule — time-based plan
        self._check_power_schedule()

        # 8. External Monitor Detection
        self._check_external_monitor()

        # 9. AC / Battery Auto Plan
        self._check_ac_battery_plan()

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
        zone = self.zone_combo.currentData() or "all"
        mode = self.mode_combo.currentData() or "static"
        color = self.selected_color
        bright = self.selected_brightness
        
        zones_to_write = list(ZONE_NAMES) if zone == "all" else [zone]
        errors = []
        
        # Handle software modes
        if mode == "thermal_sync":
            for z in zones_to_write:
                self.active_software_modes[z] = "thermal_sync"
            mode_to_write = "static"
        else:
            for z in zones_to_write:
                self.active_software_modes[z] = None
            mode_to_write = mode
            
        for z in zones_to_write:
            if mode == "thermal_sync":
                cpu_temp, gpu_temp = get_temperatures()
                max_t = max(cpu_temp, gpu_temp)
                if max_t < 55:
                    color = "0000FF"
                elif max_t < 65:
                    color = "00FF00"
                elif max_t < 75:
                    color = "FF8000"
                else:
                    color = "FF0000"
                    
            for attr, value in [("color", color), ("mode", mode_to_write)]:
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
        self.tray_icon.setToolTip("Excalibur Control Center")
        
        self.tray_menu = QMenu(self)
        
        # Telemetry status in tray
        self.tray_cpu_status = QAction("CPU: -- RPM | --°C", self)
        self.tray_cpu_status.setEnabled(False)
        self.tray_gpu_status = QAction("GPU: -- RPM | --°C", self)
        self.tray_gpu_status.setEnabled(False)
        self.tray_menu.addAction(self.tray_cpu_status)
        self.tray_menu.addAction(self.tray_gpu_status)
        
        self.tray_menu.addSeparator()
        
        # Power Plan Submenu
        self.tray_power_menu = QMenu("Power Plan", self)
        self.tray_power_actions = {}
        for num, (name, icon, _, _) in POWER_PLANS.items():
            act = QAction(f"{icon} {name}", self)
            act.setCheckable(True)
            act.triggered.connect(lambda checked, p=num: self.set_power_plan(p))
            self.tray_power_menu.addAction(act)
            self.tray_power_actions[num] = act
        self.tray_menu.addMenu(self.tray_power_menu)
        
        self.tray_menu.addSeparator()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show_and_activate)
        self.tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        self.tray_menu.addAction(hide_action)
        
        self.tray_menu.addSeparator()
        
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(self.quit_app)
        self.tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_1:
            self.btn_dashboard.setChecked(True)
            self.pages.setCurrentIndex(0)
        elif event.key() == Qt.Key.Key_2:
            self.btn_lighting.setChecked(True)
            self.pages.setCurrentIndex(1)
        elif event.key() == Qt.Key.Key_3:
            self.btn_power.setChecked(True)
            self.pages.setCurrentIndex(2)
        elif event.key() == Qt.Key.Key_4:
            self.btn_settings.setChecked(True)
            self.pages.setCurrentIndex(3)
        elif event.key() == Qt.Key.Key_5:
            self.btn_about.setChecked(True)
            self.pages.setCurrentIndex(4)
        elif event.key() == Qt.Key.Key_R:
            self.update_fans()
            if self.hwmon_path:
                raw = _read(f"{self.hwmon_path}/pwm1")
                if raw:
                    try:
                        self.update_plan_ui(int(raw))
                    except ValueError: pass
            self.show_status(tr("Sensors and plan status refreshed"))
        elif event.key() == Qt.Key.Key_Q:
            self.quit_app()
        else:
            super().keyPressEvent(event)

    def update_diagnostics(self):
        self.diag_output.setText(tr("Running diagnostics..."))
        QApplication.processEvents()
        self.diag_output.setText(self.run_diagnostics())

    def run_diagnostics(self) -> str:
        import subprocess
        log = []
        try:
            res = subprocess.run(["lsmod"], capture_output=True, text=True)
            if "excalibur" in res.stdout:
                log.append("Kernel Module: Loaded (excalibur)")
            else:
                log.append("Kernel Module: NOT Loaded")
        except Exception as e:
            log.append(f"Kernel Module check failed: {e}")
            
        wmi_guid = "644C5791-B7B0-4123-A90B-E93876E0DAAD"
        wmi_dev = Path(f"/sys/bus/wmi/devices/{wmi_guid}")
        # Also check with instance suffix (e.g. -0)
        wmi_dev_inst = Path(f"/sys/bus/wmi/devices/{wmi_guid}-0")
        if wmi_dev.exists() or wmi_dev_inst.exists():
            log.append("WMI GUID: Exposed by firmware and bound")
        else:
            log.append(f"WMI GUID: NOT found ({wmi_guid})")
            log.append("  → This means the firmware does not expose this ACPI/WMI interface.")
            log.append("  → The excalibur-wmi module is loaded but cannot bind to your hardware.")
            log.append("  → Keyboard LED control still works via the sysfs LED class driver.")
            
        led_paths = glob.glob(f"{LED_BASE}/excalibur::kbd_backlight-*")
        log.append(f"LED Zones Found: {len(led_paths)}")
        for lp in led_paths:
            name = Path(lp).name
            writable = os.access(f"{lp}/color", os.W_OK)
            log.append(f"  - {name}: {'Writable' if writable else 'Read-Only (Requires Udev/Sudo)'}")
            
        if self.hwmon_path:
            writable = os.access(f"{self.hwmon_path}/pwm1", os.W_OK)
            log.append(f"hwmon Device: Found ({Path(self.hwmon_path).name})")
            log.append(f"  - Power Plan: {'Writable' if writable else 'Read-Only (Requires Udev/Sudo)'}")
        else:
            log.append("hwmon Device: NOT Found")
            
        log.append("\nRecent Driver Kernel Logs (dmesg):")
        try:
            res = subprocess.run(["dmesg"], capture_output=True, text=True)
            lines = [line for line in res.stdout.splitlines() if "excalibur" in line.lower()]
            if lines:
                log.extend(lines[-5:])
            else:
                log.append("  No driver messages found in dmesg.")
        except Exception as e:
            try:
                res = subprocess.run(["journalctl", "-k", "--grep=excalibur", "-n", "5"], capture_output=True, text=True)
                if res.stdout.strip():
                    log.append(res.stdout.strip())
                else:
                    log.append(f"  Could not read dmesg: {e}")
            except Exception:
                log.append(f"  Could not read dmesg: {e}")
        
        return "\n".join(log)

    # ─────────────────────────────────────────────────────────────────────────
    # Lighting Profiles Management
    # ─────────────────────────────────────────────────────────────────────────

    def populate_profiles(self):
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        self.profile_combo.addItem(tr("Select a profile..."))
        
        profiles = self.settings.value("lighting_profiles", {}, type=dict)
        for name in sorted(profiles.keys()):
            self.profile_combo.addItem(name)
        self.profile_combo.blockSignals(False)

    def save_profile(self):
        name, ok = QInputDialog.getText(self, "Save Profile", "Enter profile name:")
        if not ok or not name.strip():
            return
            
        name = name.strip()
        if name in ("Select a profile...", tr("Select a profile...")):
            self.show_status("Invalid profile name", False)
            return
            
        state = {
            "zone_colors": {z: self.kbd_visualizer.zone_colors[z].name().lstrip("#") for z in ZONE_NAMES},
            "brightness": self.selected_brightness,
            "mode": self.mode_combo.currentData() or "static"
        }
        
        profiles = self.settings.value("lighting_profiles", {}, type=dict)
        profiles[name] = state
        self.settings.setValue("lighting_profiles", profiles)
        
        self.populate_profiles()
        self.profile_combo.setCurrentText(name)
        self.show_status(f"Profile '{name}' saved successfully!")

    def delete_profile(self):
        name = self.profile_combo.currentText()
        if name in ("Select a profile...", tr("Select a profile...")) or not name:
            return
            
        profiles = self.settings.value("lighting_profiles", {}, type=dict)
        if name in profiles:
            del profiles[name]
            self.settings.setValue("lighting_profiles", profiles)
            self.populate_profiles()
            self.show_status(f"Profile '{name}' deleted")

    def on_profile_combo_changed(self, name):
        if name in ("Select a profile...", tr("Select a profile...")) or not name:
            return
            
        profiles = self.settings.value("lighting_profiles", {}, type=dict)
        if name in profiles:
            state = profiles[name]
            zone_colors = state.get("zone_colors", {})
            for z, color_hex in zone_colors.items():
                self.kbd_visualizer.set_zone_color(z, color_hex)
            
            bright = state.get("brightness", 2)
            self.set_brightness_ui(bright)
            
            mode = state.get("mode", "static")
            index = self.mode_combo.findData(mode.lower())
            if index < 0:
                index = self.mode_combo.findText(mode)
            if index >= 0:
                self.mode_combo.setCurrentIndex(index)
                
            errors = []
            for z in ZONE_NAMES:
                color = zone_colors.get(z, "FFFFFF")
                mode_str = mode.lower()
                ok, err = _write(led_path(z, "color"), color)
                if ok:
                    _write(led_path(z, "mode"), mode_str)
                else:
                    errors.append(err)
            
            _write(led_path("left", "brightness"), str(bright))
            _write(led_path("corners", "brightness"), str(bright))
            
            if errors:
                self.show_status(f"Profile applied with errors: {errors[0]}", False)
            else:
                self.show_status(f"Profile '{name}' applied successfully!")

    # ─────────────────────────────────────────────────────────────────────────
    # Game Profile Launcher
    # ─────────────────────────────────────────────────────────────────────────

    def _check_game_profiles(self):
        """Monitor running processes and auto-switch plan/lighting if a matching game is running."""
        profiles = self.settings.value("game_profiles", {}, type=dict)
        if not profiles:
            return
        try:
            import subprocess
            result = subprocess.run(["ps", "-e", "-o", "comm="], capture_output=True, text=True)
            running = set(result.stdout.lower().split())
        except Exception:
            return

        matched = False
        for exe, cfg in profiles.items():
            if exe.lower() in running:
                matched = True
                # Auto power plan
                plan_id = cfg.get("plan")
                if plan_id is not None and self.hwmon_path:
                    current_raw = _read(f"{self.hwmon_path}/pwm1")
                    try:
                        current_plan = int(current_raw) if current_raw else -1
                    except ValueError:
                        current_plan = -1
                    if current_plan != plan_id:
                        _write(f"{self.hwmon_path}/pwm1", str(plan_id))
                        self.update_plan_ui(plan_id)
                # Auto keyboard color
                color = cfg.get("color")
                if color:
                    for z in ZONE_NAMES:
                        _write(led_path(z, "color"), color)
                        _write(led_path(z, "mode"), "static")
                break

    # ─────────────────────────────────────────────────────────────────────────
    # Power Schedule
    # ─────────────────────────────────────────────────────────────────────────

    def _check_power_schedule(self):
        """Apply power plan based on time-of-day schedule entries."""
        schedule = self.settings.value("power_schedule", [], type=list)
        if not schedule or not self.hwmon_path:
            return
        from datetime import datetime
        now_minutes = datetime.now().hour * 60 + datetime.now().minute
        # Find the last entry whose start_time <= now
        best = None
        for entry in schedule:
            try:
                h, m = map(int, entry["time"].split(":"))
                entry_minutes = h * 60 + m
                if entry_minutes <= now_minutes:
                    if best is None or entry_minutes > best["_min"]:
                        best = dict(entry)
                        best["_min"] = entry_minutes
            except Exception:
                continue
        if best is None and schedule:
            # wrap around midnight — use the last entry
            try:
                last = schedule[-1]
                best = dict(last)
            except Exception:
                return
        if best:
            plan_id = int(best.get("plan", 3))
            current_raw = _read(f"{self.hwmon_path}/pwm1")
            try:
                current_plan = int(current_raw) if current_raw else -1
            except ValueError:
                current_plan = -1
            sched_key = f"sched_last_{plan_id}"
            last_applied = getattr(self, sched_key, -1)
            if current_plan != plan_id and last_applied != plan_id:
                setattr(self, sched_key, plan_id)
                _write(f"{self.hwmon_path}/pwm1", str(plan_id))
                self.update_plan_ui(plan_id)

    # ─────────────────────────────────────────────────────────────────────────
    # External Monitor Detection
    # ─────────────────────────────────────────────────────────────────────────

    def _check_external_monitor(self):
        """Detect external monitor via /sys/class/drm and auto-switch plan."""
        if not self.settings.value("monitor_detect_enabled", False, type=bool):
            return
        import glob as _glob
        connected = False
        for connector in _glob.glob("/sys/class/drm/*/status"):
            if "card" in connector and "-" in connector:
                status = _read(connector)
                if status and status.strip() == "connected":
                    # Exclude eDP (built-in screen)
                    if "eDP" not in connector and "LVDS" not in connector:
                        connected = True
                        break
        prev = getattr(self, "_monitor_was_connected", None)
        if prev == connected:
            return  # no change
        self._monitor_was_connected = connected
        if connected:
            plan_id = self.settings.value("monitor_connect_plan", 1, type=int)
        else:
            plan_id = self.settings.value("monitor_disconnect_plan", 4, type=int)
        if self.hwmon_path:
            _write(f"{self.hwmon_path}/pwm1", str(plan_id))
            self.update_plan_ui(plan_id)
        label = "connected" if connected else "disconnected"
        if hasattr(self, 'tray_icon'):
            self.tray_icon.showMessage(
                "Monitor Detected",
                f"External display {label}. Switched to {POWER_PLANS.get(plan_id, ('?',))[0]} plan.",
                QSystemTrayIcon.MessageIcon.Information,
                4000
            )

    # ─────────────────────────────────────────────────────────────────────────
    # AC / Battery Auto Plan
    # ─────────────────────────────────────────────────────────────────────────

    def _check_ac_battery_plan(self):
        """Auto-switch power plan when AC cable is plugged/unplugged."""
        if not self.settings.value("ac_battery_enabled", False, type=bool):
            return
        charging, _cap = get_battery_status()
        prev = getattr(self, "_was_charging", None)
        if prev == charging:
            return  # no change
        self._was_charging = charging
        if charging:
            plan_id = self.settings.value("ac_connect_plan", 1, type=int)
            label = "AC connected"
        else:
            plan_id = self.settings.value("ac_disconnect_plan", 4, type=int)
            label = "AC disconnected"
        if self.hwmon_path:
            _write(f"{self.hwmon_path}/pwm1", str(plan_id))
            self.update_plan_ui(plan_id)
        plan_name = POWER_PLANS.get(plan_id, ("?",))[0]
        if hasattr(self, "tray_icon"):
            self.tray_icon.showMessage(
                "Power Source Changed",
                f"{label}. Switched to {plan_name} plan.",
                QSystemTrayIcon.MessageIcon.Information,
                3000,
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Lighting Profile Export / Import
    # ─────────────────────────────────────────────────────────────────────────

    def export_profiles(self):
        import json
        profiles = self.settings.value("lighting_profiles", {}, type=dict)
        if not profiles:
            QMessageBox.information(self, "Export Profiles", "No profiles to export.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Lighting Profiles", "excalibur_profiles.json",
            "JSON Files (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "w") as f:
                json.dump(profiles, f, indent=2)
            self.show_status(f"Exported {len(profiles)} profile(s) to {path}")
        except Exception as e:
            self.show_status(f"Export failed: {e}", False)

    def import_profiles(self):
        import json
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Lighting Profiles", "",
            "JSON Files (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r") as f:
                incoming = json.load(f)
            if not isinstance(incoming, dict):
                raise ValueError("Invalid format")
            existing = self.settings.value("lighting_profiles", {}, type=dict)
            existing.update(incoming)
            self.settings.setValue("lighting_profiles", existing)
            self.populate_profiles()
            self.show_status(f"Imported {len(incoming)} profile(s)")
        except Exception as e:
            self.show_status(f"Import failed: {e}", False)

    # ─────────────────────────────────────────────────────────────────────────
    # Fan Curve Page
    # ─────────────────────────────────────────────────────────────────────────

    def create_fancurve_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        page_title = QLabel(tr("Fan Curve Editor"))
        page_title.setProperty("class", "title")
        header_layout.addWidget(page_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Info banner
        info = QLabel(
            tr("🖱  Click to add a point · Drag to move · Double-click to remove a point.\n"
            "The red dashed line shows the current live CPU temperature.\n"
            "Note: This curve is stored as a profile. Applying it requires a supported fan control daemon.")
        )
        info.setProperty("class", "muted")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Editor panel
        editor_panel = QFrame()
        editor_panel.setProperty("class", "panel")
        editor_layout = QVBoxLayout(editor_panel)
        editor_layout.setContentsMargins(20, 20, 20, 20)
        editor_layout.setSpacing(12)

        editor_title = QLabel(tr("CUSTOM FAN CURVE"))
        editor_title.setProperty("class", "section-title")
        editor_layout.addWidget(editor_title)

        self.fan_curve_editor = FanCurveEditor()
        # Load saved curve if present
        saved_curve = self.settings.value("fan_curve", None)
        if saved_curve and isinstance(saved_curve, list):
            try:
                parsed = [tuple(pt) for pt in saved_curve]
                self.fan_curve_editor.set_curve(parsed)
            except Exception:
                pass
        self.fan_curve_editor.curve_changed.connect(self._on_fan_curve_changed)
        editor_layout.addWidget(self.fan_curve_editor)

        # Curve table label
        self.fan_curve_table_label = QLabel()
        self.fan_curve_table_label.setStyleSheet(
            "font-family: monospace; font-size: 10px; color: #00f0ff;"
            " background: #0c0e12; padding: 8px; border-radius: 6px;"
        )
        self.fan_curve_table_label.setWordWrap(True)
        editor_layout.addWidget(self.fan_curve_table_label)
        self._refresh_fan_curve_table()

        layout.addWidget(editor_panel)

        # Buttons row
        btn_row = QHBoxLayout()

        reset_btn = QPushButton("Reset to Default")
        reset_btn.clicked.connect(self.fan_curve_editor.reset_default)

        save_btn = QPushButton("Save Curve")
        save_btn.setProperty("class", "apply-btn")
        save_btn.clicked.connect(self._save_fan_curve)

        export_btn = QPushButton("Export Curve…")
        export_btn.clicked.connect(self._export_fan_curve)

        import_btn = QPushButton("Import Curve…")
        import_btn.clicked.connect(self._import_fan_curve)

        btn_row.addWidget(reset_btn)
        btn_row.addStretch()
        btn_row.addWidget(import_btn)
        btn_row.addWidget(export_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def _on_fan_curve_changed(self, points):
        self._refresh_fan_curve_table()

    def _refresh_fan_curve_table(self):
        if not hasattr(self, "fan_curve_table_label"):
            return
        pts = self.fan_curve_editor.get_curve()
        lines = ["  Temp (°C)   Fan (%)"]
        lines.append("  " + "─" * 20)
        for t, p in pts:
            lines.append(f"  {t:>5}°C  →  {p:>3}%")
        self.fan_curve_table_label.setText("\n".join(lines))

    def _save_fan_curve(self):
        pts = self.fan_curve_editor.get_curve()
        self.settings.setValue("fan_curve", pts)
        self.show_status(f"Fan curve saved ({len(pts)} points)")

    def _export_fan_curve(self):
        import json
        pts = self.fan_curve_editor.get_curve()
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Fan Curve", "excalibur_fancurve.json", "JSON Files (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "w") as f:
                json.dump({"fan_curve": pts}, f, indent=2)
            self.show_status(f"Fan curve exported to {path}")
        except Exception as e:
            self.show_status(f"Export failed: {e}", False)

    def _import_fan_curve(self):
        import json
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Fan Curve", "", "JSON Files (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            pts = [tuple(p) for p in data.get("fan_curve", [])]
            if len(pts) < 2:
                raise ValueError("Need at least 2 points")
            self.fan_curve_editor.set_curve(pts)
            self._refresh_fan_curve_table()
            self.show_status(f"Fan curve imported ({len(pts)} points)")
        except Exception as e:
            self.show_status(f"Import failed: {e}", False)

    # ─────────────────────────────────────────────────────────────────────────
    # Session Stats helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _refresh_stats_labels(self):
        import time
        elapsed = int(time.time() - self.session_start_time)
        h, rem = divmod(elapsed, 3600)
        m, s = divmod(rem, 60)
        uptime_str = f"{h:02d}:{m:02d}:{s:02d}"

        def avg(lst): return int(sum(lst) / len(lst)) if lst else 0
        def peak(lst): return max(lst) if lst else 0

        self.stats_labels["uptime"].setText(uptime_str)
        self.stats_labels["avg_cpu_t"].setText(f"{avg(self.session_cpu_temps)}°C")
        self.stats_labels["peak_cpu_t"].setText(f"{peak(self.session_cpu_temps)}°C")
        self.stats_labels["avg_gpu_t"].setText(f"{avg(self.session_gpu_temps)}°C")
        self.stats_labels["peak_gpu_t"].setText(f"{peak(self.session_gpu_temps)}°C")
        self.stats_labels["avg_cpu_f"].setText(f"{avg(self.session_cpu_rpms):,} RPM")
        self.stats_labels["peak_cpu_f"].setText(f"{peak(self.session_cpu_rpms):,} RPM")
        self.stats_labels["plan_changes"].setText(str(self.session_plan_changes))

    def export_stats_csv(self):
        import csv
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Session Statistics", "excalibur_session_stats.csv",
            "CSV Files (*.csv)"
        )
        if not path:
            return
        
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Statistic", "Value"])
                
                # Uptime
                import time
                elapsed = int(time.time() - self.session_start_time)
                h, rem = divmod(elapsed, 3600)
                m, s = divmod(rem, 60)
                uptime_str = f"{h:02d}:{m:02d}:{s:02d}"
                writer.writerow(["Session Uptime", uptime_str])
                
                # CPU / GPU stats
                def avg(lst): return int(sum(lst) / len(lst)) if lst else 0
                def peak(lst): return max(lst) if lst else 0
                
                writer.writerow(["Avg CPU Temp", f"{avg(self.session_cpu_temps)} °C"])
                writer.writerow(["Peak CPU Temp", f"{peak(self.session_cpu_temps)} °C"])
                writer.writerow(["Avg GPU Temp", f"{avg(self.session_gpu_temps)} °C"])
                writer.writerow(["Peak GPU Temp", f"{peak(self.session_gpu_temps)} °C"])
                writer.writerow(["Avg CPU Fan Speed", f"{avg(self.session_cpu_rpms)} RPM"])
                writer.writerow(["Peak CPU Fan Speed", f"{peak(self.session_cpu_rpms)} RPM"])
                writer.writerow(["Avg GPU Fan Speed", f"{avg(self.session_gpu_rpms)} RPM"])
                writer.writerow(["Peak GPU Fan Speed", f"{peak(self.session_gpu_rpms)} RPM"])
                writer.writerow(["Power Plan Changes", self.session_plan_changes])
                
            self.show_status(f"Session stats exported to {path}")
        except Exception as e:
            self.show_status(f"CSV Export failed: {e}", False)

    # ─────────────────────────────────────────────────────────────────────────
    # Settings Page & Preferences
    # ─────────────────────────────────────────────────────────────────────────

    def create_settings_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        page_title = QLabel(tr("Settings & Preferences"))
        page_title.setProperty("class", "title")
        header_layout.addWidget(page_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 1. Preferences Panel
        pref_panel = QFrame()
        pref_panel.setProperty("class", "panel")
        pref_layout = QVBoxLayout(pref_panel)
        pref_layout.setContentsMargins(20, 20, 20, 20)
        pref_layout.setSpacing(15)
        
        pref_title = QLabel(tr("APPLICATION PREFERENCES"))
        pref_title.setProperty("class", "section-title")
        pref_layout.addWidget(pref_title)
        
        self.chk_autostart = QCheckBox(tr("Launch on system startup (Autostart)"))
        self.chk_autostart.setChecked(is_autostart_enabled())
        self.chk_autostart.toggled.connect(self.on_autostart_toggled)
        pref_layout.addWidget(self.chk_autostart)
        
        self.chk_close_tray = QCheckBox(tr("Close window to system tray"))
        self.chk_close_tray.setChecked(self.close_to_tray)
        self.chk_close_tray.toggled.connect(self.on_close_tray_toggled)
        pref_layout.addWidget(self.chk_close_tray)
        
        self.chk_start_minimized = QCheckBox(tr("Start minimized in system tray"))
        self.chk_start_minimized.setChecked(self.settings.value("start_minimized", False, type=bool))
        self.chk_start_minimized.toggled.connect(self.on_start_minimized_toggled)
        pref_layout.addWidget(self.chk_start_minimized)
        
        # Interval layout
        interval_layout = QHBoxLayout()
        interval_label = QLabel(tr("Monitoring Refresh Interval:"))
        self.interval_combo = QComboBox()
        self.interval_combo.addItems([tr("1 second"), tr("2 seconds"), tr("3 seconds"), tr("5 seconds")])
        
        curr_int = self.settings.value("refresh_interval", 1, type=int)
        int_text = tr(f"{curr_int} second") if curr_int == 1 else tr(f"{curr_int} seconds")
        index = self.interval_combo.findText(int_text)
        if index >= 0:
            self.interval_combo.setCurrentIndex(index)
        self.interval_combo.currentTextChanged.connect(self.on_interval_changed)
        
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_combo)
        interval_layout.addStretch()
        pref_layout.addLayout(interval_layout)
        
        layout.addWidget(pref_panel)
        
        # 2. Permissions Panel
        perm_panel = QFrame()
        perm_panel.setProperty("class", "panel")
        perm_layout = QVBoxLayout(perm_panel)
        perm_layout.setContentsMargins(20, 20, 20, 20)
        perm_layout.setSpacing(15)
        
        perm_title = QLabel(tr("SYSTEM PERMISSIONS"))
        perm_title.setProperty("class", "section-title")
        perm_layout.addWidget(perm_title)
        
        perm_desc = QLabel(
            tr("Udev rules allow running this control panel as a normal user without root privileges (sudo).\n"
            "If you see a permission warning at launch, install the rules below.")
        )
        perm_desc.setProperty("class", "muted")
        perm_desc.setWordWrap(True)
        perm_layout.addWidget(perm_desc)
        
        install_rules_btn = QPushButton("Install Udev Rules (Requires Privileges)")
        install_rules_btn.clicked.connect(self.install_udev_rules)
        perm_layout.addWidget(install_rules_btn)

        layout.addWidget(perm_panel)

        # ── 3. Custom Alert Thresholds ──────────────────────────────────────
        alert_panel = QFrame()
        alert_panel.setProperty("class", "panel")
        alert_layout = QVBoxLayout(alert_panel)
        alert_layout.setContentsMargins(20, 20, 20, 20)
        alert_layout.setSpacing(12)

        alert_title = QLabel(tr("ALERT THRESHOLDS"))
        alert_title.setProperty("class", "section-title")
        alert_layout.addWidget(alert_title)

        def make_threshold_row(label_text, setting_key, default, unit, lo, hi):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(200)
            from PyQt6.QtWidgets import QSlider, QSpinBox
            spin = QSpinBox()
            spin.setRange(lo, hi)
            spin.setValue(self.settings.value(setting_key, default, type=int))
            spin.setSuffix(f" {unit}")
            spin.setFixedWidth(110)
            spin.valueChanged.connect(lambda v, k=setting_key: self.settings.setValue(k, v))
            row.addWidget(lbl)
            row.addWidget(spin)
            row.addStretch()
            return row

        alert_layout.addLayout(make_threshold_row(
            tr("CPU Temperature Warning:"), "alert_cpu_temp", 85, "°C", 50, 110))
        alert_layout.addLayout(make_threshold_row(
            tr("GPU Temperature Warning:"), "alert_gpu_temp", 85, "°C", 50, 110))
        alert_layout.addLayout(make_threshold_row(
            tr("Fan Speed Warning:"), "alert_fan_rpm", 5500, "RPM", 1000, 7000))

        layout.addWidget(alert_panel)

        # ── 4. Power Schedule ───────────────────────────────────────────────
        sched_panel = QFrame()
        sched_panel.setProperty("class", "panel")
        sched_layout = QVBoxLayout(sched_panel)
        sched_layout.setContentsMargins(20, 20, 20, 20)
        sched_layout.setSpacing(12)

        sched_title = QLabel(tr("POWER PLAN SCHEDULE"))
        sched_title.setProperty("class", "section-title")
        sched_layout.addWidget(sched_title)

        sched_desc = QLabel(
            tr("Automatically switch power plans at specific times of day.\nFormat: HH:MM  →  Power Plan")
        )
        sched_desc.setProperty("class", "muted")
        sched_desc.setWordWrap(True)
        sched_layout.addWidget(sched_desc)

        self.sched_list = QLabel()
        self.sched_list.setWordWrap(True)
        self.sched_list.setStyleSheet("font-family: monospace; font-size: 11px; color: #00f0ff;"
                                      " background: #0c0e12; padding: 8px; border-radius: 6px;")
        sched_layout.addWidget(self.sched_list)
        self._refresh_sched_list()

        sched_add_row = QHBoxLayout()
        self.sched_time_edit = QComboBox()
        times = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
        self.sched_time_edit.addItems(times)
        self.sched_time_edit.setEditable(True)
        self.sched_time_edit.setFixedWidth(90)

        self.sched_plan_combo = QComboBox()
        for pid, pdata in POWER_PLANS.items():
            self.sched_plan_combo.addItem(f"{pdata[1]} {pdata[0]}", pid)
        self.sched_plan_combo.setFixedWidth(160)

        sched_add_btn = QPushButton(tr("Add"))
        sched_add_btn.setFixedWidth(70)
        sched_add_btn.clicked.connect(self._add_sched_entry)

        sched_del_btn = QPushButton(tr("Clear All"))
        sched_del_btn.setFixedWidth(90)
        sched_del_btn.clicked.connect(self._clear_sched_entries)

        sched_add_row.addWidget(QLabel(tr("Time:")))
        sched_add_row.addWidget(self.sched_time_edit)
        sched_add_row.addWidget(QLabel(tr("Plan:")))
        sched_add_row.addWidget(self.sched_plan_combo)
        sched_add_row.addWidget(sched_add_btn)
        sched_add_row.addWidget(sched_del_btn)
        sched_add_row.addStretch()
        sched_layout.addLayout(sched_add_row)

        layout.addWidget(sched_panel)

        # ── 5. Game Profile Launcher ────────────────────────────────────────
        game_panel = QFrame()
        game_panel.setProperty("class", "panel")
        game_layout = QVBoxLayout(game_panel)
        game_layout.setContentsMargins(20, 20, 20, 20)
        game_layout.setSpacing(12)

        game_title = QLabel(tr("GAME PROFILE LAUNCHER"))
        game_title.setProperty("class", "section-title")
        game_layout.addWidget(game_title)

        game_desc = QLabel(
            tr("Automatically switch power plan and keyboard color when a specific\nprocess (game/app) is detected as running.")
        )
        game_desc.setProperty("class", "muted")
        game_desc.setWordWrap(True)
        game_layout.addWidget(game_desc)

        self.game_list_label = QLabel()
        self.game_list_label.setWordWrap(True)
        self.game_list_label.setStyleSheet(
            "font-family: monospace; font-size: 11px; color: #00f0ff;"
            " background: #0c0e12; padding: 8px; border-radius: 6px;"
        )
        game_layout.addWidget(self.game_list_label)
        self._refresh_game_list()

        game_add_row = QHBoxLayout()
        self.game_exe_edit = QLineEdit()
        self.game_exe_edit.setPlaceholderText(tr("Process name (e.g. steam, cs2)"))
        self.game_exe_edit.setFixedWidth(170)

        self.game_plan_combo = QComboBox()
        for pid, pdata in POWER_PLANS.items():
            self.game_plan_combo.addItem(f"{pdata[1]} {pdata[0]}", pid)
        self.game_plan_combo.setFixedWidth(160)

        game_add_btn = QPushButton(tr("Add"))
        game_add_btn.setFixedWidth(70)
        game_add_btn.clicked.connect(self._add_game_profile)

        game_del_btn = QPushButton(tr("Clear All"))
        game_del_btn.setFixedWidth(90)
        game_del_btn.clicked.connect(self._clear_game_profiles)

        game_add_row.addWidget(QLabel(tr("Process:")))
        game_add_row.addWidget(self.game_exe_edit)
        game_add_row.addWidget(QLabel(tr("Plan:")))
        game_add_row.addWidget(self.game_plan_combo)
        game_add_row.addWidget(game_add_btn)
        game_add_row.addWidget(game_del_btn)
        game_add_row.addStretch()
        game_layout.addLayout(game_add_row)

        layout.addWidget(game_panel)

        # ── 6. External Monitor Detection ───────────────────────────────────
        mon_panel = QFrame()
        mon_panel.setProperty("class", "panel")
        mon_layout = QVBoxLayout(mon_panel)
        mon_layout.setContentsMargins(20, 20, 20, 20)
        mon_layout.setSpacing(12)

        mon_title = QLabel(tr("EXTERNAL MONITOR DETECTION"))
        mon_title.setProperty("class", "section-title")
        mon_layout.addWidget(mon_title)

        self.chk_monitor_detect = QCheckBox(tr("Auto-switch plan when external monitor connects/disconnects"))
        self.chk_monitor_detect.setChecked(
            self.settings.value("monitor_detect_enabled", False, type=bool))
        self.chk_monitor_detect.toggled.connect(
            lambda v: self.settings.setValue("monitor_detect_enabled", v))
        mon_layout.addWidget(self.chk_monitor_detect)

        mon_plan_row = QHBoxLayout()
        mon_plan_row.addWidget(QLabel(tr("On connect:")))
        self.mon_connect_combo = QComboBox()
        for pid, pdata in POWER_PLANS.items():
            self.mon_connect_combo.addItem(f"{pdata[1]} {pdata[0]}", pid)
        idx = self.mon_connect_combo.findData(
            self.settings.value("monitor_connect_plan", 1, type=int))
        if idx >= 0: self.mon_connect_combo.setCurrentIndex(idx)
        self.mon_connect_combo.currentIndexChanged.connect(
            lambda: self.settings.setValue("monitor_connect_plan",
                                           self.mon_connect_combo.currentData()))

        mon_plan_row.addWidget(self.mon_connect_combo)
        mon_plan_row.addSpacing(20)
        mon_plan_row.addWidget(QLabel(tr("On disconnect:")))
        self.mon_disconnect_combo = QComboBox()
        for pid, pdata in POWER_PLANS.items():
            self.mon_disconnect_combo.addItem(f"{pdata[1]} {pdata[0]}", pid)
        idx2 = self.mon_disconnect_combo.findData(
            self.settings.value("monitor_disconnect_plan", 4, type=int))
        if idx2 >= 0: self.mon_disconnect_combo.setCurrentIndex(idx2)
        self.mon_disconnect_combo.currentIndexChanged.connect(
            lambda: self.settings.setValue("monitor_disconnect_plan",
                                           self.mon_disconnect_combo.currentData()))
        mon_plan_row.addWidget(self.mon_disconnect_combo)
        mon_plan_row.addStretch()
        mon_layout.addLayout(mon_plan_row)

        layout.addWidget(mon_panel)

        # ── 7. AC & Battery Auto Power Plan ───────────────────────────────────
        ac_bat_panel = QFrame()
        ac_bat_panel.setProperty("class", "panel")
        ac_bat_layout = QVBoxLayout(ac_bat_panel)
        ac_bat_layout.setContentsMargins(20, 20, 20, 20)
        ac_bat_layout.setSpacing(12)

        ac_bat_title = QLabel(tr("AC & BATTERY AUTO POWER PLAN"))
        ac_bat_title.setProperty("class", "section-title")
        ac_bat_layout.addWidget(ac_bat_title)

        self.chk_ac_battery = QCheckBox(tr("Auto-switch power plan on AC connect/disconnect"))
        self.chk_ac_battery.setChecked(
            self.settings.value("ac_battery_enabled", False, type=bool))
        self.chk_ac_battery.toggled.connect(
            lambda v: self.settings.setValue("ac_battery_enabled", v))
        ac_bat_layout.addWidget(self.chk_ac_battery)

        ac_bat_row = QHBoxLayout()
        ac_bat_row.addWidget(QLabel(tr("On AC connected:")))
        self.ac_connect_combo = QComboBox()
        for pid, pdata in POWER_PLANS.items():
            self.ac_connect_combo.addItem(f"{pdata[1]} {pdata[0]}", pid)
        idx = self.ac_connect_combo.findData(
            self.settings.value("ac_connect_plan", 1, type=int))
        if idx >= 0: self.ac_connect_combo.setCurrentIndex(idx)
        self.ac_connect_combo.currentIndexChanged.connect(
            lambda: self.settings.setValue("ac_connect_plan",
                                           self.ac_connect_combo.currentData()))
        ac_bat_row.addWidget(self.ac_connect_combo)

        ac_bat_row.addSpacing(20)
        ac_bat_row.addWidget(QLabel(tr("On AC disconnected (Battery):")))
        self.ac_disconnect_combo = QComboBox()
        for pid, pdata in POWER_PLANS.items():
            self.ac_disconnect_combo.addItem(f"{pdata[1]} {pdata[0]}", pid)
        idx2 = self.ac_disconnect_combo.findData(
            self.settings.value("ac_disconnect_plan", 4, type=int))
        if idx2 >= 0: self.ac_disconnect_combo.setCurrentIndex(idx2)
        self.ac_disconnect_combo.currentIndexChanged.connect(
            lambda: self.settings.setValue("ac_disconnect_plan",
                                           self.ac_disconnect_combo.currentData()))
        ac_bat_row.addWidget(self.ac_disconnect_combo)
        ac_bat_row.addStretch()
        ac_bat_layout.addLayout(ac_bat_row)

        layout.addWidget(ac_bat_panel)

        # ── 8. TDP Power Limits ────────────────────────────────────────────────
        tdp_panel = QFrame()
        tdp_panel.setProperty("class", "panel")
        tdp_layout = QVBoxLayout(tdp_panel)
        tdp_layout.setContentsMargins(20, 20, 20, 20)
        tdp_layout.setSpacing(12)

        tdp_title = QLabel(tr("TDP POWER LIMITS"))
        tdp_title.setProperty("class", "section-title")
        tdp_layout.addWidget(tdp_title)

        tdp_desc = QLabel(
            tr("Limit CPU Power Consumption (TDP) in Watts. "
            "Requires ryzenadj (AMD) or Intel RAPL powercap interface.")
        )
        tdp_desc.setProperty("class", "muted")
        tdp_desc.setWordWrap(True)
        tdp_layout.addWidget(tdp_desc)

        tdp_row = QHBoxLayout()
        tdp_row.addWidget(QLabel(tr("Target TDP Limit:")))
        self.tdp_spin = QSpinBox()
        self.tdp_spin.setRange(5, 120)
        self.tdp_spin.setSuffix(" W")
        self.tdp_spin.setValue(self.settings.value("tdp_limit", 35, type=int))
        self.tdp_spin.setFixedWidth(100)
        tdp_row.addWidget(self.tdp_spin)

        apply_tdp_btn = QPushButton("Apply TDP Limit")
        apply_tdp_btn.setFixedWidth(140)
        apply_tdp_btn.clicked.connect(self.apply_tdp)
        tdp_row.addWidget(apply_tdp_btn)
        tdp_row.addStretch()
        tdp_layout.addLayout(tdp_row)

        layout.addWidget(tdp_panel)

        layout.addStretch()
        scroll.setWidget(tab)
        return scroll

    def on_autostart_toggled(self, checked):
        set_autostart(checked)
        self.show_status(tr("Autostart enabled") if checked else tr("Autostart disabled"))

    def on_close_tray_toggled(self, checked):
        self.close_to_tray = checked
        self.settings.setValue("close_to_tray", checked)
        self.show_status(tr("Close to tray enabled") if checked else tr("Close to tray disabled"))

    def on_start_minimized_toggled(self, checked):
        self.settings.setValue("start_minimized", checked)
        self.show_status(tr("Start minimized enabled") if checked else tr("Start minimized disabled"))

    def on_interval_changed(self, text):
        try:
            val = int(text.split()[0])
            self.timer.setInterval(val * 1000)
            self.settings.setValue("refresh_interval", val)
            self.show_status(tr(f"Refresh interval set to {val}s"))
        except ValueError:
            pass

    # ── Power Schedule helpers ──────────────────────────────────────────────
    def _refresh_sched_list(self):
        if not hasattr(self, 'sched_list'):
            return
        schedule = self.settings.value("power_schedule", [], type=list)
        if not schedule:
            self.sched_list.setText(tr("No entries. Add one below."))
        else:
            lines = []
            for e in sorted(schedule, key=lambda x: x.get("time", "")):
                plan_name = POWER_PLANS.get(int(e.get("plan", 3)), ("?",))[0]
                lines.append(f"  {e['time']}  →  {plan_name}")
            self.sched_list.setText("\n".join(lines))

    def _add_sched_entry(self):
        time_str = self.sched_time_edit.currentText().strip()
        plan_id = self.sched_plan_combo.currentData()
        if not time_str or plan_id is None:
            return
        schedule = list(self.settings.value("power_schedule", [], type=list))
        # Remove duplicate time
        schedule = [e for e in schedule if e.get("time") != time_str]
        schedule.append({"time": time_str, "plan": plan_id})
        self.settings.setValue("power_schedule", schedule)
        self._refresh_sched_list()
        self.show_status(f"Schedule entry added: {time_str}")

    def _clear_sched_entries(self):
        self.settings.setValue("power_schedule", [])
        self._refresh_sched_list()
        self.show_status(tr("Schedule cleared"))

    # ── Game Profile helpers ────────────────────────────────────────────────
    def _refresh_game_list(self):
        if not hasattr(self, 'game_list_label'):
            return
        profiles = self.settings.value("game_profiles", {}, type=dict)
        if not profiles:
            self.game_list_label.setText(tr("No game profiles. Add one below."))
        else:
            lines = []
            for exe, cfg in profiles.items():
                plan_name = POWER_PLANS.get(int(cfg.get("plan", 3)), ("?",))[0]
                lines.append(f"  {exe}  →  {plan_name}")
            self.game_list_label.setText("\n".join(lines))

    def _add_game_profile(self):
        exe = self.game_exe_edit.text().strip().lower()
        plan_id = self.game_plan_combo.currentData()
        if not exe:
            return
        profiles = dict(self.settings.value("game_profiles", {}, type=dict))
        profiles[exe] = {"plan": plan_id}
        self.settings.setValue("game_profiles", profiles)
        self.game_exe_edit.clear()
        self._refresh_game_list()
        self.show_status(f"Game profile added: {exe}")

    def _clear_game_profiles(self):
        self.settings.setValue("game_profiles", {})
        self._refresh_game_list()
        self.show_status(tr("Game profiles cleared"))

    def install_udev_rules(self):
        import subprocess
        rules_path = "/etc/udev/rules.d/99-excalibur.rules"
        if os.getuid() == 0:
            try:
                Path(rules_path).write_text(UDEV_RULES_CONTENT)
                subprocess.run(["udevadm", "control", "--reload-rules"], check=True)
                subprocess.run(["udevadm", "trigger"], check=True)
                self.show_status("Udev rules installed successfully!")
            except Exception as e:
                self.show_status(f"Error: {e}", False)
        else:
            import tempfile
            try:
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                    f.write(UDEV_RULES_CONTENT)
                    temp_name = f.name
                
                cmd = [
                    "pkexec", "sh", "-c",
                    f"cp {temp_name} {rules_path} && chmod 644 {rules_path} && udevadm control --reload-rules && udevadm trigger"
                ]
                res = subprocess.run(cmd, capture_output=True, text=True)
                os.unlink(temp_name)
                
                if res.returncode == 0:
                    self.show_status("Udev rules installed! Please re-login/reboot.")
                else:
                    self.show_status("Installation cancelled or failed.", False)
            except Exception as e:
                self.show_status(f"Error: {e}", False)

    def apply_tdp(self):
        watts = self.tdp_spin.value()
        import subprocess
        import shutil
        
        # Check for AMD (ryzenadj)
        ryzenadj_path = shutil.which("ryzenadj")
        if ryzenadj_path:
            cmd = [ryzenadj_path, f"--stapm-limit={watts}000", f"--fast-limit={watts}000", f"--slow-limit={watts}000"]
            if os.getuid() != 0:
                cmd = ["pkexec"] + cmd
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if res.returncode == 0:
                    self.show_status(f"TDP limit set to {watts}W via ryzenadj")
                    self.settings.setValue("tdp_limit", watts)
                    return
                else:
                    self.show_status(f"Failed to set TDP: {res.stderr.strip()}", False)
                    return
            except Exception as e:
                self.show_status(f"TDP apply error: {e}", False)
                return
        
        # Check for Intel RAPL via sysfs
        rapl_dir = Path("/sys/class/powercap/intel-rapl:0")
        if rapl_dir.exists():
            limit_file = rapl_dir / "constraint_0_power_limit_uw"
            uw = watts * 1000000
            if os.getuid() == 0:
                try:
                    limit_file.write_text(str(uw))
                    self.show_status(f"TDP limit set to {watts}W via Intel RAPL")
                    self.settings.setValue("tdp_limit", watts)
                    return
                except Exception as e:
                    self.show_status(f"RAPL write error: {e}", False)
                    return
            else:
                cmd = ["pkexec", "sh", "-c", f"echo {uw} > {limit_file}"]
                try:
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if res.returncode == 0:
                        self.show_status(f"TDP limit set to {watts}W via Intel RAPL (authenticated)")
                        self.settings.setValue("tdp_limit", watts)
                        return
                      
                    else:
                        self.show_status("TDP write cancelled or failed", False)
                        return
                except Exception as e:
                    self.show_status(f"TDP Apply error: {e}", False)
                    return
        
        self.show_status("TDP control not supported (ryzenadj or intel-rapl not found)", False)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Excalibur Control Center CLI & GUI")
    parser.add_argument("--minimized", "-m", action="store_true", help="Start minimized in system tray")
    parser.add_argument("--set-plan", type=int, choices=[1, 2, 3, 4], help="Set power plan ID (1: High Perf, 2: Gaming, 3: Office, 4: Battery Boost)")
    parser.add_argument("--set-color", type=str, help="Set RGB color hex (e.g. FF0000 or 'random')")
    parser.add_argument("--zone", type=str, choices=["left", "middle", "right", "corners", "all"], default="all", help="Target LED zone for color/mode/brightness (default: all)")
    parser.add_argument("--set-mode", type=str, help="Set lighting effect mode (e.g. static, blink, fade, heartbeat, rainbow, wave)")
    parser.add_argument("--set-brightness", type=int, choices=[0, 1, 2], help="Set brightness level (0: Off, 1: Medium, 2: Full)")
    parser.add_argument("--get-temp", action="store_true", help="Print CPU and GPU temperatures and exit")
    parser.add_argument("--get-fan", action="store_true", help="Print CPU and GPU fan RPMs and exit")
    
    args, unknown = parser.parse_known_args()
    
    if args.get_temp:
        cpu_t, gpu_t = get_temperatures()
        print(f"CPU Temperature: {cpu_t}°C")
        print(f"GPU Temperature: {gpu_t}°C")
        sys.exit(0)
        
    if args.get_fan:
        hw_path = find_hwmon_path()
        if hw_path:
            cpu_raw = _read(f"{hw_path}/fan1_input")
            gpu_raw = _read(f"{hw_path}/fan2_input")
            cpu_rpm = int(cpu_raw) if cpu_raw and cpu_raw.isdigit() else 0
            gpu_rpm = int(gpu_raw) if gpu_raw and gpu_raw.isdigit() else 0
            print(f"CPU Fan Speed: {cpu_rpm} RPM")
            print(f"GPU Fan Speed: {gpu_rpm} RPM")
        else:
            print("Error: hwmon device not found (driver not loaded)")
        sys.exit(0)
        
    if (args.set_plan is not None or 
        args.set_color is not None or 
        args.set_mode is not None or 
        args.set_brightness is not None):
        
        if args.set_plan is not None:
            hw_path = find_hwmon_path()
            if hw_path:
                ok, err = _write(f"{hw_path}/pwm1", str(args.set_plan))
                if ok:
                    print(f"Power plan successfully set to {args.set_plan} ({POWER_PLANS[args.set_plan][0]})")
                else:
                    print(f"Error setting power plan: {err}")
            else:
                print("Error: hwmon device not found (driver not loaded)")
                
        if args.set_color is not None or args.set_mode is not None or args.set_brightness is not None:
            zone = args.zone.lower()
            zones_to_write = list(ZONE_NAMES) if zone == "all" else [zone]
            
            if args.set_color is not None:
                color = args.set_color.upper().lstrip("#")
                if color == "RANDOM":
                    import random
                    color = f"{random.randint(0, 0xFFFFFF):06X}"
                for z in zones_to_write:
                    ok, err = _write(led_path(z, "color"), color)
                    if ok:
                        print(f"Set color of zone '{z}' to #{color}")
                    else:
                        print(f"Error setting color for zone '{z}': {err}")
                        
            if args.set_mode is not None:
                mode = args.set_mode.lower().strip()
                for z in zones_to_write:
                    ok, err = _write(led_path(z, "mode"), mode)
                    if ok:
                        print(f"Set mode of zone '{z}' to {mode}")
                    else:
                        print(f"Error setting mode for zone '{z}': {err}")
                        
            if args.set_brightness is not None:
                bright = args.set_brightness
                if zone == "all":
                    ok, err = _write(led_path("left", "brightness"), str(bright))
                    if ok:
                        _write(led_path("corners", "brightness"), str(bright))
                        print(f"Set brightness of all zones to {bright}")
                    else:
                        print(f"Error setting brightness: {err}")
                elif zone == "corners":
                    ok, err = _write(led_path("corners", "brightness"), str(bright))
                    if ok:
                        print(f"Set brightness of corners to {bright}")
                    else:
                        print(f"Error setting brightness of corners: {err}")
                else:
                    print("Note: Brightness can only be set for 'all' or 'corners' zones in sysfs interface.")
        sys.exit(0)

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
    start_min = QSettings("LupuS", "ExcaliburControlPanel").value("start_minimized", False, type=bool)
    if "--minimized" not in sys.argv and "-m" not in sys.argv and not start_min:
        window.show()
        
    sys.exit(app.exec())
