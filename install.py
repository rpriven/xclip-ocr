#!/usr/bin/env python3

import os
import sys
import argparse
import logging
import subprocess
import shutil
import json

SCRIPT_NAME = "xclip-ocr.py"
USER_HOME = os.path.expanduser("~")

# configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def detect_pkg_manager(pref=None):
    if pref:
        return pref
    for mgr in ("apt", "dnf", "pacman"): 
        if shutil.which(mgr):
            return mgr
    return None

def install_dependencies(pkg_manager=None):
    logging.info("Installing required packages...")
    mgr = detect_pkg_manager(pkg_manager)
    if not mgr:
        logging.warning("No supported package manager found; please install dependencies manually.")
        return
    pkgs = ["tesseract-ocr", "flameshot", "xclip", "xdotool", "libnotify-bin"]
    if mgr == "apt":
        cmd = ["sudo", "apt", "install", "-y"] + pkgs
    elif mgr == "dnf":
        cmd = ["sudo", "dnf", "install", "-y"] + pkgs
    else:
        cmd = ["sudo", "pacman", "-Sy", "--noconfirm"] + pkgs
    subprocess.run(cmd, check=True)

def copy_script(install_dir):
    dest = os.path.join(install_dir, SCRIPT_NAME)
    os.makedirs(install_dir, exist_ok=True)
    shutil.copy(SCRIPT_NAME, dest)
    os.chmod(dest, 0o755)
    logging.info(f"Script installed to {dest}")
    return dest

def get_desktop_environment():
    return os.environ.get("XDG_CURRENT_DESKTOP", "").lower()

def bind_hotkey_cinnamon(script_path):
    logging.info("Binding hotkey for Cinnamon...")
    key_base = "/org/cinnamon/desktop/keybindings/custom-keybindings"
    # read current list
    res = subprocess.run(["dconf", "read", key_base], capture_output=True, text=True)
    current = res.stdout.strip()
    try:
        plist = json.loads(current.replace("'", '"')) if current and current != '[]' else []
    except:
        plist = []
    # find next index
    idx = 0
    while f"{key_base}/custom{idx}/" in plist:
        idx += 1
    new_path = f"{key_base}/custom{idx}/"
    plist.append(new_path)
    subprocess.run(["dconf", "write", key_base, str(plist).replace('"', "'")], check=True)
    subprocess.run(["dconf", "write", f"{new_path}name", "'xclip-ocr'"], check=True)
    subprocess.run(["dconf", "write", f"{new_path}command", f"'{sys.executable} {script_path}'"], check=True)
    subprocess.run(["dconf", "write", f"{new_path}binding", "['<Super><Shift>t']"], check=True)
    logging.info("Hotkey successfully bound.")
    return True

def unbind_hotkey_cinnamon(script_path):
    logging.info("Unbinding hotkey for Cinnamon...")
    key_base = "/org/cinnamon/desktop/keybindings/custom-keybindings"
    res = subprocess.run(["dconf", "read", key_base], capture_output=True, text=True)
    current = res.stdout.strip()
    try:
        plist = json.loads(current.replace("'", '"')) if current and current != '[]' else []
    except:
        plist = []
    new_list = []
    for path in plist:
        cmd_key = f"{path}command"
        val = subprocess.run(["dconf", "read", cmd_key], capture_output=True, text=True).stdout.strip()
        if script_path in val:
            subprocess.run(["dconf", "reset", cmd_key], check=True)
            subprocess.run(["dconf", "reset", f"{path}name"], check=True)
            subprocess.run(["dconf", "reset", f"{path}binding"], check=True)
        else:
            new_list.append(path)
    subprocess.run(["dconf", "write", key_base, str(new_list).replace('"', "'")], check=True)
    logging.info("Hotkey unbound.")
    return True

def print_manual_instructions():
    logging.info("Manual hotkey setup:")
    logging.info("1. Open Keyboard Shortcuts in your DE settings.")
    logging.info(f"2. Command: {sys.executable} {os.path.join(USER_HOME, '.local', 'bin', SCRIPT_NAME)}")
    logging.info("3. Shortcut: Super+Shift+T (or your choice)")


def main():
    parser = argparse.ArgumentParser(description="Install or uninstall xclip-ocr")
    parser.add_argument("--install-dir", default=os.path.join(USER_HOME, '.local', 'bin'), help="Installation directory")
    parser.add_argument("--pkg-manager", choices=["apt", "dnf", "pacman"], default=None, help="Package manager to use")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall script and hotkey")
    args = parser.parse_args()

    install_dir = args.install_dir
    script_path = os.path.join(install_dir, SCRIPT_NAME)

    de = get_desktop_environment()

    if args.uninstall:
        # remove script
        if os.path.exists(script_path):
            os.remove(script_path)
            logging.info(f"Removed {script_path}")
        # unbind hotkey
        if "cinnamon" in de:
            unbind_hotkey_cinnamon(script_path)
        sys.exit(0)

    logging.info("Starting installation of xclip-ocr...")
    install_dependencies(args.pkg_manager)
    installed_path = copy_script(install_dir)
    logging.info(f"Installed at {installed_path}")
    # bind hotkey
    if "cinnamon" in de:
        bind_hotkey_cinnamon(installed_path)
    else:
        logging.warning(f"DE '{de}' not fully supported; use manual setup")
        print_manual_instructions()

if __name__ == "__main__":
    main()
