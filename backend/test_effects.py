import sys
import os
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.renderer import TextRenderer

def test_effects_rendering():
    print("\n✨ --- TESTING DAY 09: EFFECT SIMULATION (Faux Bold & Outline) ---\n")
    
    renderer = TextRenderer()
    
    # Mock Data
    bubbles = [
        {
            "bbox": [50, 50, 250, 150],
            "translation": "FAUX BOLD",
            "font": "ComicNeue",
            "style_data": {
                "is_bold": True,
                "has_stroke": False
            },
            "bg_color": (200, 200, 200),
            "text_color": (0, 0, 0), # Black text
            "polygon": [[50,50], [250,50], [250,150], [50,150]]
        },
        {
            "bbox": [50, 200, 250, 300],
            "translation": "STROKE FX",
            "font": "Bangers", # SFX Font
            "bubble_type": "sfx",
            "style_data": {
                "is_bold": True,
                "has_stroke": True,
                "stroke_color": "#FF0000" # Red Stroke
            },
            "bg_color": (50, 50, 50), # Dark bg
            "text_color": (255, 255, 255), # White text
            "polygon": [[50,200], [250,200], [250,300], [50,300]]
        }
    ]
    
    # Create Canvas
    img = Image.new("RGB", (300, 400), (100, 100, 100))
    input_path = "test_effects_input.png"
    output_path = "test_effects_output.png"
    img.save(input_path)
    
    # Render
    print(f"   🖼️ Rendering to {output_path}...")
    success = renderer.render_text(input_path, bubbles, output_path)
    
    if success:
        print("   ✅ Render Success!")
        print(f"   👉 Check {output_path}:")
        print("      1. Top box: Black text should look marginally thicker (Bold).")
        print("      2. Bottom box: White text should have a RED OUTLINE.")
    else:
        print("   ❌ Render Failed.")

if __name__ == "__main__":
    test_effects_rendering()
