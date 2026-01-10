
import cv2
import numpy as np
from services.style_analyzer import StyleAnalyzer
import os

def create_test_image(text="TEST", bg_color=255, text_color=0):
    # Create black or white image
    img = np.full((100, 200, 3), bg_color, dtype=np.uint8)
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, text, (50, 50), font, 1, (text_color, text_color, text_color), 2)
    return img

def test_analyzer():
    print("Testing Style Analyzer...")
    analyzer = StyleAnalyzer()
    
    # Test 1: Light BG (Black Text)
    print("\n--- Test 1: Light Background (Black Text) ---")
    img_light = create_test_image(text="BOLD", bg_color=255, text_color=0) 
    # Use thicker font (thickness=3) to simulate bold
    cv2.putText(img_light, "BOLD", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)
    
    result = analyzer.analyze_roi(img_light, [0, 0, 200, 100])
    print(f"Result: {result}")
    
    # Test 2: Dark BG (Red Text)
    print("\n--- Test 2: Dark Background (Red Text) ---")
    # Red in BGR is (0, 0, 255)
    img_dark = create_test_image(text="RED", bg_color=0, text_color=0) # dummy
    img_dark[:] = 0 # reset to black
    cv2.putText(img_dark, "RED", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    result_dark = analyzer.analyze_roi(img_dark, [0, 0, 200, 100])
    print(f"Result: {result_dark}")
    
    if result.get('is_bold'): print("✅ Bold detection passed")
    if result_dark.get('text_color') == '#ff0000': print("✅ Color detection passed (Red)")
    else: print(f"⚠️ Color mismatch: Expected #ff0000, got {result_dark.get('text_color')}")

if __name__ == "__main__":
    test_analyzer()
