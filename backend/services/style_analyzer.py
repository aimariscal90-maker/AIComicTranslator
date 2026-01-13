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

    # [Day 13] Updated Signature
    def analyze_roi(self, image: np.ndarray, bbox: list, polygon: list = None) -> Dict[str, Any]:
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
        
        # [Day 13] Pre-Processing: Mask Background used Mean Bubble Color
        # If we have a polygon, we replace the OUTSIDE (detected noise) with the MEAN COLOR of the INSIDE.
        # Why? Because Otsu's defaults to separating "Dark Background" vs "Light Bubble".
        # We want it to separate "Light Bubble" vs "White Text".
        # By making the Background = Bubble Color, the only variance left is Text vs Bubble.
        poly_mask = None
        if polygon and len(polygon) > 2:
            h_roi, w_roi = roi.shape[:2]
            poly_mask = np.zeros((h_roi, w_roi), dtype=np.uint8)
            local_pts = np.array([[p[0]-x1, p[1]-y1] for p in polygon], dtype=np.int32)
            cv2.fillPoly(poly_mask, [local_pts], 255)
            
            # Calculate mean color inside mask
            mean_val = cv2.mean(roi, mask=poly_mask)[:3]
            mean_color = np.array(mean_val, dtype=np.uint8)
            
            # Fill outside with mean color
            bg_fill = np.full_like(roi, mean_color)
            roi = np.where(poly_mask[..., None] == 255, roi, bg_fill)
        
        # 2. Binarization (Otsu's Method) - The Core of Day 01
        # We need to answer: Where is the text?
        binary_mask, is_inverted = self._binarize_otsus(roi)
        
        # Re-Apply Clean Mask to result (to cut straight transitions)
        if poly_mask is not None:
             binary_mask = cv2.bitwise_and(binary_mask, binary_mask, mask=poly_mask)
        
        # 3. Contour Extraction - Identifying Letters
        contours = self.get_text_contours(binary_mask)
        
        # 4. Basic Attributes
         
        # 3. Analyze Color
        text_color_hex = self._analyze_color(roi, binary_mask, is_inverted)
        
        # 4. Analyze Stroke
        stroke_color, stroke_width = self._analyze_stroke(roi, binary_mask, text_color_hex)
        
        # [Day 03] Geometry (Size & Leading)
        geo_data = self._analyze_geometry(contours)
        
        # [Day 04] Weight (Bold) & Angle (Italic/Rotation)
        weight_data = self._analyze_weight(binary_mask)
        angle_data = self._analyze_angle(contours)

        # Construct the "Style Cloner" JSON Object
        return {
            # Day 01 - Pixel Data
            "has_content": len(contours) > 0,
            
            # Day 02 - Color & Stroke
            "text_color": text_color_hex,
            "bg_color": self._analyze_background(roi, binary_mask), # New
            "stroke_color": stroke_color, 
            "stroke_width": stroke_width,
            "has_stroke": stroke_width > 0,       
            
            # Font Info
            "font_category": "normal",
            "font_match": "AnimeAce.ttf",
            
            # [Day 04] Style Flags
            "is_bold": weight_data["is_bold"],
            "density": weight_data["density"], 
            "is_italic": angle_data["is_italic"],
            "rotation_angle": angle_data["rotation_angle"],
            "is_light": weight_data["is_light"], # New Day 04
            
            # [Day 03] Geometry
            "line_spacing_ratio": geo_data["line_spacing_ratio"],
            "font_size_px": geo_data["font_size_px"],
            "estimated_font_size": geo_data["font_size_px"], # Legacy
            "font_size_pt": geo_data["font_size_pt"],        # New Day 03
            
            # Debug/Internal
            "is_inverted": bool(is_inverted),
            "contours_count": len(contours)
        }

    # ... (Keep _binarize_otsus, get_text_contours, _analyze_color, _analyze_stroke, _analyze_geometry as they are) ...

    def _analyze_weight(self, mask: np.ndarray) -> Dict[str, Any]:
        """
        [Day 04] Analyze Text Weight (Bold/Light) based on Pixel Density.
        """
        if mask.size == 0: 
            return {"is_bold": False, "is_light": False, "density": 0.0}
            
        text_pixels = cv2.countNonZero(mask)
        density = text_pixels / mask.size
        
        # User thresholds: Bold > 0.4, Light < 0.2
        return {
            "is_bold": density > 0.40,
            "is_light": density < 0.20,
            "density": float(density)
        }

    def _analyze_angle(self, contours: List[np.ndarray]) -> Dict[str, Any]:
        """
        [Day 04] Detect Rotation (Text Block) and Shear (Italic/Slant).
        """
        if not contours:
            return {"rotation_angle": 0.0, "is_italic": False}
            
        # 1. Global Rotation (Bubble Rotation)
        # Using all contour points to find the minimum area rectangle
        all_points = np.vstack(contours)
        rot_rect = cv2.minAreaRect(all_points)
        # rot_rect = ((cx, cy), (w, h), angle)
        # OpenCV angle range depends on version, usually -90 to 0 or 0 to 90.
        # We assume standard upright text is ~0 or ~90.
        
        angle = rot_rect[2]
        
        # Normalize angle to -45 to 45 range approximately
        if angle < -45:
            angle = 90 + angle
        if angle > 45:
            angle = angle - 90
            
        # Ignore small fluctuations
        if abs(angle) < 2.0: 
            angle = 0.0
            
        # 2. Italic Detection (Shear)
        # We fit an ellipse to each letter and check the slant.
        # Erect letters | have angle ~0. Italic / have angle ~10-20 deg.
        slant_angles = []
        for cnt in contours:
            # Need at least 5 points for fitEllipse
            if len(cnt) < 5: continue
            
            (ex, ey), (ew, eh), e_angle = cv2.fitEllipse(cnt)
            
            # Filter: Check aspect ratio. Dots/circles don't have slant e_angle reliable.
            if min(ew, eh) == 0: continue
            aspect_ratio = max(ew, eh) / min(ew, eh)
            if aspect_ratio < 1.5: continue # Too round to detect slant
            
            # e_angle is 0 at 12 o'clock? OpenCV docs say:
            # Angle is measured clockwise from X-axis? Or vertical?
            # Typically 0 is Vertical for text contours in this context? 
            # Actually fitEllipse returns 0..180. ~0 and ~180 are vertical-ish if trained that way?
            # Let's collect angles and look for a mode.
            
            # Normalize to deviation from Vertical (90 deg usually in image coords? No, OpenCV is weird)
            # Empirically: Upright 'I' is approx 0 or 180 depending on orientation logic.
            # Italic 'I' leans right.
            
            # Simplification: Just save the raw angle for specific range logic
            slant_angles.append(e_angle)
            
        is_italic = False
        if slant_angles:
            median_slant = np.median(slant_angles)
            # Standard Text (Vertical) usually yields fitEllipse angle near 0 or 180.
            # Italic Text leans. Let's assume Italic if we are consistently in a range like 10-30 deg?
            # Or 160-170?
            
            # "A" (Centroid logic might be better but let's try this)
            # Heuristic: Check if significant number of letters have slant.
            
            # Alternative: Moments
            # mu11 / mu02 correlates to skew.
            
            # Let's use simple logic: If angle is NOT 0 (+/- 5) and NOT 180 (+/- 5)
            # Italic usually leans Right -> Angle ~ 10-20
            
            # Checking if median is in "Italic Range" (e.g. 5 to 25 degrees)
            if 5 < median_slant < 35 or 145 < median_slant < 175:
                is_italic = True
                
        return {
            "rotation_angle": round(angle, 1),
            "is_italic": is_italic
        }

    def _pixels_to_points(self, px: int) -> int:
        """
        [Day 03] Calibration function.
        Standard web/print: 1 px = 0.75 pt (at 96 DPI).
        We might need to calibrate this with 'Golden Test'.
        """
        return int(px * 0.75)

    def _get_default_style(self):
        return {
            "has_content": False,
            "text_color": "#000000",
            "stroke_color": "#FFFFFF",
            "stroke_width": 0,
            "font_category": "normal",
            "font_match": "Arial.ttf",
            "is_bold": False,
            "is_light": False,
            "is_italic": False,
            "rotation_angle": 0,
            "line_spacing_ratio": 1.0,
            "font_size_px": 20,
            "font_size_pt": 15,
            "estimated_font_size": 20,
            "is_inverted": False,  
            "contours_count": 0
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
        thresh_val, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 2. Determine Polarity (Is text Black or White?)
        num_white = cv2.countNonZero(binary)
        num_black = binary.size - num_white
        
        if num_white > num_black:
            final_mask = cv2.bitwise_not(binary)
            is_inverted = False # Standard: Dark text on Light BG
        else:
            final_mask = binary
            is_inverted = True # Inverted: Light text on Dark BG
            
        return final_mask, is_inverted

    def get_text_contours(self, binary_mask: np.ndarray) -> List[np.ndarray]:
        """
        [Day 01 Task] Get contour of each individual letter.
        """
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        valid_contours = []
        h_img, w_img = binary_mask.shape
        
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w < 3 or h < 5: continue
            if w > w_img * 0.95 and h > h_img * 0.95: continue
            valid_contours.append(cnt)
            
        return valid_contours

    def _analyze_color(self, roi: np.ndarray, mask: np.ndarray, is_inverted: bool = False) -> str:
        """
        [Day 02] Extract accurate Text Color using K-Means.
        Erodes mask to capture core ink pixels, ignoring anti-aliasing edges.
        """
        # 1. Erode mask to be safer (pixels strictly inside letters)
        kernel = np.ones((2,2), np.uint8)
        core_mask = cv2.erode(mask, kernel, iterations=1)
        
        # Fallback if text is too thin and disappears
        if cv2.countNonZero(core_mask) < 20:
            core_mask = mask
            
        # 2. Extract Pixels
        coords = np.where(core_mask == 255)
        # Default based on polarity
        default_color = "#FFFFFF" if is_inverted else "#000000"
        
        if len(coords[0]) < 10: return default_color
        
        pixels = roi[coords[0], coords[1]]
        
        # [Fix Day 10] Rule 2: Dark Core (Nuclear Option)
        # If > 30% of the pixels are dark, it's black. Period.
        # This completely ignores pink/green noise on the edges.
        if not is_inverted:
            # Calculate brightness (Mean of BGR) for every pixel
            brightness = np.mean(pixels, axis=1)
            dark_count = np.sum(brightness < 60)
            if len(pixels) > 0 and (dark_count / len(pixels) > 0.30):
                 return "#000000"
        
        # 3. K-Means (k=2) to separate Main Ink vs Shadows/Highlights
        try:
            # We assume the cluster with MORE pixels is the main color
            kmeans = KMeans(n_clusters=2, n_init=3) 
            labels = kmeans.fit_predict(pixels)
            
            # Count labels
            count0 = np.sum(labels == 0)
            count1 = np.sum(labels == 1)
            
            # Cluster Centers
            c0 = kmeans.cluster_centers_[0]
            c1 = kmeans.cluster_centers_[1]
            
            if is_inverted:
                # LIGHT TEXT (White/Yellow) on DARK BG
                # Priority 1: Brightness. Pick the lighter color.
                bright0 = np.mean(c0)
                bright1 = np.mean(c1)
                dominant_idx = 0 if bright0 > bright1 else 1
            else:
                # DARK TEXT (Black/Red) on LIGHT BG
                # Priority 1: Saturation (Vibrance) vs Noise
                sat0 = max(c0) - min(c0)
                sat1 = max(c1) - min(c1)
                
                total_pixels = count0 + count1
                if total_pixels == 0: return "#000000"
                
                ratio0 = count0 / total_pixels
                ratio1 = count1 / total_pixels
                
                # If one cluster is significantly more colorful
                # [Fix Day 10] Rule 1: Increase Saturation Threshold (30 -> 80)
                if abs(sat0 - sat1) > 80:
                    cand_idx = 0 if sat0 > sat1 else 1
                    cand_ratio = ratio0 if cand_idx == 0 else ratio1
                    
                    if cand_ratio > 0.20:
                        # [Fix Day 10] Noise Suppression:
                        # If candidate is Bright (Pink Noise) but alternative is Dark (Black Ink),
                        # reject candidate unless it's the majority (> 50%).
                        cand_color = kmeans.cluster_centers_[cand_idx]
                        other_color = kmeans.cluster_centers_[1 - cand_idx]
                        
                        cand_bright = np.mean(cand_color)
                        other_bright = np.mean(other_color)
                        
                        # If "Saturated" is much brighter than "Unsaturated" (likely Black), 
                        # treat "Saturated" as noise artifacts if it's not dominant.
                        if cand_bright > (other_bright + 40) and other_bright < 80:
                             if cand_ratio > 0.50:
                                 dominant_idx = cand_idx
                             else:
                                 # Fallback to dark color (which is likely the real ink)
                                 dominant_idx = 1 - cand_idx
                        else:
                             dominant_idx = cand_idx
                    else:
                        dominant_idx = 0 if count0 > count1 else 1
                else:
                    dominant_idx = 0 if count0 > count1 else 1

            dominant_color = kmeans.cluster_centers_[dominant_idx].astype(int)
            b, g, r = dominant_color
            
            # [Fix Day 09] Force Dark-Black Snapping
            if not is_inverted and max(b, g, r) < 60:
                 return "#000000"
            
            # [Fix Day 10] Force White Snapping
            if is_inverted and min(b, g, r) > 200:
                 return "#FFFFFF"

            return "#{:02x}{:02x}{:02x}".format(r, g, b)
            
        except Exception as e:
            print(f"K-Means Color failed: {e}")
            return default_color

    def _analyze_background(self, roi: np.ndarray, text_mask: np.ndarray) -> str:
        """
        [Day 02 Refined] Extract Background Color.
        """
        # Inverse of text mask is background
        bg_mask = cv2.bitwise_not(text_mask)
        
        coords = np.where(bg_mask == 255)
        if len(coords[0]) < 10: return "#FFFFFF" # Default White
        
        pixels = roi[coords[0], coords[1]]
        
        # Simple Median often works best for background to ignore noise
        try:
             bg_median = np.median(pixels, axis=0).astype(int)
             b, g, r = bg_median
             return "#{:02x}{:02x}{:02x}".format(r, g, b)
        except:
             return "#FFFFFF"

    def _analyze_stroke(self, roi: np.ndarray, text_mask: np.ndarray, text_color_hex: str) -> Tuple[str, int]:
        """
        [Day 02] Detect if text has an outline (Stroke).
        Logic: Look at pixels *just outside* the text contours. 
        If they form a coherent color ring different from background and text, it's a stroke.
        """
        # 1. Create a "Stroke Area" mask (Donut shape)
        # Dilate text mask (outer ring)
        kernel = np.ones((2,2), np.uint8)
        dilated = cv2.dilate(text_mask, kernel, iterations=3) # ~3px ring
        
        # Subtract original text (donut hole)
        stroke_area_mask = cv2.subtract(dilated, text_mask)
        
        coords = np.where(stroke_area_mask == 255)
        if len(coords[0]) < 20: return "#000000", 0 # No stroke area?
        
        stroke_pixels = roi[coords[0], coords[1]]
        
        # 2. Analyze colors in this ring using K-Means
        try:
            kmeans = KMeans(n_clusters=2, n_init=3)
            labels = kmeans.fit_predict(stroke_pixels)
            
            # Find dominant color in the ring
            count0 = np.sum(labels == 0)
            count1 = np.sum(labels == 1)
            stroke_idx = 0 if count0 > count1 else 1
            best_stroke_color = kmeans.cluster_centers_[stroke_idx].astype(int)
            b, g, r = best_stroke_color
            stroke_hex = "#{:02x}{:02x}{:02x}".format(r, g, b)
            
            # 3. Validation: Is this actually a stroke or just background?
            # Compare with text color
            if stroke_hex == text_color_hex:
                return "#000000", 0 # Ring is same color as text -> Text is just thicker
            
            # Compare with Background (Approximate)
            # We assume BG is the dominant color of the REST of the ROI
            # Let's get a simple BG estimate: Inverse of dilated
            bg_mask = cv2.bitwise_not(dilated)
            bg_coords = np.where(bg_mask == 255)
            
            if len(bg_coords[0]) > 50:
                bg_pixels = roi[bg_coords[0], bg_coords[1]]
                # Quick average of BG
                bg_avg = np.mean(bg_pixels, axis=0).astype(int)
                bg_hex = "#{:02x}{:02x}{:02x}".format(bg_avg[2], bg_avg[1], bg_avg[0])
                
                # Check similarity (Simple Euclidean distance in RGB)
                dist = np.linalg.norm(best_stroke_color - bg_avg)
                if dist < 30: # If stroke color is too close to BG color
                    return "#000000", 0 # It's just background
                    
            # If we survived checks -> It's a Stroke!
            # Estimate width: Basic guess based on iteration count vs coverage
            # Real width calc is harder, let's assume standard 3px for now if detected
            return stroke_hex, 3
            
        except Exception as e:
            print(f"Stroke Analysis failed: {e}")
            return "#000000", 0

    def _analyze_geometry(self, contours: List[np.ndarray]) -> Dict[str, Any]:
        """
        [Day 03] Calculate real height (x-height) and Leading (Line Spacing).
        Includes outlier filtering to ignore background noise/art.
        """
        if not contours:
            return {"font_size_px": 20, "font_size_pt": 15, "line_spacing_ratio": 1.0}
            
        # 1. Get Geometry of all candidates
        raw_boxes = []
        raw_heights = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            raw_boxes.append((x, y, w, h))
            raw_heights.append(h)
            
        # 2. Robust Filtering (Smart Filter)
        # We assume the "Text" is the most common element size.
        # Filter out tiny noise and huge borders relative to the median.
        median_h = np.median(raw_heights)
        
        valid_boxes = []
        valid_heights = []
        
        for i, h in enumerate(raw_heights):
            # Allow some variation (e.g. capital letters vs lowercase)
            # But duplicate borders usually are > 3x height, and noise is < 0.3x
            if h > median_h * 0.4 and h < median_h * 3.0:
                valid_boxes.append(raw_boxes[i])
                valid_heights.append(h)
                
        if not valid_boxes:
            # Fallback to raw if we filtered everything (rare)
            valid_boxes = raw_boxes
            valid_heights = raw_heights
            
        # 3. Refined x-height Estimation
        x_height_px = np.median(valid_heights)
        
        # Convert to full Font Size
        font_size_px = int(x_height_px / 0.7)
        font_size_pt = self._pixels_to_points(font_size_px)
        
        # 4. Leading (Line Spacing) Analysis on VALID boxes only
        if len(valid_boxes) < 2:
            return {"font_size_px": font_size_px, "font_size_pt": font_size_pt, "line_spacing_ratio": 1.2}
            
        # Sort by Y position
        valid_boxes.sort(key=lambda b: b[1])
        
        lines = []
        current_line = [valid_boxes[0]]
        
        for i in range(1, len(valid_boxes)):
            prev_b = current_line[-1]
            curr_b = valid_boxes[i]
            
            prev_cy = prev_b[1] + prev_b[3]/2
            curr_cy = curr_b[1] + curr_b[3]/2
            
            # Threshold: overlap in Y
            if abs(curr_cy - prev_cy) < (x_height_px * 0.8):
                current_line.append(curr_b)
            else:
                lines.append(current_line)
                current_line = [curr_b]
        lines.append(current_line)
        
        # Calculate spacing
        if len(lines) > 1:
            line_centers = []
            for line in lines:
                centers = [b[1] + b[3]/2 for b in line]
                line_centers.append(np.mean(centers))
                
            spacings = np.diff(line_centers)
            avg_leading_px = np.mean(spacings)
            
            # Calibrate Ratio: Real Leading includes the font height itself?
            # Usually Line Height = Average Distance. 
            # Ratio = Line Height / Font Size
            spacing_ratio = avg_leading_px / font_size_px
            
            # Safety clamp for ratio (comics rarely go below 0.8 or above 2.0)
            spacing_ratio = max(0.8, min(spacing_ratio, 2.5))
        else:
            spacing_ratio = 1.2 
            
        return {
            "font_size_px": max(10, font_size_px),
            "font_size_pt": max(8, font_size_pt),
            "line_spacing_ratio": round(spacing_ratio, 2)
        }

    def _pixels_to_points(self, px: int) -> int:
        """
        [Day 03] Calibration function.
        Standard web/print: 1 px = 0.75 pt (at 96 DPI).
        We might need to calibrate this with 'Golden Test'.
        """
        return int(px * 0.75)



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
