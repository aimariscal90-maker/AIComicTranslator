
import os
import cv2
import numpy as np
from typing import Dict, Optional

class FontMatcher:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontMatcher, cls).__new__(cls)
            cls._instance.fonts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")
            cls._instance._load_font_map()
        return cls._instance

    def _load_font_map(self):
        """
        Scans the fonts directory and categorizes them.
        """
        self.font_map = {
            "dialogue": [],
            "sfx": [],
            "narrator": []
        }
        
        if not os.path.exists(self.fonts_dir):
            print(f"⚠️ Fonts directory not found: {self.fonts_dir}")
            return
            
        for category in self.font_map.keys():
            cat_path = os.path.join(self.fonts_dir, category)
            if os.path.exists(cat_path):
                for f in os.listdir(cat_path):
                    if f.endswith(".ttf") or f.endswith(".otf"):
                        self.font_map[category].append(f)
        
        print(f"📚 Font Arsenal Loaded: { {k:len(v) for k,v in self.font_map.items()} }")

    def match_font(self, roi: np.ndarray, style_profile: Dict) -> str:
        """
        Determines the best matching font based on style analysis and heuristics.
        SSIM comparison will be implemented in Day 07.
        """
        is_bold = style_profile.get("is_bold", False)
        density = style_profile.get("density", 0.0)
        
        # Heuristic 1: Shout Detection (High Density + Bold)
        if density > 0.45 or (is_bold and density > 0.35):
            # Probably Sound Effect or Shout
            if self.font_map["sfx"]:
                return self.font_map["sfx"][0] # Return 'Bangers'
        
        # Heuristic 2: Inverted Text (Narrator usually)
        if style_profile.get("is_inverted", False):
            if self.font_map["narrator"]:
                return self.font_map["narrator"][0] # Return 'Roboto'
                
        # Default: Dialogue
        if self.font_map["dialogue"]:
            return self.font_map["dialogue"][0] # Return 'ComicNeue'
            
        return "Arial.ttf" # Ultimate fallback

    def get_font_path(self, font_name: str) -> Optional[str]:
        """
        Resolves absolute path for a font name.
        """
        for category, fonts in self.font_map.items():
            if font_name in fonts:
                return os.path.join(self.fonts_dir, category, font_name)
        return None
