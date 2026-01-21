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

    def remove_text(self, image_path, bboxes, output_path, mask_mode='bubble', fast_mode=False):
        """
        Borra el texto de la imagen.
        mask_mode='bubble': Borra todo el poligono del globo.
        mask_mode='text': Borra solo las cajas de palabras (word_boxes) dentro del globo.
        """
        if self.model is None:
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
                # OJO: Las word_boxes son relativas al crop (recorte) o absolutas?
                # Revisar ocr.py. Vision devuelve absolutas si se le pasa la imagen entera,
                # pero en main.py le pasamos el crop.
                # IMPORTANTE: En main.py necesitamos ajustar coordenadas si son relativas al crop.
                # ASUMIREMOS aqui que 'word_boxes' vienen ya en coordenadas de la imagen original.
                for wb in bubble['word_boxes']:
                    pts = np.array(wb, np.int32)
                    cv2.fillPoly(mask, [pts], 1.0)
            else:
                # --- ESTRATEGIA: SOLO TEXTO (Adaptive) ---
                # Objetivo: Crear mascara SOLO de las letras.
                # 1. Analizar si el globo es claro (letras negras) u oscuro (letras blancas).
                x1, y1, x2, y2 = map(int, bubble['bbox'])
                    
                # Clamp
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                
                if x2 > x1 and y2 > y1:
                    roi = img[y1:y2, x1:x2]
                    gray_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
                    
                    # Determinar brillo medio
                    mean_brightness = np.mean(gray_roi)
                    
                    text_mask_roi = None
                    
                    if mean_brightness > 100:
                        # TIPO 1: Globo Claro (Fondo Blanco/Gris, Texto Oscuro)
                        # Buscamos pixeles oscuros (< umbral)
                        # Adaptive Threshold es mejor para iluminacion variable
                        text_mask_roi = cv2.adaptiveThreshold(
                            gray_roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                            cv2.THRESH_BINARY_INV, 21, 10
                        )
                    else:
                        # TIPO 2: Globo Oscuro (Fondo Negro, Texto Blanco)
                        # Buscamos pixeles claros (> umbral)
                        # Invertimos la imagen para que el texto blanco sea negro, luego threshold inv
                        # O simplemente threshold normal: Texto blanco (255) -> Mascara (255)
                        _, text_mask_roi = cv2.threshold(gray_roi, 150, 255, cv2.THRESH_BINARY)
                        
                    # Limpieza Morfologica:
                    # 1. Eliminar ruido diminuto (puntos) con OPEN
                    # 2. Conectar letras rotas con DILATE
                    kernel_clean = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
                    # Eliminar ruido
                    text_mask_roi = cv2.morphologyEx(text_mask_roi, cv2.MORPH_OPEN, kernel_clean)
                    
                    # Asignar al mask global
                    mask[y1:y2, x1:x2] = text_mask_roi.astype(np.float32) / 255.0
                    
                    # IMPORTANTE: Si por alguna razon la mascara esta vacia (no detecto texto),
                    # hacemos fallback a borrar un rectangulo pequeño en el centro? 
                    # No, mejor no borrar nada que borrarlo todo.
                    if np.sum(text_mask_roi) < 10:
                            print(f"[INPAINT WARNING] No text detected in bubble {x1},{y1}. Skipping mask.")
                
        # Dilatar mascara
        # Para texto fino, dilatar menos. Para globo entero, dilatar un poco mas.
        if mask_mode == 'text' or True: # Force precision mode always as requested
             MASK_PADDING = 3 
             iter_dil = 2 # Un poco mas para asegurar que cubre bordes de compresion JPG
        else:
             MASK_PADDING = 5
             iter_dil = 1
             
        kernel = np.ones((MASK_PADDING, MASK_PADDING), np.uint8) 
        mask = cv2.dilate(mask, kernel, iterations=iter_dil)
        
        # --- OPTIMIZATION 3: FAST MODE (OpenCV Telea) ---
        if fast_mode:
            print("[INPAINTING] Fast Mode enabled (OpenCV Telea)")
            try:
                # cv2.inpaint requires uint8 mask
                mask_8u = (mask * 255).astype(np.uint8)
                # Radius 3 is a good balance
                inpainted = cv2.inpaint(img, mask_8u, 3, cv2.INPAINT_TELEA)
                
                result_bgr = cv2.cvtColor(inpainted, cv2.COLOR_RGB2BGR)
                cv2.imwrite(output_path, result_bgr)
                return output_path
            except Exception as e:
                print(f"[INPAINTING] Fast mode failed: {e}. Falling back to LaMa.")
        # ------------------------------------------------
        
        # 2. SMART TILING INFERENCE (Optimization)
        # Instead of processing the full high-res page, we iterate over bubbles,
        # crop them with context, and run LaMa on the small patches.
        
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
