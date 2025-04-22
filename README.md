# 📸 xclip-ocr - Quick OCR from Your Screen to Clipboard

![License](https://img.shields.io/github/license/rpriven/ocr-xclip)
![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![Platform](https://img.shields.io/badge/platform-linux-lightgrey)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)

**xclip-ocr** is a lightweight Linux utility that lets you quickly select any part of your screen, extract the text via OCR (using Tesseract), and copy it straight to your clipboard — all with a hotkey.

## ✨ Features

- Fast screenshot-to-text via [Flameshot](https://flameshot.org/)
- OCR powered by [Tesseract](https://github.com/tesseract-ocr/tesseract)
- Automatically copies extracted text to your clipboard
- Works with `xclip`, `xsel`, or (coming soon...`pyperclip`)
- Hotkey integration via your system (e.g., Cinnamon, GNOME, etc.)

---

## 🛠 Installation

### 1. Clone the repository

```bash
git clone https://github.com/rpriven/xclip-ocr.git
cd xclip-ocr
```

### 2. Run the install script (this installs dependencies and makes script available system-wide)

```bash
python3 install.py
```

Make sure you have the latest Tesseract (v5+):

```bash
tesseract --version
```

> If needed, you can add a PPA for the latest Tesseract:
> ```bash
> sudo add-apt-repository ppa:alex-p/tesseract-ocr-devel
> sudo apt update && sudo apt upgrade
> ```

Make sure `~/.local/bin` is in your `$PATH`.

---

## 🖱️ Usage

Run manually:

```bash
xclip-ocr.py
```

You'll be prompted to select a screen region. Press 'Enter' and the text will be OCR'd and copied to your clipboard automatically.

---

## ⌨️ Optional: Hotkey Setup (e.g., Cinnamon)

1. Open `Keyboard Settings` → "Custom Shortcuts"
2. Add a new shortcut:
   - **Name:** xclip-ocr
   - **Command:** `python3 /home/$USER/.local/bin/xclip-ocr.py`
   - **Shortcut:** Set your preferred key combo (e.g., `Shift + Super + T`)
3. Save and test.

> ⚠️ In some desktop environments, the hotkey might not appear until you create it manually in the GUI.

---

## 🧠 Troubleshooting

- **No text found?**
  - Make sure your screenshot includes real text, not a blurry image or graphic.
  - Ensure `tesseract-ocr` and its language files (like `eng.traineddata`) are installed.
  - You may need to set `TESSDATA_PREFIX` if Tesseract can’t find language files (already handled by the script, just in case).

- **Clipboard not working?**
  - Ensure you have `xclip`, `xsel` or (`pyperclip`)
  - Check that `$DISPLAY` is set if running in a graphical session.
  - Check the logs in /tmp/xclip-ocr-error.log or /tmp/xclip-ocr-debug.log
  - See if you are able to run `tesseract /tmp/tmp<image>.png` to extract manually, if that works it's a hotkey issue

---

## 📂 File Overview

- `xclip-ocr.py` — main script
- `install.py` — automation of setup
- `README.md` — you're here

---

## Contributing

- If you find any issues, please let me know so I can fix them.
- Please feel free to help me make this work on additional distros.

---

## 💬 License

MIT — free for personal and commercial use.

---

## 🙌 Credits

Thanks to the developers of [Tesseract OCR](https://github.com/tesseract-ocr/tesseract), [Flameshot](https://flameshot.org/), and the Linux desktop community 🐧

