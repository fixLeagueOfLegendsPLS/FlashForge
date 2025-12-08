#!/usr/bin/env python3
"""
FlashForge Build Script
Builds standalone executables using PyInstaller.

Usage:
    python build.py          # Build for current platform
    python build.py --onedir # Build as directory instead of single file
    python build.py --debug  # Build with console for debugging
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Build configuration
APP_NAME = "FlashForge"
APP_VERSION = "1.0.0"
MAIN_SCRIPT = "src/main.py"

# PyInstaller options
PYINSTALLER_OPTS = [
    "--name", APP_NAME,
    "--windowed",  # No console window
    "--noconfirm",  # Don't ask for confirmation
    "--clean",  # Clean cache
]

# Data files to include
DATA_FILES = [
    ("assets", "assets"),
]

# Hidden imports that PyInstaller might miss
HIDDEN_IMPORTS = [
    "customtkinter",
    "PIL",
    "sqlalchemy",
    "sqlalchemy.orm",
]


def get_platform():
    """Get current platform name."""
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "darwin":
        return "macos"
    else:
        return "linux"


def clean_build():
    """Clean previous build artifacts."""
    dirs_to_clean = ["build", "dist", f"{APP_NAME}.spec"]

    for d in dirs_to_clean:
        path = Path(d)
        if path.exists():
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)
            print(f"Cleaned: {d}")


def build_app(onefile=True, debug=False):
    """Build the application."""
    print(f"\n{'='*50}")
    print(f"Building {APP_NAME} v{APP_VERSION}")
    print(f"Platform: {get_platform()}")
    print(f"{'='*50}\n")

    # Clean previous builds
    clean_build()

    # Build PyInstaller command
    cmd = ["pyinstaller"]
    cmd.extend(PYINSTALLER_OPTS)

    # One file or directory
    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    # Debug mode
    if debug:
        cmd.remove("--windowed")
        cmd.append("--console")

    # Add data files
    for src, dst in DATA_FILES:
        if Path(src).exists():
            cmd.extend(["--add-data", f"{src}{os.pathsep}{dst}"])

    # Add hidden imports
    for imp in HIDDEN_IMPORTS:
        cmd.extend(["--hidden-import", imp])

    # Platform-specific options
    platform = get_platform()

    if platform == "windows":
        # Windows icon
        icon_path = Path("assets/icons/app.ico")
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])

    elif platform == "macos":
        # macOS icon
        icon_path = Path("assets/icons/app.icns")
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])

        # macOS bundle identifier
        cmd.extend(["--osx-bundle-identifier", "com.flashforge.app"])

    elif platform == "linux":
        # Linux icon
        icon_path = Path("assets/icons/app.png")
        if icon_path.exists():
            cmd.extend(["--icon", str(icon_path)])

    # Add main script
    cmd.append(MAIN_SCRIPT)

    print(f"Running: {' '.join(cmd)}\n")

    # Run PyInstaller
    try:
        subprocess.run(cmd, check=True)
        print(f"\n{'='*50}")
        print("Build successful!")
        print(f"Output: dist/{APP_NAME}")
        print(f"{'='*50}\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        return False


def create_portable():
    """Create portable version with data folder."""
    platform = get_platform()
    dist_path = Path("dist")

    if platform == "windows":
        exe_name = f"{APP_NAME}.exe"
    else:
        exe_name = APP_NAME

    exe_path = dist_path / exe_name

    if not exe_path.exists():
        print("Executable not found. Run build first.")
        return False

    # Create portable folder
    portable_dir = dist_path / f"{APP_NAME}_Portable"
    portable_dir.mkdir(exist_ok=True)

    # Copy executable
    shutil.copy2(exe_path, portable_dir / exe_name)

    # Create data folder for portable mode
    data_dir = portable_dir / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / ".gitkeep").touch()

    # Create README for portable
    readme = portable_dir / "README.txt"
    readme.write_text(f"""
{APP_NAME} v{APP_VERSION} - Portable Version

This is the portable version of {APP_NAME}.
All your data will be stored in the 'data' folder next to the executable.

To use:
1. Run {exe_name}
2. Your flashcards and settings will be saved in the 'data' folder

You can move this entire folder anywhere and your data will follow.
""")

    print(f"Portable version created: {portable_dir}")
    return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description=f"Build {APP_NAME}")
    parser.add_argument("--onedir", action="store_true",
                        help="Build as directory instead of single file")
    parser.add_argument("--debug", action="store_true",
                        help="Build with console for debugging")
    parser.add_argument("--portable", action="store_true",
                        help="Create portable version after build")
    parser.add_argument("--clean", action="store_true",
                        help="Only clean build artifacts")

    args = parser.parse_args()

    if args.clean:
        clean_build()
        return

    success = build_app(
        onefile=not args.onedir,
        debug=args.debug
    )

    if success and args.portable:
        create_portable()


if __name__ == "__main__":
    main()
