import cv2
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.cluster import KMeans

class StyleAnalyzer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StyleAnalyzer, cls).__new__(cls)
        return cls._instance

    def analyze_roi(self, image: np.ndarray, bbox: list) -> Dict[str, Any]:
        """
        Main entry point. Analyzes a Region of Interest (ROI) defined by bbox
        and returns a dictionary of style attributes.
        """
        x1, y1, x2, y2 = map(int, bbox)
        h, w = image.shape[:2]
        
        # Clamp coordinates
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            return self._get_default_style()

        roi = image[y1:y2, x1:x2]
        
        # 1. Binarization (Isolate Text)
        mask, is_dark_bg = self._binarize_text(roi)
        
        # 2. Pixel Density (Bold Detection)
        density_data = self._analyze_density(mask)
        
        # 3. Color Sampling (Font Color)
        color_data = self._analyze_color(roi, mask)
        
        # 4. Geometry (Font Size)
        geo_data = self._analyze_geometry(mask)
        
        return {
            "has_content": True,
            "is_inverted": is_dark_bg,
            **density_data,
            **color_data,
            **geo_data
        }

    def _binarize_text(self, roi: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Returns binary mask (255=text, 0=bg) and boolean (True if inverted/dark bg).
        Uses Otsu's thresholding with Automatic Background Detection.
        """
        if roi.size == 0: return np.zeros((1,1), np.uint8), False
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Otsu's thresholding
        thresh_val, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Automatic Background Detection
        # Check border pixels (Top/Bottom/Left/Right 2px margin)
        border_mask = np.zeros_like(gray, dtype=bool)
        pad = min(2, roi.shape[0]//2, roi.shape[1]//2)
        if pad > 0:
            border_mask[:pad, :] = True
            border_mask[-pad:, :] = True
            border_mask[:, :pad] = True
            border_mask[:, -pad:] = True
            median_border_val = np.median(gray[border_mask])
        else:
            median_border_val = np.median(gray)
        
        if median_border_val < 100:
             # Background is Dark -> Text is Light
             # In Otsu, Light pixels become 255 (Foreground).
             # So binary mask is already correct (Text=255).
             is_dark_bg = True
             final_mask = binary
        else:
             # Background is Light (High Val) -> Text is Dark (Low Val).
             # In Otsu, Light pixels (BG) become 255. 
             # So we need to INVERT binary to get Text=255.
             is_dark_bg = False
             final_mask = cv2.bitwise_not(binary)

        return final_mask, is_dark_bg

    def _analyze_density(self, mask: np.ndarray) -> Dict[str, Any]:
        """
        Calculates the ratio of text pixels vs total bounding box area.
        High density (> 0.30) usually implies Bold text or Shout (Thick font).
        """
        total_pixels = mask.size
        if total_pixels == 0: return {"density": 0, "is_bold": False}
        
        text_pixels = cv2.countNonZero(mask)
        density = text_pixels / total_pixels
        
        # Heuristic Threshold for Bold
        is_bold = density > 0.30
        
        return {
            "density": float(density),
            "is_bold": is_bold
        }

    def _analyze_color(self, roi: np.ndarray, mask: np.ndarray) -> Dict[str, str]:
        """
        Extracts the dominant color of the TEXT using K-Means on the masked area.
        Returns HEX code.
        """
        # Get pixels where mask is 255 (Text)
        text_coords = np.where(mask == 255)
        
        # Check if we have enough pixels
        if len(text_coords[0]) < 10:
            # Not enough text pixels, return Default (Black or White based on ROI brightness?)
            # Usually if no text detected, we fall back to Black.
            return {"text_color": "#000000"}
            
        # Extract RGB values of text pixels
        # roi is BGR (OpenCV standard)
        text_pixels = roi[text_coords[0], text_coords[1]]
        
        # Use K-Means to find dominant color (k=1)
        # We assume the text is mostly uniform color.
        # If we used mean(), antialiasing edges would dull the color.
        # K-Means approaches the cluster center (the true ink color).
        try:
            kmeans = KMeans(n_clusters=1, n_init=3)
            kmeans.fit(text_pixels)
            dominant_color = kmeans.cluster_centers_[0].astype(int) # [B, G, R]
            
            # Convert BGR to Hex
            b, g, r = dominant_color
            hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
            
            return {"text_color": hex_color}
        except Exception as e:
            print(f"Color analysis failed: {e}")
            return {"text_color": "#000000"}

    def _analyze_geometry(self, mask: np.ndarray) -> Dict[str, int]:
        """
        Estimates font size by finding contours (letters) and calculating median height.
        """
        # Get contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        heights = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Filter noise
            if h < 4 or w < 2: continue 
            # Filter huge blobs (e.g. borders)
            if h > mask.shape[0] * 0.9: continue 
            
            heights.append(h)
            
        if not heights:
            return {"estimated_font_size": 20} # Default safe size
            
        # Median height is a robust estimator of letter size (x-height approx)
        median_height = np.median(heights)
        
        # Convert to estimated full font size (Pillow font size usually includes ascenders/descenders)
        # Typically x-height is 0.5 ~ 0.7 of full size. Let's assume 0.7
        font_size_px = int(median_height / 0.7)
        
        return {
            "estimated_font_size": max(10, font_size_px)
        }

    def _get_default_style(self):
        return {
            "has_content": False,
            "error": "Empty ROI",
            "is_inverted": False,
            "text_color": "#000000",
            "is_bold": False,
            "estimated_font_size": 20
        }
