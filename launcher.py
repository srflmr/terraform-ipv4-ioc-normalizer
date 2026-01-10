#!/usr/bin/env python3
"""
🚀 Terraform IPv4 Normalizer - AUTO VENV LAUNCHER
Cross-platform launcher for Windows, Linux, and macOS

Usage:
    python launcher.py      # Windows (CMD/PowerShell)
    python3 launcher.py     # Linux/macOS
"""
import os
import sys
import subprocess
from pathlib import Path
import platform


class LauncherError(Exception):
    """Custom exception for launcher errors."""
    pass


def get_platform_info():
    """Get platform information and return executable details."""
    system = platform.system()
    is_windows = system == "Windows"
    is_linux = system == "Linux"
    is_macos = system == "Darwin"

    return {
        "system": system,
        "is_windows": is_windows,
        "is_linux": is_linux,
        "is_macos": is_macos,
        "scripts_dir": "Scripts" if is_windows else "bin",
        "python_exe": "python.exe" if is_windows else "python",
        "pip_exe": "pip.exe" if is_windows else "pip",
    }


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        raise LauncherError("Python version too old")
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def check_app_file():
    """Check if app.py exists in the current directory."""
    app_file = Path("app.py")
    if not app_file.exists():
        print("❌ 'app.py' not found in current directory!")
        print("💡 Make sure you're running this from the project root.")
        raise LauncherError("app.py not found")
    return app_file


def create_virtualenv(venv_dir, platform_info):
    """Create virtual environment if it doesn't exist."""
    if venv_dir.exists():
        print("♻️  Virtual environment already exists")
        return

    print("📦 Creating virtual environment...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "venv", "--clear", str(venv_dir)]
        )
        print("✅ Virtual environment created")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        raise LauncherError("Virtual environment creation failed")


def get_executable_paths(venv_dir, platform_info):
    """Get paths to Python and pip executables in the virtual environment."""
    scripts_dir = venv_dir / platform_info["scripts_dir"]
    python_exe = scripts_dir / platform_info["python_exe"]
    pip_exe = scripts_dir / platform_info["pip_exe"]

    # Verify Python executable exists
    if not python_exe.exists():
        raise LauncherError(f"Python executable not found: {python_exe}")

    # pip may not exist in fresh venv - use python -m pip instead
    return python_exe, pip_exe


def ensure_pip_installed(python_exe, platform_info):
    """Ensure pip is installed in the virtual environment."""
    print("🔍 Ensuring pip is available...")

    try:
        # Try to run pip as module
        subprocess.check_call(
            [str(python_exe), "-m", "pip", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✅ Pip is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # pip not available, try to install it
        print("⚠️  Pip not found, installing ensurepip...")
        try:
            subprocess.check_call([str(python_exe), "-m", "ensurepip", "--upgrade"])
            print("✅ Pip installed via ensurepip")
        except subprocess.CalledProcessError:
            print("⚠️  ensurepip failed, downloading get-pip.py...")
            print("💡 Pip may not be available. Continuing anyway...")


def upgrade_pip(python_exe, platform_info):
    """Upgrade pip using the recommended method."""
    print("📈 Upgrading pip...")

    try:
        # Use python -m pip to upgrade (more reliable than calling pip directly)
        subprocess.check_call(
            [str(python_exe), "-m", "pip", "install", "--upgrade", "pip", "--quiet"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("✅ Pip upgraded successfully")
    except subprocess.CalledProcessError:
        # Non-fatal: continue with current pip version
        print("⚠️  Pip upgrade skipped (using current version)")
    except Exception as e:
        print(f"⚠️  Pip upgrade warning: {e}")


def install_dependencies(python_exe, pip_exe):
    """Install dependencies from requirements.txt."""
    requirements_file = Path("requirements.txt")

    if not requirements_file.exists():
        print("⚠️  requirements.txt not found, installing core dependencies...")
        # Install core dependencies if requirements.txt is missing
        deps = ["textual>=0.65.0", "rich", "pyperclip"]
        for dep in deps:
            print(f"   Installing {dep}...")
            try:
                subprocess.check_call(
                    [str(python_exe), "-m", "pip", "install", dep],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {dep}: {e}")
                raise LauncherError(f"Failed to install {dep}")
    else:
        print("📥 Installing dependencies from requirements.txt...")
        try:
            subprocess.check_call(
                [str(python_exe), "-m", "pip", "install", "-r", str(requirements_file)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            raise LauncherError("Dependency installation failed")


def launch_application(python_exe, platform_info):
    """Launch the application using the appropriate method for the platform."""
    print("🎯 Launching application...")

    try:
        if platform_info["is_windows"]:
            # Windows: Use subprocess.Popen to spawn new process
            # We need to properly handle the path on Windows
            python_str = str(python_exe)

            # Use Popen without detached mode to keep output visible
            subprocess.call([python_str, "app.py"])
        else:
            # Linux/macOS: Use os.exec* to replace current process
            # This is cleaner as the launcher process is replaced
            os.execvp(str(python_exe), [str(python_exe), "app.py"])
    except Exception as e:
        print(f"❌ Failed to launch application: {e}")
        raise LauncherError("Application launch failed")


def print_success_message(platform_info):
    """Print success message with platform-specific notes."""
    print()
    print("=" * 50)
    print("✅ Setup complete!")
    print("=" * 50)
    print()
    print("🚀 Starting Terraform IPv4 IoC Normalizer...")
    print()

    if platform_info["is_windows"]:
        print("💡 Tip: Press 'q' or Esc to quit the application")
        print("💡 To run again: python launcher.py")
    else:
        print("💡 Tip: Press 'Esc' to quit the application")
        print("💡 To run again: python3 launcher.py")

    print()


def main():
    """Main launcher function."""
    print()
    print("🔧 Terraform IPv4 IoC Normalizer - Launcher")
    print("=" * 50)
    print()

    try:
        # Step 1: Check Python version
        check_python_version()

        # Step 2: Get platform information
        platform_info = get_platform_info()
        print(f"🖥️  Platform: {platform_info['system']}")

        # Step 3: Check if app.py exists
        check_app_file()

        # Step 4: Create virtual environment
        venv_dir = Path(".venv")
        create_virtualenv(venv_dir, platform_info)

        # Step 5: Get executable paths
        python_exe, pip_exe = get_executable_paths(venv_dir, platform_info)

        # Step 6: Ensure pip is installed
        ensure_pip_installed(python_exe, platform_info)

        # Step 7: Upgrade pip
        upgrade_pip(python_exe, platform_info)

        # Step 8: Install dependencies
        install_dependencies(python_exe, pip_exe)

        # Step 9: Print success message
        print_success_message(platform_info)

        # Step 10: Launch application
        launch_application(python_exe, platform_info)

    except LauncherError as e:
        print()
        print(f"❌ Launcher error: {e}")
        print()
        print("Troubleshooting tips:")
        print("  • Ensure Python 3.8+ is installed")
        print("  • Run this script from the project root directory")
        print("  • Check that you have write permissions")
        if platform_info.get("is_windows", False):
            print("  • Try running as Administrator if needed")
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print("⚠️  Setup cancelled by user")
        sys.exit(130)
    except Exception as e:
        print()
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
