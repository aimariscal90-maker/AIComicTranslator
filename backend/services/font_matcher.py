
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

    def match_font(self, style_profile: Dict, bubble_type: str = "speech", roi_image: np.ndarray = None, ocr_text: str = "") -> str:
        """
        [Day 06] Hybrid Font Selection.
        Combines Semantic Analysis (LLM Tone) with Visual Analysis (StyleAnalyzer).
        [Day 07] Adds Visual Similarity (SSIM) refinement.
        """
        is_bold = style_profile.get("is_bold", False)
        bubble_type = bubble_type.lower()
        
        selected_category = "dialogue" # Default
        
        # --- PHASE 1: Category Selection (Semantic) ---
        
        if bubble_type in ["scream", "shout", "sfx"]:
            selected_category = "sfx"
        elif bubble_type in ["narration", "robot", "system"]:
            selected_category = "narrator"
        elif is_bold and style_profile.get("font_size_pt", 10) > 30:
            selected_category = "sfx"
        elif style_profile.get("is_inverted", False):
            selected_category = "narrator"
            
        # Fallback if category empty, go to dialogue
        if not self.font_map[selected_category]:
            selected_category = "dialogue"
            
        # If still empty (no fonts at all), return default
        if not self.font_map[selected_category]:
             return "Arial.ttf"

        # --- PHASE 2: Visual Refinement (SSIM) ---
        # If we have the image and text, pick the BEST font in the category
        if roi_image is not None and ocr_text and len(ocr_text) > 1:
            best_font = self._find_visually_closest(roi_image, ocr_text, self.font_map[selected_category], selected_category)
            if best_font:
                return best_font
        
        # Default: Return first in category
        return self.font_map[selected_category][0]

    def _find_visually_closest(self, roi: np.ndarray, text: str, font_list: list, category: str) -> Optional[str]:
        """
        [Day 07] Ghost Rendering & SSIM Comparison.
        Renders the text with each candidate font and compares it to the original ROI.
        """
        try:
            from skimage.metrics import structural_similarity as ssim
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            print("⚠️ scikit-image not installed. Skipping SSIM visual matching.")
            return None

        # 1. Binarize Original ROI (Ground Truth)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # Use Otsu to get strict mask
        _, mask_original = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Resize to standard height for comparison (e.g. 64px height) to speed up
        target_h = 64
        h, w = mask_original.shape
        scale = target_h / h
        target_w = int(w * scale)
        mask_original_resized = cv2.resize(mask_original, (target_w, target_h))
        
        best_score = -1.0
        best_font = None
        
        for font_name in font_list:
            font_path = self.get_font_path(font_name)
            if not font_path: continue
            
            # 2. Ghost Render
            # Create a blank image (black bg, white text to match THRESH_BINARY_INV mask?
            # Wait, mask_original is Text=White, BG=Black (Invariant).
            img_pil = Image.new("L", (target_w, target_h), 0)
            draw = ImageDraw.Draw(img_pil)
            
            try:
                # Load font. Try to fit height.
                # Heuristic: Font size usually ~0.8 of height?
                font_size = int(target_h * 0.8) 
                font = ImageFont.truetype(font_path, font_size)
                
                # Check text size
                bbox = font.getbbox(text)
                fw = bbox[2] - bbox[0]
                fh = bbox[3] - bbox[1]
                
                # Center it
                x = (target_w - fw) // 2
                y = (target_h - fh) // 2
                
                draw.text((x, y), text, font=font, fill=255)
                
                # Convert to numpy
                mask_candidate = np.array(img_pil)
                
                # 3. Compare (SSIM)
                # win_size must be smaller than image min dimension (7 for 64px is fine)
                score, _ = ssim(mask_original_resized, mask_candidate, full=True, data_range=255)
                
                if score > best_score:
                    best_score = score
                    best_font = font_name
                    
            except Exception as e:
                continue
                
        if best_score > 0.3: # Threshold to accept a visual match
            print(f"   👁️ [SSIM] Winner: {best_font} (Score: {best_score:.2f})")
            return best_font
            
        return None

    def get_font_path(self, font_name: str) -> Optional[str]:
        """
        Resolves absolute path for a font name.
        """
        for category, fonts in self.font_map.items():
            if font_name in fonts:
                return os.path.join(self.fonts_dir, category, font_name)
        return None
