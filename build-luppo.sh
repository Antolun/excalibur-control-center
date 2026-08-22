#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo " Excalibur Control Center — Luppo Package Builder"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export EXCALIBUR_CONTROL_CENTER_SRC_DIR="${SCRIPT_DIR}"
cd "${SCRIPT_DIR}"

# Detect compiler for module build if kernel headers are present
MAKE_FLAGS=""
if grep -q "clang" /proc/version 2>/dev/null; then
    MAKE_FLAGS="CC=clang LLVM=1 LLVM_IAS=1"
fi

echo "[1/2] Building kernel module..."
if [ -d "/lib/modules/$(uname -r)/build" ]; then
    make ${MAKE_FLAGS} || echo "Warning: Kernel module pre-compilation failed, DKMS will handle it on install."
else
    echo "Kernel headers not found for running kernel. DKMS source tree will be packaged."
fi

echo "[2/2] Creating Luppo package (.luppo)..."
if command -v luppo &>/dev/null; then
    luppo build lopec.xml --no-sandbox --ignore-dependency
else
    echo "Error: luppo command not found!"
    exit 1
fi

echo "Locating generated .luppo package..."
LUPPO_FILE=$(find . /var/luppo /tmp -name "excalibur-control-center-*.luppo" 2>/dev/null | head -n 1 || true)

if [ -n "${LUPPO_FILE}" ] && [ -f "${LUPPO_FILE}" ]; then
    TARGET_PATH="${SCRIPT_DIR}/$(basename "${LUPPO_FILE}")"
    if [ "${LUPPO_FILE}" != "${TARGET_PATH}" ]; then
        cp -f "${LUPPO_FILE}" "${TARGET_PATH}"
    fi
    
    if [ -n "${SUDO_USER:-}" ]; then
        chown "${SUDO_USER}:" "${TARGET_PATH}" 2>/dev/null || true
    fi
    
    echo ""
    echo "=========================================="
    echo " SUCCESS! .luppo package saved to:"
    echo " ${TARGET_PATH}"
    echo "=========================================="
else
    echo "Error: .luppo package file could not be found."
    exit 1
fi
