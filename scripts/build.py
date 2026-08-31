#!/usr/bin/env python3
"""Build a standalone Windows executable for the Restaurant POS System.

Usage (from the project root):
    python scripts/build.py

Requires PyInstaller (pip install pyinstaller) and the runtime dependencies
listed in requirements.txt.
"""
import os
import shutil
import subprocess
import sys

APP_NAME = "RestaurantPOS"

# Resolve important paths relative to the project root, regardless of where
# this script is invoked from.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
ENTRY_POINT = os.path.join(PROJECT_ROOT, "restaurant_pos", "app.py")
VERSION_FILE = os.path.join(SCRIPT_DIR, "version_info.txt")
CONFIG_FILE = os.path.join(PROJECT_ROOT, "restaurant_pos", "core", "config.py")
# The .spec file carries the Tcl/Tk 9.0 data-collection logic required for
# Python 3.14+ (see RestaurantPOS.spec). Build from it so the executable
# bundles tkinter correctly and does not fail with a missing "_tcl_data".
SPEC_FILE = os.path.join(PROJECT_ROOT, f"{APP_NAME}.spec")


def clean_artifacts():
    """Remove build artifacts from previous runs."""
    for path in ("build", "dist"):
        full = os.path.join(PROJECT_ROOT, path)
        if os.path.isdir(full):
            shutil.rmtree(full, ignore_errors=True)

    for root, dirs, _ in os.walk(PROJECT_ROOT):
        for directory in list(dirs):
            if directory == "__pycache__":
                shutil.rmtree(os.path.join(root, directory), ignore_errors=True)
                dirs.remove(directory)


def build_command():
    """Assemble the PyInstaller command.

    Prefer the .spec file when present, since it contains the Tcl/Tk data
    collection needed for Python 3.14+. Fall back to a direct command-line
    build only if the spec is missing.
    """
    if os.path.exists(SPEC_FILE):
        return [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm",
            "--clean",
            SPEC_FILE,
        ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={APP_NAME}",
        f"--version-file={VERSION_FILE}",
        f"--paths={PROJECT_ROOT}",
        f"--add-data={CONFIG_FILE}{os.pathsep}restaurant_pos/core",
    ]

    for module in (
        "tkinter", "reportlab.pdfgen", "reportlab.lib",
        "win32print", "win32api", "wmi",
    ):
        cmd += ["--hidden-import", module]

    cmd.append(ENTRY_POINT)
    return cmd


def main():
    os.chdir(PROJECT_ROOT)

    clean_artifacts()

    try:
        subprocess.run(build_command(), check=True)
    except FileNotFoundError:
        print("PyInstaller is not installed. Run: pip install pyinstaller")
        return 1
    except subprocess.CalledProcessError as error:
        print(f"Build failed with exit code {error.returncode}")
        return 1

    exe_path = os.path.join(PROJECT_ROOT, "dist", f"{APP_NAME}.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"Build complete: {exe_path} ({size_mb:.1f} MB)")
        return 0

    print("Build finished but the executable was not found in dist/.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
