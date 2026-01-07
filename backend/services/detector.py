from ultralytics import YOLO
import cv2
import os
import numpy as np

class BubbleDetector:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BubbleDetector, cls).__new__(cls)
            cls._instance.load_model()
        return cls._instance

    def load_model(self):
        # Volvemos al modelo de Deteccion (mas robusto)
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "comic_yolov8m.pt")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Run download_model.py first.")
        
        print(f"Loading YOLO model from {model_path}...")
        self._model = YOLO(model_path)
    
    def detect(self, image_path: str):
        """
        Detecta bocadillos en una imagen.
        Retorna la imagen procesada con cajas y la lista de cajas.
        """
        if self._model is None:
            self.load_model()
        
        # Leemos la imagen original para procesarla despues (OpenCV Segmentation)
        original_img = cv2.imread(image_path)
        
        print(f"Running inference on {image_path}...")
        # Usar modelo de deteccion, umbral normal
        results = self._model(image_path, conf=0.20)
        
        # Procesar resultados
        boxes_data = []
        result = results[0] 
        
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = box.conf[0].item()
            cls = box.cls[0].item()
            
            # Generar Mascara Algoritmica (Hybrid Approach)
            polygon = self._get_bubble_contour(original_img, [x1, y1, x2, y2])

            boxes_data.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": conf,
                "class": cls,
                "polygon": polygon
            })

        print(f"Detected {len(boxes_data)} bubbles.")
        return boxes_data

    def _get_bubble_contour(self, img, bbox):
        """
        Genera un poligono ajustado usando OpenCV.
        Intenta detectar tanto burbujas claras (fondo oscuro) como oscuras (fondo claro).
        """
        x1, y1, x2, y2 = map(int, bbox)
        h, w = img.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            return []
            
        crop = img[y1:y2, x1:x2]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Helper para extraer el mejor contorno de una mascara binaria
        def get_best_contour(binary_mask):
            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return None, 0
            # Criterio: El contorno mas grande que este "centrado" es el mejor candidato
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            return largest, area

        # Intento 1: Burbujas Claras (Texto negro sobre blanco, o blanco sobre fondo pagina oscuro)
        # THRESH_BINARY + OTSU: Pixeles claros -> 255 (Foreground)
        _, mask_light = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cnt_light, area_light = get_best_contour(mask_light)
        
        # Intento 2: Burbujas Oscuras (Negras/Grises sobre fondo blanco)
        # THRESH_BINARY_INV + OTSU: Pixeles oscuros -> 255 (Foreground)
        _, mask_dark = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        cnt_dark, area_dark = get_best_contour(mask_dark)
        
        # Decision: ¿Cual tiene mas sentido?
        # Generalmente el globo ocupa una gran parte del bounding box.
        # Si la deteccion inversa da un area mucho mayor, podria ser una burbuja oscura
        # Ojo: Si el fondo es blanco, invertirlo hace que TODO el fondo sea "burbuja".
        # Necesitamos verificar que el contorno no toque todos los bordes (o sea el recuadro entero)
        
        crop_area = (x2-x1) * (y2-y1)
        
        # Preferimos el contorno que ocupe una porcion significativa (ej. > 20%) 
        # pero no TOTAL (ej. < 95% si es el recuadro entero)
        
        candidate = None
        
        # Logica simple: El que tenga mayor area valida
        def is_valid(area, crop_a):
            if crop_a == 0: # Avoid division by zero if crop is 0-sized
                return False
            ratio = area / crop_a
            return 0.15 < ratio < 0.98

        valid_light = is_valid(area_light, crop_area)
        valid_dark = is_valid(area_dark, crop_area)
        
        if valid_light and not valid_dark:
            candidate = cnt_light
        elif valid_dark and not valid_light:
            candidate = cnt_dark
        elif valid_light and valid_dark:
            # Ambos validos? Probablemente uno es el globo y otro es el "no globo"
            # En comics, los globos suelen ser convexos y centrados.
            # Nos quedamos con el que tenga mayor area (heuristicamente funciona mejor para blobs)
            if area_light > area_dark:
                candidate = cnt_light
            else:
                candidate = cnt_dark
        else:
            # Ninguno valido (muy pequeños o recuadro entero)
            # Fallback: Usar el light si existe (comportamiento default)
            candidate = cnt_light if cnt_light is not None else cnt_dark

        if candidate is None:
            return []

        # Simplificar
        # Ajuste de sensibilidad (Day 13): 
        # Bajamos epsilon de 0.01 a 0.002 para que NO recorte las esquinas de los cuadrados.
        epsilon = 0.002 * cv2.arcLength(candidate, True)
        approx = cv2.approxPolyDP(candidate, epsilon, True)
        
        # Coordenadas Globales
        global_contour = []
        for point in approx:
            px, py = point[0]
            # Convertir a int nativo
            global_contour.append([int(px + x1), int(py + y1)])
            
        return global_contour

    def draw_boxes(self, image_path: str, boxes_data: list, output_path: str):
        """
        Dibuja poligonos y cajas.
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image {image_path}")
            
        overlay = img.copy()

        for item in boxes_data:
            x1, y1, x2, y2 = map(int, item['bbox'])
            
            # Dibujar Poligono
            if item.get('polygon') and len(item['polygon']) > 0:
                pts = np.array(item['polygon'], np.int32)
                pts = pts.reshape((-1, 1, 2))
                color = (255, 100, 0) # Azul
                cv2.fillPoly(overlay, [pts], color)
                
            # Caja
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Etiqueta
            label = f"{item['confidence']:.2f}"
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        # Transparencia
        alpha = 0.4
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
            
        cv2.imwrite(output_path, img)
        return output_path
