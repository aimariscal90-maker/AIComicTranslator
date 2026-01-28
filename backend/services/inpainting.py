import torch
import os
import cv2
import numpy as np
from PIL import Image

class TextRemover:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TextRemover, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Inpainting Service using device: {self.device}")
        
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "big-lama.pt")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"LaMa model not found at {model_path}")
            
        print(f"Loading LaMa model from {model_path}...")
        try:
            self.model = torch.jit.load(model_path, map_location=self.device)
            self.model.eval()
            print("LaMa model loaded successfully.")
        except Exception as e:
            print(f"Error loading LaMa model: {e}")
            self.model = None

    def remove_text(self, image_path, bboxes, output_path, mask_mode='bubble', inpaint_mode='lama', fast_mode=False):
        """
        Borra el texto de la imagen.
        mask_mode='bubble': Borra todo el poligono del globo.
        mask_mode='text': Borra solo las cajas de palabras (word_boxes) dentro del globo.
        inpaint_mode='lama' | 'telea' | 'fill'
        """
        # Backward compatibility for fast_mode
        if fast_mode: 
            inpaint_mode = 'telea'

        if inpaint_mode == 'lama' and self.model is None:
            print("Model not loaded, skipping inpainting.")
            return
            
        # 1. Leer Imagen y crear Mascara
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w = img.shape[:2]
        
        mask = np.zeros((h, w), dtype=np.float32)
        
        for bubble in bboxes:
            if mask_mode == 'text' and 'word_boxes' in bubble and bubble['word_boxes']:
                # Modo Fino: Usar coordenadas de palabras
                for wb in bubble['word_boxes']:
                    pts = np.array(wb, np.int32)
                    cv2.fillPoly(mask, [pts], 1.0)
            else:
                # --- ESTRATEGIA: SOLO TEXTO (Adaptive) ---
                x1, y1, x2, y2 = map(int, bubble['bbox'])
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                
                if x2 > x1 and y2 > y1:
                    roi = img[y1:y2, x1:x2]
                    gray_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
                    mean_brightness = np.mean(gray_roi)
                    text_mask_roi = None
                    
                    if mean_brightness > 100:
                        text_mask_roi = cv2.adaptiveThreshold(
                            gray_roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                            cv2.THRESH_BINARY_INV, 21, 10
                        )
                    else:
                        _, text_mask_roi = cv2.threshold(gray_roi, 150, 255, cv2.THRESH_BINARY)
                        
                    kernel_clean = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
                    text_mask_roi = cv2.morphologyEx(text_mask_roi, cv2.MORPH_OPEN, kernel_clean)
                    mask[y1:y2, x1:x2] = text_mask_roi.astype(np.float32) / 255.0
                    
                    if np.sum(text_mask_roi) < 10:
                            print(f"[INPAINT WARNING] No text detected in bubble {x1},{y1}. Skipping mask.")
                
        # Dilatar mascara
        if mask_mode == 'text' or True: 
             MASK_PADDING = 3 
             iter_dil = 2 
        else:
             MASK_PADDING = 5
             iter_dil = 1
             
        kernel = np.ones((MASK_PADDING, MASK_PADDING), np.uint8) 
        dilated_mask = cv2.dilate(mask, kernel, iterations=iter_dil)

        # --- SAFE CONSTRAINT (Protect Borders) ---
        # Create a mask of the "Allowed Area" (Inside Bubbles)
        # and intersect with the dilated mask to prevent bleeding onto borders.
        
        constraint_mask = np.zeros((h, w), dtype=np.uint8)
        
        for bubble in bboxes:
            # Prefer Polygon if available
            if 'polygon' in bubble and len(bubble['polygon']) > 3:
                pts = np.array(bubble['polygon'], np.int32)
                cv2.fillPoly(constraint_mask, [pts], 255)
            else:
                # Fallback to bbox
                x1, y1, x2, y2 = map(int, bubble['bbox'])
                # Erode bbox slightly to be safe
                cv2.rectangle(constraint_mask, (x1+2, y1+2), (x2-2, y2-2), 255, -1)
        
        # Erode Constraint Mask (IMPORTANT)
        # We shrink the allowed area by ~2px to ensure we don't touch the black border
        kernel_safe = np.ones((5,5), np.uint8) 
        constraint_mask = cv2.erode(constraint_mask, kernel_safe, iterations=1)
        
        # Apply Intersection
        # logical_and requires binary, but we are working with float mask 0..1
        
        constraint_float = constraint_mask.astype(np.float32) / 255.0
        # Intersect: Only allow mask where constraint is 1.0
        final_mask = cv2.bitwise_and(dilated_mask, dilated_mask, mask=constraint_mask)
        
        # Update main mask
        mask = final_mask
        
        # --- MODE 1: SOLID COLOR FILL (Smart Flood Fill) ---
        if inpaint_mode == 'fill':
            print("[INPAINTING] Mode: Solid Color Fill (Smart Flood)")
            result_img = img.copy()
            
            # Apply fill for each bubble
            for i, bubble in enumerate(bboxes):
                x1, y1, x2, y2 = map(int, bubble['bbox'])
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                
                if x2 <= x1 or y2 <= y1: continue
                
                # Get ROI
                roi = result_img[y1:y2, x1:x2]
                
                # 1. Create Layout Mask (Full Bubble) from Polygon
                layout_mask = np.zeros((y2-y1, x2-x1), dtype=np.uint8)
                
                if 'polygon' in bubble and len(bubble['polygon']) > 3:
                     # Translate polygon to ROI coordinates
                     poly_pts = np.array(bubble['polygon'], np.int32)
                     poly_pts = poly_pts - np.array([x1, y1])
                     cv2.fillPoly(layout_mask, [poly_pts], 255)
                else:
                     cv2.rectangle(layout_mask, (0,0), (x2-x1, y2-y1), 255, -1)
                
                # 2. Determine Fill Color (Median of Layout Mask)
                fill_color = (255, 255, 255) 
                coords = np.where(layout_mask == 255)
                if len(coords[0]) > 0:
                    try:
                        bg_pixels = roi[coords[0], coords[1]]
                        median_bg = np.median(bg_pixels, axis=0).astype(int)
                        fill_color = tuple(map(int, median_bg))
                    except: pass
                    
                # 3. Create Smart Mask (Geometric Erosion Only)
                # We simply erode the layout mask to be safe from borders.
                # No thresholding based on brightness, because that protects the text too!
                
                kernel_erode = np.ones((5,5), np.uint8)
                erosion_iter = 1
                
                # Dynamic erosion based on bubble size? 
                # If bubble is tiny, 5px might kill it.
                if (x2-x1) < 50 or (y2-y1) < 50:
                    kernel_erode = np.ones((3,3), np.uint8)
                
                final_fill_mask = cv2.erode(layout_mask, kernel_erode, iterations=erosion_iter)
                
                # 4. Apply Fill
                color_layer = np.full_like(roi, fill_color)
                mask_bool = final_fill_mask > 0
                roi[mask_bool] = color_layer[mask_bool]
                
                result_img[y1:y2, x1:x2] = roi

            result_bgr = cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR)
            cv2.imwrite(output_path, result_bgr)
            return output_path

        # --- MODE 2: FAST (OpenCV Telea) ---
        if inpaint_mode == 'telea':
            print("[INPAINTING] Mode: OpenCV Telea")
            try:
                mask_8u = (mask * 255).astype(np.uint8)
                inpainted = cv2.inpaint(img, mask_8u, 3, cv2.INPAINT_TELEA)
                result_bgr = cv2.cvtColor(inpainted, cv2.COLOR_RGB2BGR)
                cv2.imwrite(output_path, result_bgr)
                return output_path
            except Exception as e:
                print(f"[INPAINTING] Fast mode failed: {e}. Falling back to LaMa.")
        
        # --- MODE 3: LAMA (Smart Tiling) ---
        # Default fallback
        
        result_img = img.copy() # Work on a copy
        
        # Determine padding for context (pixels)
        CONTEXT_PAD = 120 
        
        for i, bubble in enumerate(bboxes):
            # Coordinates
            x1, y1, x2, y2 = map(int, bubble['bbox'])
            
            # Add padding for context (LaMa needs context to hallucinate background)
            bx1 = max(0, x1 - CONTEXT_PAD)
            by1 = max(0, y1 - CONTEXT_PAD)
            bx2 = min(w, x2 + CONTEXT_PAD)
            by2 = min(h, y2 + CONTEXT_PAD)
            
            # Crop
            crop_img = result_img[by1:by2, bx1:bx2] # Use result_img to support overlapping repairs
            crop_mask = mask[by1:by2, bx1:bx2]
            
            # Skip if mask is empty in this region
            if np.sum(crop_mask) == 0:
                continue
                
            # Prepare LaMa Input (Divisible by 8)
            def pad_to_divisible(arr, divisor=8):
                ch, cw = arr.shape[:2]
                h_pad = (divisor - ch % divisor) % divisor
                w_pad = (divisor - cw % divisor) % divisor
                if h_pad == 0 and w_pad == 0: return arr, 0, 0
                
                # Reflect padding best for textures
                pad_width = ((0, h_pad), (0, w_pad), (0, 0)) if arr.ndim == 3 else ((0, h_pad), (0, w_pad))
                return np.pad(arr, pad_width, mode='reflect'), h_pad, w_pad

            img_p, hp, wp = pad_to_divisible(crop_img)
            mask_p, _, _ = pad_to_divisible(crop_mask)
            
            # Tensor Conversion
            img_t = torch.from_numpy(img_p).permute(2, 0, 1).float().div(255.0).to(self.device).unsqueeze(0)
            mask_t = torch.from_numpy(mask_p).float().to(self.device).unsqueeze(0).unsqueeze(0) # 1x1xHxW
            
            try:
                with torch.no_grad():
                    inpainted_t = self.model(img_t, mask_t)
                    # Handle tuple return
                    if isinstance(inpainted_t, (list, tuple)):
                        inpainted_t = inpainted_t[0]
                
                # Post-process
                inpainted_np = inpainted_t[0].permute(1, 2, 0).cpu().numpy()
                inpainted_np = np.clip(inpainted_np * 255, 0, 255).astype(np.uint8)
                
                # Unpad (Remove the extra padding we added for mod 8)
                real_h, real_w = crop_img.shape[:2]
                final_crop = inpainted_np[:real_h, :real_w]
                
                # Paste back
                # Update result_img
                result_img[by1:by2, bx1:bx2] = final_crop
                
            except Exception as e:
                print(f"[INPAINT ERROR] Failed on bubble {i}: {e}")
                
        # 3. Final Save
        result_bgr = cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, result_bgr)
        print(f"[INPAINTING] Smart Tiling Complete. Saved to {output_path}")
        return output_path
