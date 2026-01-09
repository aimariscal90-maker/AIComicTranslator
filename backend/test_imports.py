
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

print("Testing imports...")
try:
    print("1. Importing BubbleDetector...")
    from services.detector import BubbleDetector
    print("   Detector imported.")
    
    print("2. Importing OCRService...")
    from services.ocr import OCRService
    print("   OCR imported.")

    print("3. Importing TranslatorService...")
    from services.translator import TranslatorService
    print("   Translator imported.")

    print("4. Importing TextRemover...")
    from services.inpainting import TextRemover
    print("   Remover imported.")

    print("ALL SERVICES OK.")
except Exception as e:
    print(f"IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
