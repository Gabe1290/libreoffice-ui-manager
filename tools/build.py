#!/usr/bin/env python3
"""
Build script for LibreOffice UI Manager.

Creates an installable .oxt package in dist/.
"""

from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
EXTENSION = ROOT / "extension"
TEMPLATES = ROOT / "templates"
DIST = ROOT / "dist"
BUILD = ROOT / "build" / "louim"
VERSION = "0.0.1"


def clean():
    if BUILD.exists():
        shutil.rmtree(BUILD)
    DIST.mkdir(exist_ok=True)
    BUILD.mkdir(parents=True)


def copy_files():
    shutil.copytree(EXTENSION, BUILD, dirs_exist_ok=True)
    shutil.copytree(SRC / "louim", BUILD / "python" / "louim", dirs_exist_ok=True)
    shutil.copytree(TEMPLATES, BUILD / "templates", dirs_exist_ok=True)


def make_oxt():
    # Stable filename (no version): LibreOffice deploys the .oxt into a folder
    # named after the file, and the menu's vnd.sun.star.script URL references
    # that folder name. Keeping it constant means the URL survives version bumps.
    # The real version lives in extension/description.xml.
    oxt_path = DIST / "louim.oxt"

    if oxt_path.exists():
        oxt_path.unlink()

    with zipfile.ZipFile(oxt_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in BUILD.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(BUILD))

    print(f"Created {oxt_path}")


def main():
    clean()
    copy_files()
    make_oxt()


if __name__ == "__main__":
    main()
