import sys
import os
import cv2
import numpy as np
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.renderer import TextRenderer

def test_physical_rendering():
    print("\n🎨 --- TESTING DAY 08: PHYSICAL RENDERING (Rotation & Spacing) ---\n")
    
    renderer = TextRenderer()
    
    # 1. Mock Data
    # A bubble that needs rotation
    bubbles = [
        {
            "bbox": [50, 50, 350, 250],
            "translation": "ROTATED TEXT EXAMPLE",
            "font": "ComicNeue",
            "style_data": {
                "rotation_angle": -15, # Rotated 15 degrees CCW (or CW depending on system)
                "line_spacing": 1.5,   # Wide spacing
                "is_bold": True
            },
            "bg_color": (255, 255, 255),
            "text_color": (0, 0, 0),
            "polygon": [[50,50], [350,50], [350,250], [50,250]] # Rect
        }
    ]
    
    # 2. Create Base Image
    img = Image.new("RGB", (400, 300), (100, 100, 100)) # Grey background
    input_path = "test_render_input.png"
    output_path = "test_render_output.png"
    img.save(input_path)
    
    # 3. Render
    print(f"   🖼️ Rendering to {output_path}...")
    success = renderer.render_text(input_path, bubbles, output_path)
    
    if success:
        print("   ✅ Render Success!")
        print(f"   👉 Check {output_path}. Text should be TILTED -15 degrees.")
    else:
        print("   ❌ Render Failed.")

if __name__ == "__main__":
    test_physical_rendering()
