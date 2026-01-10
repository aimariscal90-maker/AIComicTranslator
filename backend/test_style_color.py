
import cv2
import numpy as np
from services.style_analyzer import StyleAnalyzer

def create_color_test(bg_color, text_color, text="TEST"):
    img = np.full((100, 200, 3), bg_color, dtype=np.uint8) # BGR
    cv2.putText(img, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 4)
    return img

def test_colors():
    analyzer = StyleAnalyzer()
    
    # Case 1: Yellow Text (0, 255, 255) on Blue BG (255, 0, 0) -> High Contrast
    print("\n--- Test 1: Yellow Text on Blue BG ---")
    img1 = create_color_test((255, 0, 0), (0, 255, 255)) 
    res1 = analyzer.analyze_roi(img1, [0, 0, 200, 100])
    print(f"Detected: {res1.get('text_color')} (Expected Yellowish)")

    # Case 2: Purple Text (128, 0, 128) on Gray BG (128, 128, 128) -> Medium Contrast
    print("\n--- Test 2: Purple Text on Gray BG ---")
    img2 = create_color_test((128, 128, 128), (128, 0, 128))
    res2 = analyzer.analyze_roi(img2, [0, 0, 200, 100])
    print(f"Detected: {res2.get('text_color')} (Expected Purpleish)")

    # Case 3: Dark Green Text (0, 100, 0) on Black BG (0, 0, 0) -> Low Contrast
    print("\n--- Test 3: Dark Green Text on Black BG ---")
    img3 = create_color_test((0, 0, 0), (0, 100, 0))
    res3 = analyzer.analyze_roi(img3, [0, 0, 200, 100])
    print(f"Detected: {res3.get('text_color')} (Expected #006400 approx)")

if __name__ == "__main__":
    test_colors()
