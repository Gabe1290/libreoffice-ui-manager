#!/usr/bin/env bash
#
# Install the standalone LOUIM development macro into the LibreOffice user
# profile so it can be run from Writer without packaging an .oxt.
#
# After running this, restart LibreOffice (or close all windows) and use:
#   Tools > Macros > Organize Macros > Python...
#   -> My Macros > louim_hello > hello -> Run
#
# Re-run this script any time you edit tools/dev-macro/louim_hello.py.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MACRO_SRC="${SCRIPT_DIR}/dev-macro/louim_hello.py"

# Default LibreOffice user profile location on Linux. Override with LO_USER_DIR.
LO_USER_DIR="${LO_USER_DIR:-${HOME}/.config/libreoffice/4/user}"
DEST_DIR="${LO_USER_DIR}/Scripts/python"

if [[ ! -f "${MACRO_SRC}" ]]; then
    echo "error: macro source not found: ${MACRO_SRC}" >&2
    exit 1
fi

if [[ ! -d "${LO_USER_DIR}" ]]; then
    echo "error: LibreOffice user profile not found: ${LO_USER_DIR}" >&2
    echo "       launch LibreOffice once, or set LO_USER_DIR to the right path." >&2
    exit 1
fi

mkdir -p "${DEST_DIR}"
cp "${MACRO_SRC}" "${DEST_DIR}/"

echo "Installed: ${DEST_DIR}/louim_hello.py"
echo "Restart LibreOffice, then run via Tools > Macros > Organize Macros > Python..."
