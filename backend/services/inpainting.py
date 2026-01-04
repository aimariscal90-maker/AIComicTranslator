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

    def remove_text(self, image_path, bboxes, output_path, mask_mode='bubble'):
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
                # Modo Bruto (Fallback o Default): Usar poligono del globo
                if bubble.get('polygon') and len(bubble['polygon']) > 0:
                    pts = np.array(bubble['polygon'], np.int32)
                    cv2.fillPoly(mask, [pts], 1.0)
                else:
                    x1, y1, x2, y2 = map(int, bubble['bbox'])
                    cv2.rectangle(mask, (x1, y1), (x2, y2), 1.0, -1)
                
        # Dilatar mascara
        # Para texto fino, dilatar menos. Para globo entero, dilatar un poco mas.
        if mask_mode == 'text':
             MASK_PADDING = 3 # Mas fino para letras
             iter_dil = 1
        else:
             MASK_PADDING = 5
             iter_dil = 1
             
        kernel = np.ones((MASK_PADDING, MASK_PADDING), np.uint8) 
        mask = cv2.dilate(mask, kernel, iterations=iter_dil)
        
        # 2. Preprocesar para LaMa
        # Resize a multiplo de 8 
        # (LaMa lo necesita para bajar/subir de resolucion en la red)
        def pad_to_divisible(arr, divisor=8):
            h, w = arr.shape[:2]
            h_pad = (divisor - h % divisor) % divisor
            w_pad = (divisor - w % divisor) % divisor
            return np.pad(arr, ((0, h_pad), (0, w_pad), (0, 0)), mode='reflect') if arr.ndim == 3 else np.pad(arr, ((0, h_pad), (0, w_pad)), mode='reflect')

        img_padded = pad_to_divisible(img)
        mask_padded = pad_to_divisible(mask, 8)
        
        # Normalize 0-1 and Tensor conversion
        img_tensor = torch.from_numpy(img_padded).permute(2, 0, 1).float().div(255.0).to(self.device)
        mask_tensor = torch.from_numpy(mask_padded).unsqueeze(0).float().to(self.device)
        
        # Agregar batch dimension
        img_tensor = img_tensor.unsqueeze(0)
        mask_tensor = mask_tensor.unsqueeze(0)
        
        # 3. Inferencia
        with torch.no_grad():
            # La entrada de big-lama.pt suele ser (image, mask) o solo image concatenada
            # Dependiendo de como se exporto. 
            # El modelo estandar de LaMa espera img y mask por separado o concatenados.
            # Probemos la firma comun: model(img, mask)
            try:
                # Inpaint
                inpainted = self.model(img_tensor, mask_tensor)
                
                # A veces devuelve una lista o tupla
                if isinstance(inpainted, (list, tuple)):
                    inpainted = inpainted[0]
                    
            except Exception as e:
                print(f"Inference error: {e}")
                return

        # 4. Postprocesar
        result_tensor = inpainted[0].permute(1, 2, 0).cpu().numpy()
        result_tensor = np.clip(result_tensor * 255, 0, 255).astype(np.uint8)
        
        # Crop back to original size
        result_img = result_tensor[:h, :w]
        
        # Guardar
        result_bgr = cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, result_bgr)
        return output_path
