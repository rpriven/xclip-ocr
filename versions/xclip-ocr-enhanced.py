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

def enhance_image_for_ocr(temp_path):
    """
    Enhanced image preprocessing that preserves quality
    """
    try:
        img = Image.open(temp_path)
        log_debug(f"Original image: {img.size}, mode: {img.mode}")

        # Convert to grayscale
        if img.mode != 'L':
            img = img.convert('L')

        # Only apply enhancements if image is small or low quality
        w, h = img.size

        # Smart upscaling for small images
        if w < 400 or h < 200:
            scale_factor = 2 if min(w, h) < 200 else 1.5
            new_w, new_h = int(w * scale_factor), int(h * scale_factor)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            log_debug(f"Upscaled to: {new_w}x{new_h}")

        # Very gentle noise reduction (much less aggressive than before)
        img = img.filter(ImageFilter.MedianFilter(size=3))

        # Smart contrast enhancement based on image statistics
        import numpy as np
        img_array = np.array(img)
        contrast = np.std(img_array)

        if contrast < 40:  # Only enhance low-contrast images
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)  # Much gentler than 2.0
            log_debug("Applied gentle contrast enhancement")

        # Gentle sharpening instead of harsh threshold
        img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=100, threshold=3))

        # Save the enhanced image
        img.save(temp_path)
        log_debug("Image enhancement complete")
        return True

    except Exception as e:
        log_debug(f"Image enhancement failed: {e}")
        log_error(e)
        return False

def run_ocr_with_best_settings(temp_path):
    """
    Run OCR with optimized Tesseract settings
    """
    # Try multiple OCR approaches
    ocr_configs = [
        # Best for general text blocks (like UI text, paragraphs)
        ["tesseract", temp_path, "stdout", "--psm", "6", "--oem", "1"],

        # Good for mixed/sparse text (like menus, scattered text)
        ["tesseract", temp_path, "stdout", "--psm", "11", "--oem", "1"],

        # Single line text (like titles, labels)
        ["tesseract", temp_path, "stdout", "--psm", "7", "--oem", "1"],

        # Fallback to default
        ["tesseract", temp_path, "stdout", "--psm", "3", "--oem", "1"]
    ]

    best_result = ""
    best_length = 0

    for i, cmd in enumerate(ocr_configs):
        try:
            log_debug(f"Trying OCR config {i+1}: PSM={cmd[4]}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=ENV,
                timeout=20
            )

            text = result.stdout.strip()

            if text and len(text) > best_length:
                best_result = text
                best_length = len(text)
                log_debug(f"Config {i+1} found {len(text)} characters")

                # If first config works well, use it
                if i == 0 and len(text) > 5:
                    break

        except subprocess.TimeoutExpired:
            log_debug(f"Config {i+1} timed out")
            continue
        except Exception as e:
            log_debug(f"Config {i+1} failed: {e}")
            continue

    return best_result

def clean_ocr_text(text):
    """
    Clean up common OCR errors
    """
    if not text:
        return text

    # Remove excessive whitespace
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line:
            lines.append(line)

    cleaned_text = '\n'.join(lines)

    # Remove any trailing/leading whitespace
    cleaned_text = cleaned_text.strip()

    return cleaned_text

def main():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
        temp_path = temp_img.name

    try:
        log_debug("=== Starting Enhanced xclip-ocr ===")
        log_debug("Starting screenshot capture...")

        subprocess.run(
            ["flameshot", "gui", "-r"],
            stdout=open(temp_path, "wb"),
            check=True
        )
        log_debug(f"Screenshot saved to {temp_path}")

        if os.path.getsize(temp_path) == 0:
            subprocess.run(
                ["notify-send", "Text Extractor", "No region selected"],
                env=ENV
            )
            log_debug("No region selected, file is empty.")
            return

        # Enhanced preprocessing (less aggressive than current version)
        log_debug("Applying enhanced image processing...")
        enhance_image_for_ocr(temp_path)

        # Run OCR with multiple configurations
        log_debug("Running OCR with optimized settings...")
        text = run_ocr_with_best_settings(temp_path)

        # Clean up the text
        text = clean_ocr_text(text)

        log_debug(f"Final OCR result ({len(text)} chars):\n{text}")

        if text:
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

            # Enhanced notification with character count
            char_count = len(text)
            word_count = len(text.split())
            subprocess.run(
                ["notify-send", "Text Extracted",
                 f"✅ {char_count} chars, {word_count} words copied"],
                env=ENV,
            )
        else:
            log_debug("No text found by OCR.")
            subprocess.run(
                ["notify-send", "Text Extractor", "❌ No text found in image"],
                env=ENV,
            )

    except Exception as e:
        log_debug("Exception in main flow.")
        log_error(e)
        subprocess.run(
            ["notify-send", "Text Extractor", "❌ Error occurred during OCR"],
            env=ENV,
        )

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            log_debug(f"Deleted temp file: {temp_path}")

if __name__ == "__main__":
    main()