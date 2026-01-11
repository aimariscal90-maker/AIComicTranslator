import cv2
import numpy as np
from typing import Dict, Any, Tuple, List
from sklearn.cluster import KMeans

class StyleAnalyzer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StyleAnalyzer, cls).__new__(cls)
        return cls._instance

    def analyze_roi(self, image: np.ndarray, bbox: list) -> Dict[str, Any]:
        """
        [Day 01] Analysis Entry Point.
        Extracts pixel-level data from a cropped text bubble.
        """
        # 1. Extract ROI
        x1, y1, x2, y2 = map(int, bbox)
        h, w = image.shape[:2]
        x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            return self._get_default_style()

        roi = image[y1:y2, x1:x2]
        
        # 2. Binarization (Otsu's Method) - The Core of Day 01
        # We need to answer: Where is the text?
        binary_mask, is_inverted = self._binarize_otsus(roi)
        
        # 3. Contour Extraction - Identifying Letters
        contours = self.get_text_contours(binary_mask)
        
        # 4. Basic Attributes
        text_color = self._detect_text_color(roi, binary_mask)
        font_size = self._estimate_font_size(contours)
        
        # Calculate Density explicitly for frontend
        if binary_mask.size > 0:
            text_pixels = cv2.countNonZero(binary_mask)
            density = text_pixels / binary_mask.size
        else:
            density = 0.0
            
        is_bold = density > 0.30

        # Construct the "Style Cloner" JSON Object
        return {
            # Day 01 - Pixel Data
            "has_content": len(contours) > 0,
            "text_color": text_color,
            "stroke_color": "#FFFFFF", 
            "stroke_width": 0,       
            
            # Font Info
            "font_category": "normal",
            "font_match": "AnimeAce.ttf",
            
            # Style Flags
            "is_bold": bool(is_bold),
            "density": float(density), # RESTORED: Required by Frontend
            "is_italic": False,
            
            # Geometry
            "rotation_angle": 0.0,
            "line_spacing_ratio": 1.0,
            "font_size_px": int(font_size),
            "estimated_font_size": int(font_size), # RESTORED: Compatibility alias
            
            # Debug/Internal
            "is_inverted": bool(is_inverted),
            "contours_count": len(contours)
        }

    def _binarize_otsus(self, roi: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        [Day 01 Task] Implement Otsu's Binarization.
        Separates text (foreground) from background.
        Returns:
            - mask: Binary image where Text = 255 (White), Background = 0 (Black).
            - is_inverted: True if original text was White on Black.
        """
        if roi.size == 0: return np.zeros((1,1), np.uint8), False

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # 1. Apply Otsu's Thresholding
        # Otsu automatically finds the best split value between "Dark" and "Light".
        # It returns the threshold used (thresh_val) and the binary image.
        # cv2.THRESH_BINARY: Pixel > Thresh -> 255 (Light), Pixel < Thresh -> 0 (Dark)
        thresh_val, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 2. Determine Polarity (Is text Black or White?)
        # We assume the Background is the DOMINANT area (most common pixel).
        # Count white vs black pixels in the binary image.
        num_white = cv2.countNonZero(binary)
        num_black = binary.size - num_white
        
        # If White pixels are the majority (> 50%), then Background is White.
        # This means Text is Black (the minority).
        # In 'binary', Background(White) is 255. Text(Black) is 0.
        # WE WANT TEXT TO BE 255. So we must INVERT.
        if num_white > num_black:
            final_mask = cv2.bitwise_not(binary)
            is_inverted = False # Standard: Dark text on Light BG
        else:
            # If Black pixels are the majority, Background is Black.
            # This means Text is White (the minority).
            # In 'binary', Background(Black) is 0. Text(White) is 255.
            # This is already what we want.
            final_mask = binary
            is_inverted = True # Inverted: Light text on Dark BG
            
        return final_mask, is_inverted

    def get_text_contours(self, binary_mask: np.ndarray) -> List[np.ndarray]:
        """
        [Day 01 Task] Get contour of each individual letter.
        """
        # Find contours on the text mask (where Text=255)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        valid_contours = []
        h_img, w_img = binary_mask.shape
        
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Simple noise filtering
            # Ignore tiny dots (noise)
            if w < 3 or h < 5: continue
            
            # Ignore huge blobs (likely panel borders or full background)
            if w > w_img * 0.95 and h > h_img * 0.95: continue
            
            valid_contours.append(cnt)
            
        return valid_contours

    def _detect_text_color(self, roi: np.ndarray, mask: np.ndarray) -> str:
        """Helper to sample text color."""
        # TODO: Refine in Day 02
        try:
            coords = np.where(mask == 255)
            if len(coords[0]) < 5: return "#000000"
            pixels = roi[coords[0], coords[1]]
            kmeans = KMeans(n_clusters=1, n_init=3).fit(pixels)
            b, g, r = kmeans.cluster_centers_[0].astype(int)
            return "#{:02x}{:02x}{:02x}".format(r, g, b)
        except:
            return "#000000"

    def _estimate_font_size(self, contours: List[np.ndarray]) -> int:
        if not contours: return 20
        heights = [cv2.boundingRect(c)[3] for c in contours]
        return int(np.median(heights) / 0.7)

    def _is_bold(self, mask: np.ndarray, contours: List[np.ndarray]) -> bool:
        if mask.size == 0: return False
        text_pixels = cv2.countNonZero(mask)
        density = text_pixels / mask.size
        return density > 0.30

    def _get_default_style(self):
        return {
            "has_content": False,
            "text_color": "#000000",
            "stroke_color": "#FFFFFF",
            "stroke_width": 0,
            "font_category": "normal",
            "font_match": "Arial.ttf",
            "is_bold": False,
            "is_italic": False,
            "rotation_angle": 0,
            "line_spacing_ratio": 1.0,
            "font_size_px": 20,
            "is_inverted": False,  
            "contours_count": 0
        }
