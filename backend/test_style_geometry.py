
import cv2
import numpy as np
from services.style_analyzer import StyleAnalyzer

def create_size_test(font_scale, thickness, text="SIZE"):
    # Dark text on light background
    img = np.full((100, 300, 3), 255, dtype=np.uint8) # White BG
    
    # Scale 1.0 approx 22px height in Hershey Simplex
    cv2.putText(img, text, (50, 70), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)
    return img

def test_geometry():
    analyzer = StyleAnalyzer()
    
    # Test 1: Small Text (Scale 0.5)
    print("\n--- Test 1: Small Text (Scale 0.5) ---")
    img1 = create_size_test(0.5, 1, "Small")
    res1 = analyzer.analyze_roi(img1, [0, 0, 300, 100])
    print(f"Detected Size: {res1.get('estimated_font_size')}px (Expected ~15-20)")

    # Test 2: Medium Text (Scale 1.0)
    print("\n--- Test 2: Medium Text (Scale 1.0) ---")
    img2 = create_size_test(1.0, 2, "Medium")
    res2 = analyzer.analyze_roi(img2, [0, 0, 300, 100])
    print(f"Detected Size: {res2.get('estimated_font_size')}px (Expected ~30-35)")

    # Test 3: Large Text (Scale 2.0)
    print("\n--- Test 3: Large Text (Scale 2.0) ---")
    img3 = create_size_test(2.0, 4, "LARGE")
    res3 = analyzer.analyze_roi(img3, [0, 0, 300, 100])
    print(f"Detected Size: {res3.get('estimated_font_size')}px (Expected ~60-70)")

if __name__ == "__main__":
    test_geometry()
