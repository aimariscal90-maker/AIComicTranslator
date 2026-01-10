
import cv2
import numpy as np
import os
from services.style_analyzer import StyleAnalyzer
from services.renderer import TextRenderer
from PIL import Image

def test_full_pipeline_geometry():
    print("🧪 Creating Synthetic Test Image...")
    # 1. Create Image with BIG text and SMALL text
    img = np.full((400, 600, 3), 255, dtype=np.uint8)
    
    # BIG TEXT (Shout) - Approx 60px height
    cv2.putText(img, "SHOUT", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 0), 5)
    bbox_big = [45, 30, 350, 120] # Roughly around the text
    cv2.rectangle(img, (45, 30), (350, 120), (200, 200, 200), 1)
    
    # SMALL TEXT (Whisper) - Approx 15px height
    cv2.putText(img, "whisper", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    bbox_small = [45, 280, 250, 320]
    cv2.rectangle(img, (45, 280), (250, 320), (200, 200, 200), 1)
    
    cv2.imwrite("test_geometry_input.png", img)
    
    # 2. Run Style Analyzer
    print("🔍 Running Style Analyzer...")
    analyzer = StyleAnalyzer()
    
    style_big = analyzer.analyze_roi(img, bbox_big)
    print(f"   [BIG] Detected Size: {style_big.get('estimated_font_size')}px")
    
    style_small = analyzer.analyze_roi(img, bbox_small)
    print(f"   [SMALL] Detected Size: {style_small.get('estimated_font_size')}px")
    
    # 3. Mock Bubbles with detected info
    bubbles = [
        {
            'bbox': bbox_big,
            'translation': 'GRITO', # Spanish translation
            'text_color': style_big.get('text_color', '#000000'),
            'estimated_font_size': style_big.get('estimated_font_size'),
            'bg_color': (255, 255, 255)
        },
        {
            'bbox': bbox_small,
            'translation': 'susurro',
            'text_color': style_small.get('text_color', '#000000'),
            'estimated_font_size': style_small.get('estimated_font_size'),
            'bg_color': (255, 255, 255)
        }
    ]
    
    # 4. Render
    print("✍️  Rendering Result...")
    renderer = TextRenderer()
    renderer.render_text("test_geometry_input.png", bubbles, "test_geometry_output.png")
    
    print("✅ Done! Check 'test_geometry_output.png'.")
    print("   You should see 'GRITO' rendered huge and 'susurro' rendered tiny.")

if __name__ == "__main__":
    test_full_pipeline_geometry()
