import sys
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.font_matcher import FontMatcher

def test_ssim_matching():
    matcher = FontMatcher()
    
    print("\n👁️ --- TESTING DAY 07: VISUAL SIMILARITY (SSIM) ---\n")
    
    # 1. Setup: Ensure we have fonts to test
    # Let's pick a font we know exists in 'sfx' or 'dialogue'
    # We saw 'badaboom-bb.regular.ttf' in logs earlier in 'sfx'
    # And 'Action Man.ttf' in 'dialogue'
    
    target_font_name = "badaboom-bb.regular.ttf" 
    target_category = "sfx"
    target_text = "SMASH!"
    
    font_path = matcher.get_font_path(target_font_name)
    if not font_path:
        # Fallback to whatever is available
        if matcher.font_map['dialogue']:
            target_font_name = matcher.font_map['dialogue'][0]
            target_category = "dialogue"
            target_text = "Hello World"
            font_path = matcher.get_font_path(target_font_name)
        else:
            print("❌ No fonts found to test!")
            return

    print(f"🎯 Target: We will generate an image using '{target_font_name}'")
    print(f"   Goal: FontMatcher should identify this font among others in '{target_category}'")

    # 2. Generate Synthetic "Comic Crop" (Ground Truth)
    img_size = (200, 100)
    img_pil = Image.new("RGB", img_size, (255, 255, 255)) # White bg
    draw = ImageDraw.Draw(img_pil)
    
    try:
        font = ImageFont.truetype(font_path, 60)
        # Center text
        bbox = font.getbbox(target_text)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((200-tw)//2, (100-th)//2), target_text, font=font, fill=(0,0,0)) # Black text
    except Exception as e:
        print(f"❌ Failed to render target image: {e}")
        return

    # Convert to OpenCV format (BGR)
    roi_image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
    # Save for debug
    cv2.imwrite("test_ssim_target.png", roi_image)
    print("   📸 Saved 'test_ssim_target.png' for visual check.")

    # 3. Run Matcher
    # We simulate that the LLM/StyleAnalyzer categorized this roughly
    # e.g. "sfx" (if it's badaboom) or "speech"
    bubble_type = "sfx" if target_category == "sfx" else "speech"
    
    print(f"   🤖 Running match_font(text='{target_text}', type='{bubble_type}')...")
    
    # Dummy style profile (not strictly needed for SSIM path, but match_font expects it)
    style = {"is_bold": True, "text_color": "#000000"} 
    
    matched_font = matcher.match_font(
        style, 
        bubble_type=bubble_type, 
        roi_image=roi_image, 
        ocr_text=target_text
    )
    
    # 4. Verification
    print(f"\n👉 Result: {matched_font}")
    
    if matched_font == target_font_name:
        print("✅ SUCCESS! The system visually recognized the font via SSIM.")
    else:
        print(f"❌ FAILURE. Expected {target_font_name}, got {matched_font}.")
        print("   (Note: Low SSIM scores might cause fallback to default)")

if __name__ == "__main__":
    test_ssim_matching()
