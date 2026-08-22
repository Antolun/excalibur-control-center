#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# COMAR System.Package script for excalibur-control-center
#

import os

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    # 1. Register, build, and install DKMS module for kernel updates
    try:
        os.system("dkms add -m excalibur-control-center -v 1.0.0 2>/dev/null || true")
        os.system("dkms build -m excalibur-control-center -v 1.0.0 2>/dev/null || true")
        os.system("dkms install -m excalibur-control-center -v 1.0.0 --force 2>/dev/null || true")
    except:
        pass

    # 2. Update kernel module dependencies
    try:
        os.system("depmod -a 2>/dev/null || true")
    except:
        pass

    # 3. Reload udev rules for non-root hardware access
    try:
        os.system("udevadm control --reload-rules 2>/dev/null || true")
        os.system("udevadm trigger 2>/dev/null || true")
    except:
        pass

    # 4. Automatically load kernel driver
    try:
        os.system("modprobe excalibur 2>/dev/null || true")
    except:
        pass

def preRemove():
    # Unload driver before removal
    try:
        os.system("rmmod excalibur 2>/dev/null || true")
    except:
        pass

    # Unregister from DKMS
    try:
        os.system("dkms remove -m excalibur-control-center -v 1.0.0 --all 2>/dev/null || true")
    except:
        pass

def postRemove():
    # Update module dependencies and reload udev
    try:
        os.system("depmod -a 2>/dev/null || true")
        os.system("udevadm control --reload-rules 2>/dev/null || true")
    except:
        pass
