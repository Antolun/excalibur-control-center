#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Actions file for Luppo package builder (excalibur-control-center)
#

import os
from luppo.actionsapi import shelltools
from luppo.actionsapi import luppotools
from luppo.actionsapi import get

WorkDir = "."
NoStrip = ["/lib/modules"]

def setup():
    pass

def build():
    pass

def install():
    src_dir = os.environ.get("EXCALIBUR_CONTROL_CENTER_SRC_DIR", os.getcwd())
    if not os.path.isfile(os.path.join(src_dir, "excalibur.c")):
        candidates = [
            src_dir,
            os.getcwd(),
        ]
        for c in candidates:
            if os.path.isfile(os.path.join(c, "excalibur.c")):
                src_dir = c
                break

    install_dir = get.installDIR()

    # 1. Install DKMS source tree (/usr/src/excalibur-control-center-1.0.0/)
    dkms_dir = os.path.join(install_dir, "usr", "src", "excalibur-control-center-1.0.0")
    shelltools.makedirs(dkms_dir)
    for f in ["excalibur.c", "Makefile", "Kconfig", "dkms.conf"]:
        file_path = os.path.join(src_dir, f)
        if os.path.isfile(file_path):
            shelltools.copy(file_path, os.path.join(dkms_dir, f))

    # 2. Install precompiled kernel module if available
    ko_file = os.path.join(src_dir, "excalibur.ko")
    if os.path.isfile(ko_file):
        kver = get.curKERNEL() if hasattr(get, "curKERNEL") and get.curKERNEL() else os.uname().release
        mod_dir = os.path.join(install_dir, "lib", "modules", kver, "extra")
        shelltools.makedirs(mod_dir)
        shelltools.copy(ko_file, os.path.join(mod_dir, "excalibur.ko"))

    # 3. Install udev rules
    udev_dir = os.path.join(install_dir, "etc", "udev", "rules.d")
    shelltools.makedirs(udev_dir)
    udev_file = os.path.join(udev_dir, "99-excalibur.rules")
    udev_content = """# excalibur-control-center udev rules
# Grants write access to LED zones and power plan for wheel/sudo group members,
# allowing the control panel to run without sudo.

# Keyboard LED zones
SUBSYSTEM=="leds", KERNEL=="excalibur*", \\
    RUN+="/bin/sh -c 'chown root:wheel /sys%p/brightness /sys%p/color /sys%p/mode /sys%p/raw 2>/dev/null; chmod g+w /sys%p/brightness /sys%p/color /sys%p/mode /sys%p/raw 2>/dev/null'", \\
    RUN+="/bin/sh -c 'chown root:sudo  /sys%p/brightness /sys%p/color /sys%p/mode /sys%p/raw 2>/dev/null; chmod g+w /sys%p/brightness /sys%p/color /sys%p/mode /sys%p/raw 2>/dev/null'"

# hwmon (fan speeds + power plan)
SUBSYSTEM=="hwmon", ATTR{name}=="excalibur_control_center", \\
    RUN+="/bin/sh -c 'chown root:wheel /sys%p/pwm1 /sys%p/fan1_input /sys%p/fan2_input 2>/dev/null; chmod g+rw /sys%p/pwm1 2>/dev/null'", \\
    RUN+="/bin/sh -c 'chown root:sudo  /sys%p/pwm1 /sys%p/fan1_input /sys%p/fan2_input 2>/dev/null; chmod g+rw /sys%p/pwm1 2>/dev/null'"
"""
    with open(udev_file, "w") as uf:
        uf.write(udev_content)

    # 4. Install modules-load.d entry
    modules_load_dir = os.path.join(install_dir, "etc", "modules-load.d")
    shelltools.makedirs(modules_load_dir)
    with open(os.path.join(modules_load_dir, "excalibur.conf"), "w") as mf:
        mf.write("excalibur\n")

    # 5. Install Control Panel into /opt/excalibur-panel
    panel_dest_dir = os.path.join(install_dir, "opt", "excalibur-panel")
    shelltools.makedirs(panel_dest_dir)
    panel_src = os.path.join(src_dir, "control-panel.py")
    if os.path.isfile(panel_src):
        shelltools.copy(panel_src, os.path.join(panel_dest_dir, "control-panel.py"))
        os.chmod(os.path.join(panel_dest_dir, "control-panel.py"), 0o644)

    logo_src = os.path.join(src_dir, "logo.png")
    if os.path.isfile(logo_src):
        shelltools.copy(logo_src, os.path.join(panel_dest_dir, "logo.png"))
        os.chmod(os.path.join(panel_dest_dir, "logo.png"), 0o644)

        # Also copy to icons dir for system desktop themes
        icon_dir = os.path.join(install_dir, "usr", "share", "icons", "hicolor", "128x128", "apps")
        shelltools.makedirs(icon_dir)
        shelltools.copy(logo_src, os.path.join(icon_dir, "excalibur-control-center.png"))

    # 6. Install launcher script /usr/bin/excalibur-panel
    bin_dir = os.path.join(install_dir, "usr", "bin")
    shelltools.makedirs(bin_dir)
    launcher_file = os.path.join(bin_dir, "excalibur-panel")
    with open(launcher_file, "w") as lf:
        lf.write("#!/bin/bash\n# Excalibur Control Panel launcher\nexec python3 /opt/excalibur-panel/control-panel.py \"$@\"\n")
    os.chmod(launcher_file, 0o755)

    # 7. Install Desktop Entry
    desktop_dir = os.path.join(install_dir, "usr", "share", "applications")
    shelltools.makedirs(desktop_dir)
    desktop_file = os.path.join(desktop_dir, "excalibur-control-center.desktop")
    desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=Excalibur Control Center
GenericName=Excalibur WMI Driver Controller
Comment=RGB lighting, fan monitoring and power plan control for Excalibur laptops
Exec=/usr/bin/excalibur-panel
Icon=/opt/excalibur-panel/logo.png
Terminal=false
Categories=System;HardwareSettings;
Keywords=excalibur;rgb;keyboard;fan;laptop;
StartupNotify=false
"""
    with open(desktop_file, "w") as df:
        df.write(desktop_content)

    # 8. Install Documentation
    for doc in ["README.md", "LICENSE", "MAINTAINERS", "dkms.conf"]:
        doc_path = os.path.join(src_dir, doc)
        if os.path.isfile(doc_path):
            luppotools.dodoc(doc_path)
