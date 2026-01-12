import os
import glob
from PIL import Image, ImageDraw, ImageFont
import re

# Configuration
FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "font_patterns")
TEST_TEXT = "HOLA MUNDO"
IMAGE_SIZE = (300, 100)
FONT_SIZE = 40

def generate_patterns():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Find all font files
    font_files = []
    for root, dirs, files in os.walk(FONTS_DIR):
        for file in files:
            if file.lower().endswith((".ttf", ".otf")):
                font_files.append(os.path.join(root, file))
    
    if not font_files:
        print(f"No fonts found in {FONTS_DIR}. Please add .ttf or .otf files.")
        return

    print(f"Found {len(font_files)} fonts. Generating patterns...")

    for font_path in font_files:
        try:
            # Load Font
            font = ImageFont.truetype(font_path, FONT_SIZE)
            
            # Create Image (Black background, White text to match our Binarization logic)
            # Or White background Black text?
            # StyleAnalyzer expects "Text" to be separated. 
            # Let's clean standard: White BG, Black Text (classic document)
            img = Image.new("RGB", IMAGE_SIZE, (255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Center Text
            # getbbox returns (left, top, right, bottom)
            bbox = font.getbbox(TEST_TEXT)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
            x = (IMAGE_SIZE[0] - text_w) // 2
            y = (IMAGE_SIZE[1] - text_h) // 2
            
            draw.text((x, y), TEST_TEXT, font=font, fill=(0, 0, 0))
            
            # Save
            # Name: dialogue_AnimeAce.png
            category = os.path.basename(os.path.dirname(font_path))
            font_name = os.path.splitext(os.path.basename(font_path))[0]
            output_filename = f"{category}_{font_name}.png"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            img.save(output_path)
            print(f"Generated: {output_filename}")
            
        except Exception as e:
            print(f"Error processing {font_path}: {e}")

if __name__ == "__main__":
    generate_patterns()
