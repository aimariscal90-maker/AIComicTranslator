import sys
import os
import cv2
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.style_analyzer import StyleAnalyzer
from services.font_matcher import FontMatcher
from services.renderer import TextRenderer

def test_pipeline_e2e():
    print("\n🚀 --- TESTING DAY 10: END-TO-END PIPELINE QUALITY GATE ---\n")
    
    # 1. Setup Components
    analyzer = StyleAnalyzer()
    matcher = FontMatcher()
    renderer = TextRenderer()
    
    # 2. Create Synthetic Input (Mocking a Comic Page)
    img_h, img_w = 400, 400
    img = np.ones((img_h, img_w, 3), dtype=np.uint8) * 255 
    
    # Draw simple text to analyze (Thick/Bold text)
    cv2.putText(img, "HELLO", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 5)
    
    input_path = "test_pipeline_input.png"
    cv2.imwrite(input_path, img)
    
    # 3. Simulate Pipeline Steps
    print("1️⃣  Phase 1: Style Analysis (Vision)...")
    # Crop the text area
    roi = img[150:250, 40:200] 
    style_data = analyzer.analyze_roi(roi)
    print(f"   Stylometry: Bold={style_data['is_bold']}, StrokeWidth={style_data['stroke_width']}, HasStroke={style_data.get('has_stroke')}")
    
    print("2️⃣  Phase 2: Font Matching (Brain)...")
    # Simulate LLM saying it's a "SHOUT" because it's big/bold
    bubble_type = "sfx" if style_data['is_bold'] else "speech"
    clean_text = "HOLA" # Translated text
    
    font_name = matcher.match_font(style_data, bubble_type=bubble_type, roi_image=roi, ocr_text="HELLO")
    font_path = matcher.get_font_path(font_name)
    print(f"   Matched Font: {font_name} (Category: {bubble_type})")
    
    print("3️⃣  Phase 3: Physical Rendering (Hand)...")
    bubbles = [{
        "bbox": [40, 150, 200, 250],
        "translation": clean_text,
        "font": font_name,
        "font_path": font_path,
        "style_data": style_data, # Pass style for effects
        "bg_color": (255, 255, 255),
        "text_color": (0, 0, 0),
        "bubble_type": bubble_type,
        "estimated_font_size": style_data['font_size_px'],
        "polygon": [[40,150], [200,150], [200,250], [40,250]]
    }]
    
    output_path = "test_pipeline_output.png"
    success = renderer.render_text(input_path, bubbles, output_path)
    
    if success:
        print("   ✅ Pipeline Success!")
        print(f"   👉 Output generated at {output_path}")
    else:
        print("   ❌ Pipeline Failed during rendering.")

if __name__ == "__main__":
    test_pipeline_e2e()
