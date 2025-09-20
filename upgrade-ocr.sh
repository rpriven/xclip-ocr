#!/bin/bash

# Upgrade script for xclip-ocr improvements

echo "🔧 xclip-ocr Quality Improvement Upgrade"
echo "========================================="

# Backup current version
if [ -f "xclip-ocr.py" ]; then
    echo "📦 Backing up current version..."
    cp xclip-ocr.py xclip-ocr-backup-$(date +%Y%m%d).py
    echo "✅ Backup saved as xclip-ocr-backup-$(date +%Y%m%d).py"
fi

# Show available improved versions
echo ""
echo "📋 Available improved versions:"
echo "1. xclip-ocr-enhanced.py  - Recommended: Improved quality with smart processing"
echo "2. xclip-ocr-improved.py  - Advanced: Maximum features with detailed analysis"
echo "3. original-xclip-ocr.py  - Fallback: Original simple version"

echo ""
read -p "Choose version to install (1, 2, or 3): " choice

case $choice in
    1)
        echo "🚀 Installing enhanced version..."
        cp xclip-ocr-enhanced.py xclip-ocr.py
        chmod +x xclip-ocr.py
        echo "✅ Enhanced version installed!"
        ;;
    2)
        echo "🚀 Installing improved (advanced) version..."
        cp xclip-ocr-improved.py xclip-ocr.py
        chmod +x xclip-ocr.py
        echo "✅ Advanced version installed!"
        ;;
    3)
        echo "🔄 Restoring original version..."
        cp original-xclip-ocr.py xclip-ocr.py
        chmod +x xclip-ocr.py
        echo "✅ Original version restored!"
        ;;
    *)
        echo "❌ Invalid choice. No changes made."
        exit 1
        ;;
esac

echo ""
echo "🎯 What's been improved:"
echo "• Better OCR engine settings (LSTM neural network)"
echo "• Smart image preprocessing (less aggressive)"
echo "• Multiple OCR attempts with different page segmentation"
echo "• Enhanced text cleaning and formatting"
echo "• Better error handling and debugging"
echo "• Character and word count in notifications"

echo ""
echo "🧪 To test the improvements:"
echo "• Use your normal hotkey to capture screen text"
echo "• Check debug log: cat /tmp/xclip-ocr-debug.txt"
echo "• Run comparison test: ./test-ocr-comparison.py"

echo ""
echo "📝 Configuration tips:"
echo "• For very small text: Use PSM mode 8 (single word)"
echo "• For single lines: Use PSM mode 7 (single line)"
echo "• For mixed layouts: Current smart detection should work well"

echo ""
echo "✅ Installation complete! Your OCR should now be more accurate."