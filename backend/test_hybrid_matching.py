import sys
import os

# Add current dir to path to import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.font_matcher import FontMatcher

def test_hybrid_matching():
    matcher = FontMatcher()
    
    print("🧪 --- TESTING HYBRID FONT MATCHING (Day 06) ---\n")
    
    # Test Cases
    scenarios = [
        {
            "name": "Normal Dialogue",
            "text": "Hello world",
            "type": "speech",
            "style": {"is_bold": False, "text_color": "#000000"},
            "expected_category": "dialogue"
        },
        {
            "name": "Scream (LLM Detected)",
            "text": "DIE!!!!",
            "type": "scream",
            "style": {"is_bold": True, "text_color": "#000000"},
            "expected_category": "sfx"
        },
        {
            "name": "Narration (LLM Detected)",
            "text": "Meanwhile...",
            "type": "narration",
            "style": {"is_bold": True, "text_color": "#000000", "is_inverted": True}, # White on black
            "expected_category": "narrator"
        },
        {
            "name": "Visual Override (LLM says speech, but LOOKS like shout)",
            "text": "WHAT?",
            "type": "speech", # LLM missed it
            "style": {"is_bold": True, "font_size_pt": 50, "density": 0.5}, # Big and Bold
            "expected_category": "sfx"
        }
    ]
    
    for case in scenarios:
        print(f"📋 Scenario: {case['name']}")
        print(f"   Input Tone: {case['type'].upper()}")
        print(f"   Input Style: {case['style']}")
        
        # Run Matcher
        font_name = matcher.match_font(case['style'], bubble_type=case['type'])
        font_path = matcher.get_font_path(font_name)
        category = "unknown"
        if font_path:
            category = os.path.basename(os.path.dirname(font_path))
            
        print(f"   👉 Selected Font: {font_name} (Category: {category})")
        
        # Verification
        if category == case['expected_category']:
            print("   ✅ PASS")
        else:
            print(f"   ❌ FAIL (Expected {case['expected_category']}, got {category})")
        print("-" * 40)

if __name__ == "__main__":
    test_hybrid_matching()
