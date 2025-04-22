#!/usr/bin/env python3

import os
import subprocess
import shutil
import json

SCRIPT_NAME = "xclip-ocr.py"
USER_HOME = os.path.expanduser("~")
INSTALL_DIR = os.path.join(USER_HOME, ".local", "bin")
SCRIPT_PATH = os.path.join(INSTALL_DIR, SCRIPT_NAME)

def install_dependencies():
    print("📦 Installing required packages...")
    subprocess.run(["sudo", "apt", "install", "-y", "tesseract-ocr", "flameshot", "xclip", "xdotool", "libnotify-bin"], check=True)

def copy_script():
    print(f"📁 Installing script to {INSTALL_DIR}")
    os.makedirs(INSTALL_DIR, exist_ok=True)
    shutil.copy(SCRIPT_NAME, SCRIPT_PATH)
    os.chmod(SCRIPT_PATH, 0o755)

def get_desktop_environment():
    return os.environ.get("XDG_CURRENT_DESKTOP", "").strip().lower()

def bind_hotkey_cinnamon():
    print("🔗 Setting up hotkey for Cinnamon (Super + Shift + T)...")

    key_base = "/org/cinnamon/desktop/keybindings/custom-keybindings"
    key_name = "custom0"
    full_key_path = f"{key_base}/{key_name}/"

    try:
        # Step 1: Read current custom-keybindings
        result = subprocess.run(["dconf", "read", key_base], capture_output=True, text=True)
        current = result.stdout.strip()

        keylist = []
        if current and current != "[]":
            keylist = json.loads(current.replace("'", '"'))

        if full_key_path not in keylist:
            keylist.append(full_key_path)
            subprocess.run(["dconf", "write", key_base, str(keylist).replace('"', "'")], check=True)

        # Step 2: Write binding, name, and command
        subprocess.run(["dconf", "write", f"{full_key_path}name", "'Text Extractor'"], check=True)
        subprocess.run(["dconf", "write", f"{full_key_path}command", f"'python3 {SCRIPT_PATH}'"], check=True)
        subprocess.run(["dconf", "write", f"{full_key_path}binding", "['<Super><Shift>t']"], check=True)

        print("✅ Hotkey successfully bound in Cinnamon.")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to bind hotkey automatically: {e}")
        return False

def print_manual_instructions(de):
    print("\n📋 Manual Hotkey Setup Instructions:")
    print("1. Open your system's Keyboard Shortcuts menu.")
    print(f"2. Add a new shortcut pointing to: {SCRIPT_PATH}")
    print("3. Set the shortcut to: Super + Shift + T")

    if "cinnamon" in de:
        print("→ Cinnamon: Menu → Keyboard → Shortcuts → Custom Shortcuts")
    elif "kde" in de:
        print("→ KDE: System Settings → Shortcuts → Custom Shortcuts")
    elif "xfce" in de:
        print("→ XFCE: Settings → Keyboard → Application Shortcuts")
    elif "lxde" in de or "openbox" in de:
        print("→ LXDE/Openbox: You may need to edit ~/.config/openbox/lxde-rc.xml")
    else:
        print("→ Try searching 'keyboard shortcuts' in your system menu.")

def main():
    print(f"[+] Installing xclip-ocr")
    install_dependencies()
    copy_script()

    de = get_desktop_environment()
    print(f"🖥️ Detected desktop environment: {de}")

    success = False

    if "cinnamon" in de:
        success = bind_hotkey_cinnamon()
    else:
        print("⚠️ Your desktop environment is not fully supported for auto-binding.")

    if not success:
        print_manual_instructions(de)

    print("\n� Setup complete. Try Super + Shift + T or test manually.")

if __name__ == "__main__":
    main()

