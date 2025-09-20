#!/usr/bin/python3
"""
Test script to compare OCR quality between different versions
"""

import subprocess
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont

def create_test_image():
    """Create a test image with various text challenges"""
    # Create image with different text scenarios
    img = Image.new('RGB', (800, 400), 'white')
    draw = ImageDraw.Draw(img)

    # Try to use a decent font, fallback to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Different text scenarios
    test_texts = [
        ("Large Title Text", 50, 50, font_large, "black"),
        ("Medium paragraph text with numbers 12345", 50, 100, font_medium, "black"),
        ("Small fine print details", 50, 150, font_small, "black"),
        ("Mixed Case: Hello World 2024!", 50, 200, font_medium, "blue"),
        ("UPPERCASE TEXT BLOCK", 50, 250, font_medium, "darkgreen"),
        ("lowercase only text", 50, 300, font_medium, "darkred"),
    ]

    for text, x, y, font, color in test_texts:
        draw.text((x, y), text, fill=color, font=font)

    # Add some background noise/texture
    for i in range(0, 800, 100):
        for j in range(0, 400, 100):
            draw.rectangle([i, j, i+50, j+50], outline="lightgray")

    return img

def test_ocr_version(script_path, test_image_path):
    """Test a specific OCR script version"""
    print(f"\n=== Testing {script_path} ===")

    # Copy our test image to the temp location that the script expects
    temp_path = "/tmp/test_ocr_input.png"

    try:
        # Simulate the screenshot by copying our test image
        with open(test_image_path, 'rb') as src:
            with open(temp_path, 'wb') as dst:
                dst.write(src.read())

        # Run the OCR script
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        print(f"Exit code: {result.returncode}")

        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")

        if result.stderr:
            print(f"STDERR:\n{result.stderr}")

        # Check debug log
        debug_log = "/tmp/xclip-ocr-debug.txt"
        if os.path.exists(debug_log):
            with open(debug_log, 'r') as f:
                debug_content = f.read()
                print(f"Debug log:\n{debug_content[-500:]}")  # Last 500 chars

        # Get clipboard content
        try:
            clipboard_result = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True,
                text=True
            )
            if clipboard_result.returncode == 0:
                clipboard_text = clipboard_result.stdout
                print(f"\nClipboard content:\n{clipboard_text}")
                return clipboard_text
            else:
                print("Could not read clipboard")
                return ""
        except:
            print("xclip not available for testing")
            return ""

    except subprocess.TimeoutExpired:
        print("Script timed out")
        return ""
    except Exception as e:
        print(f"Error testing script: {e}")
        return ""
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

def compare_results(original_result, improved_result):
    """Compare OCR results"""
    print("\n=== COMPARISON ===")
    print(f"Original result length: {len(original_result)} characters")
    print(f"Improved result length: {len(improved_result)} characters")

    if len(improved_result) > len(original_result):
        print("✅ Improved version detected more text")
    elif len(improved_result) < len(original_result):
        print("⚠️ Improved version detected less text")
    else:
        print("➡️ Same amount of text detected")

    # Check for common words that should be detected
    test_words = ["Title", "Text", "paragraph", "numbers", "12345", "Hello", "World", "2024"]
    original_words = sum(1 for word in test_words if word in original_result)
    improved_words = sum(1 for word in test_words if word in improved_result)

    print(f"Test words detected - Original: {original_words}/{len(test_words)}, Improved: {improved_words}/{len(test_words)}")

def main():
    print("Creating test image...")
    test_img = create_test_image()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        test_img_path = temp_file.name
        test_img.save(test_img_path)

    try:
        print(f"Test image saved to: {test_img_path}")

        # Clear debug log
        debug_log = "/tmp/xclip-ocr-debug.txt"
        if os.path.exists(debug_log):
            os.remove(debug_log)

        # Test original version
        original_result = test_ocr_version("xclip-ocr.py", test_img_path)

        # Clear debug log for improved version
        if os.path.exists(debug_log):
            os.remove(debug_log)

        # Test improved version
        improved_result = test_ocr_version("xclip-ocr-improved.py", test_img_path)

        # Compare results
        compare_results(original_result, improved_result)

    finally:
        if os.path.exists(test_img_path):
            os.remove(test_img_path)
            print(f"\nCleaned up test image: {test_img_path}")

if __name__ == "__main__":
    main()