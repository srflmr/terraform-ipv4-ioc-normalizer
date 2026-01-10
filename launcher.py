#!/usr/bin/env python3
"""
🚀 Terraform IPv4 Normalizer - AUTO VENV LAUNCHER
Copy-paste → chmod +x start.py → python3 start.py
"""
import os
import sys
import subprocess
from pathlib import Path
import platform

def setup_and_launch():
    print("🔧 Auto setup Terraform IPv4 Normalizer...")
    
    # Check app.py exists
    app_file = Path("app.py")
    if not app_file.exists():
        print("❌ Create 'app.py' first!")
        print("💡 Copy the app code from instructions")
        return
    
    # Create .venv
    venv_dir = Path(".venv")
    if not venv_dir.exists():
        print("📦 Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", ".venv"])
    
    # Platform paths
    is_windows = platform.system() == "Windows"
    scripts_dir = "Scripts" if is_windows else "bin"
    pip_exe = venv_dir / scripts_dir / ("pip.exe" if is_windows else "pip")
    python_exe = venv_dir / scripts_dir / ("python.exe" if is_windows else "python")
    
    # Install dependencies
    print("📥 Installing dependencies...")
    subprocess.check_call([str(pip_exe), "install", "--upgrade", "pip"])
    deps = ["textual>=0.65.0", "rich", "pyperclip"]
    for dep in deps:
        subprocess.check_call([str(pip_exe), "install", dep])
    
    print("✅ Setup complete! 🎯 Launching app...")
    os.execl(str(python_exe), str(python_exe), "app.py")

if __name__ == "__main__":
    setup_and_launch()
