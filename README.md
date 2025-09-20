# 📸 xclip-ocr - Quick OCR from Your Screen to Clipboard

![License](https://img.shields.io/github/license/rpriven/xclip-ocr?style=flat)
![Python](https://img.shields.io/badge/python-3.6%2B-blue?style=flat)
![Platform](https://img.shields.io/badge/platform-linux-lightgrey?style=flat)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat)

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Hotkey Setup](#hotkey-setup)
- [Troubleshooting](#troubleshooting)
- [File Overview](#file-overview)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

- Fast screenshot-to-text via [Flameshot](https://flameshot.org/)
- OCR powered by [Tesseract v5+](https://github.com/tesseract-ocr/tesseract) with LSTM neural engine
- **Enhanced OCR quality** with smart preprocessing and multiple detection modes
- **Multiple OCR attempts** using different page segmentation modes for better accuracy
- **Smart image enhancement** that preserves text quality instead of over-processing
- Automatic clipboard copy (`xclip` or `xsel`)
- Detailed notifications with character and word count
- Simple hotkey integration

---

## 🛠 Prerequisites

- Python 3.6 or newer
- [Flameshot](https://flameshot.org/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) with language data
- `xclip` or `xsel` for clipboard
- Ensure `~/.local/bin` is in your `$PATH`

---

## 🚀 Installation

```bash
git clone https://github.com/rpriven/xclip-ocr.git
cd xclip-ocr
python3 install.py
```

> Verifies and installs system dependencies, then copies `xclip-ocr.py` to `~/.local/bin`.

---

## 🖱️ Usage

Run the script and select a screen region:

```bash
xclip-ocr.py
# Select with Flameshot, then Enter → OCR & clipboard copy
```

---

## ⌨️ Hotkey Setup

1. **Cinnamon (auto-installed):** Super + Shift + T bound by `install.py`.
2. **Manual (any DE):**
   - Command: `python3 $HOME/.local/bin/xclip-ocr.py`
   - Shortcut: your preferred key combo

---

## 🧠 Troubleshooting

- **No text?** Ensure clear text, install `tesseract-ocr` and language files.
- **Clipboard issues?** Verify `xclip`/`xsel`, check `$DISPLAY`, inspect `/tmp/xclip-ocr-debug.txt` & `error.log`.

---

## 📂 File Overview

| File            | Description               |
|-----------------|---------------------------|
| `xclip-ocr.py`  | Main OCR script           |
| `install.py`    | Dependency & hotkey setup |
| `README.md`     | Project documentation     |

---

## 🤝 Contributing

Issues & PRs: https://github.com/rpriven/xclip-ocr/issues


---

## 📄 License

MIT — see [LICENSE](LICENSE)
