#!/usr/bin/python3

import subprocess
import os
import tempfile
import traceback
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np

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

def smart_preprocess_image(img_path):
    """
    Advanced image preprocessing using modern techniques
    """
    try:
        img = Image.open(img_path)
        log_debug(f"Original image size: {img.size}, mode: {img.mode}")

        # Convert to RGB first if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Calculate image characteristics to choose preprocessing
        gray = img.convert('L')
        img_array = np.array(gray)

        # Analyze image contrast and brightness
        mean_brightness = np.mean(img_array)
        contrast = np.std(img_array)

        log_debug(f"Image stats - Brightness: {mean_brightness:.1f}, Contrast: {contrast:.1f}")

        # Choose preprocessing based on image characteristics
        if contrast < 30:  # Low contrast image
            log_debug("Low contrast detected - applying contrast enhancement")
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)
        elif contrast > 80:  # High contrast image
            log_debug("High contrast detected - applying gentle smoothing")
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

        # Convert to grayscale
        gray = img.convert('L')

        # Adaptive thresholding instead of hard threshold
        img_array = np.array(gray)

        # Use Otsu's method for better thresholding
        from PIL import ImageOps
        if mean_brightness < 100:  # Dark image
            log_debug("Dark image - applying inversion")
            gray = ImageOps.invert(gray)

        # Gentle noise reduction only if needed
        if contrast > 60:  # Noisy image
            gray = gray.filter(ImageFilter.MedianFilter(size=3))

        # Smart upscaling - only if image is small
        w, h = gray.size
        if w < 300 or h < 100:  # Small text areas benefit from upscaling
            scale_factor = max(2, 400 // max(w, h))
            new_w, new_h = w * scale_factor, h * scale_factor
            gray = gray.resize((new_w, new_h), Image.LANCZOS)
            log_debug(f"Upscaled image to: {new_w}x{new_h}")

        # Slight sharpening for better edge definition
        gray = gray.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))

        gray.save(img_path)
        log_debug("Smart preprocessing complete")
        return True

    except Exception as e:
        log_debug(f"Preprocessing failed: {e}")
        log_error(e)
        return False

def run_tesseract_with_options(img_path):
    """
    Run Tesseract with optimized options for screenshot text
    """
    # Try different OCR configurations in order of preference
    configs = [
        # Best for general screenshot text
        {
            "psm": "6",  # Single uniform block
            "oem": "1",  # LSTM only (best quality)
            "config": ["-c", "tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,:;!?()-\"'"]
        },
        # Good for mixed text layouts
        {
            "psm": "11",  # Sparse text
            "oem": "1",
            "config": []
        },
        # Fallback for single line text
        {
            "psm": "7",  # Single line
            "oem": "1",
            "config": []
        },
        # Final fallback with default settings
        {
            "psm": "3",  # Default
            "oem": "3",  # Default
            "config": []
        }
    ]

    best_result = ""
    best_confidence = 0

    for i, config in enumerate(configs):
        try:
            cmd = [
                "tesseract", img_path, "stdout",
                "--psm", config["psm"],
                "--oem", config["oem"]
            ]

            # Add character whitelist if specified
            if config["config"]:
                cmd.extend(config["config"])

            log_debug(f"Trying OCR config {i+1}: PSM={config['psm']}, OEM={config['oem']}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=ENV,
                timeout=30
            )

            text = result.stdout.strip()

            if text:
                # Simple confidence heuristic
                confidence = len(text) * (1 - (result.stderr.count('WARNING') * 0.1))

                log_debug(f"Config {i+1} result: {len(text)} chars, confidence: {confidence:.1f}")
                log_debug(f"Text sample: {text[:100]}...")

                if confidence > best_confidence:
                    best_result = text
                    best_confidence = confidence

                # If we get good results with first config, use it
                if i == 0 and len(text) > 10:
                    break

        except subprocess.TimeoutExpired:
            log_debug(f"Config {i+1} timed out")
            continue
        except Exception as e:
            log_debug(f"Config {i+1} failed: {e}")
            continue

    return best_result

def main():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
        temp_path = temp_img.name

    try:
        log_debug("=== Starting xclip-ocr improved ===")
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

        # Smart preprocessing
        log_debug("Applying smart image preprocessing...")
        preprocess_success = smart_preprocess_image(temp_path)

        if not preprocess_success:
            log_debug("Preprocessing failed, using original image")

        # Advanced OCR with multiple attempts
        log_debug("Running advanced Tesseract OCR...")
        text = run_tesseract_with_options(temp_path)

        # Post-process text
        if text:
            # Clean up common OCR errors
            text = text.replace('\n\n', '\n')  # Remove double newlines
            text = text.replace('|', 'I')      # Common OCR error
            text = text.replace('0', 'O') if text.isupper() else text  # Context-based correction

            # Remove excessive whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)

        log_debug(f"Final OCR result ({len(text)} chars):\n{text}")

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

            # Show character count in notification
            char_count = len(text)
            subprocess.run(
                ["notify-send", "Text Extracted", f"✅ {char_count} characters copied to clipboard"],
                env=ENV,
            )
        else:
            log_debug("No text detected by any OCR method.")
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