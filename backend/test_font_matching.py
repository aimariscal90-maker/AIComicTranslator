
from services.font_matcher import FontMatcher
import numpy as np

def test_heuristics():
    matcher = FontMatcher()
    
    print("\n--- Testing Font Heuristics ---")
    
    # CASE 1: Normal Dialogue
    style_normal = {"density": 0.20, "is_bold": False, "is_inverted": False}
    font_normal = matcher.match_font(None, style_normal)
    print(f"CASE 1 (Dialogue): {font_normal} [Expected: ComicNeue-Bold.ttf]")
    
    # CASE 2: SHOUT / SFX
    style_shout = {"density": 0.50, "is_bold": True, "is_inverted": False}
    font_shout = matcher.match_font(None, style_shout)
    print(f"CASE 2 (Shout): {font_shout} [Expected: Bangers-Regular.ttf]")
    
    # CASE 3: Narrator (Inverted)
    style_narrator = {"density": 0.30, "is_bold": False, "is_inverted": True}
    font_narrator = matcher.match_font(None, style_narrator)
    print(f"CASE 3 (Narrator): {font_narrator} [Expected: Roboto-Medium.ttf]")

if __name__ == "__main__":
    test_heuristics()
