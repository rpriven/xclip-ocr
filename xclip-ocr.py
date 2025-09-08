#!/usr/bin/python3

import subprocess
import os
import tempfile
import traceback
from PIL import Image, ImageFilter, ImageEnhance

DEBUG_LOG = "/tmp/xclip-ocr-debug.txt"
ERROR_LOG = "/tmp/xclip-ocr-error.log"

# Environment for subprocesses
ENV = os.environ.copy()
ENV["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/5/tessdata/"

def log_debug(msg):
    with open(DEBUG_LOG, "a") as f:
        f.write(msg + "\n")

def log_error(e):
    with open(ERROR_LOG, "w") as f:
        traceback.print_exc(file=f)

def main():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
        temp_path = temp_img.name

    try:
        log_debug("Starting screenshot capture...")
        subprocess.run(
            ["flameshot", "gui", "-r"], stdout=open(temp_path, "wb"), check=True
        )
        log_debug(f"Screenshot saved to {temp_path}")

        if os.path.getsize(temp_path) == 0:
            subprocess.run(
                ["notify-send", "Text Extractor", "No region selected"], env=ENV
            )
            log_debug("No region selected, file is empty.")
            return

        # Preprocess image
        log_debug("Preprocessing image for OCR...")
        try:
            img = Image.open(temp_path)
            img = img.convert("L")  # grayscale
            img = img.filter(ImageFilter.MedianFilter(3))  # denoise
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)  # increase contrast
            w, h = img.size
            img = img.resize((w * 2, h * 2))  # upscale
            img = img.point(lambda x: 0 if x < 128 else 255, "1")  # threshold
            img.save(temp_path)
            log_debug("Image preprocessing complete")
        except Exception as e:
            log_debug("Image preprocessing failed, continuing")
            log_error(e)

        log_debug("Running Tesseract OCR...")
        result = subprocess.run(
            ["tesseract", temp_path, "stdout"],
            capture_output=True,
            text=True,
            env=ENV,
        )
        text = result.stdout
        log_debug(f"OCR result:\n{text}")

        if text.strip():
            try:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text.encode("utf-8"),
                    check=True,
                    env=ENV,
                )
                log_debug("Text copied using xclip.")
            except Exception:
                log_debug("xclip failed, trying xsel...")
                try:
                    subprocess.run(
                        ["xsel", "--clipboard"],
                        input=text.encode("utf-8"),
                        check=True,
                        env=ENV,
                    )
                    log_debug("Text copied using xsel.")
                except Exception as e2:
                    log_debug("xsel also failed.")
                    log_error(e2)
            subprocess.run(
                ["notify-send", "Text Extracted", "✅ Text copied to clipboard"],
                env=ENV,
            )
        else:
            log_debug("Tesseract did not find any text.")
            subprocess.run(
                ["notify-send", "Text Extractor", "No text found in image"],
                env=ENV,
            )

    except Exception as e:
        log_debug("Exception in main flow.")
        log_error(e)

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            log_debug(f"Deleted temp file: {temp_path}")

if __name__ == "__main__":
    main()
