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
            
        print(f"Running inference on {image_path}...")
        # Usar un umbral de confianza más bajo para asegurar detección
        results = self._model(image_path, conf=0.20)
        
        # Procesar resultados
        boxes_data = []
        result = results[0] # Primera imagen
        
        for box in result.boxes:
            # Coordenadas y confianza
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = box.conf[0].item()
            cls = box.cls[0].item()
            
            boxes_data.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": conf,
                "class": cls
            })

        print(f"Detected {len(boxes_data)} bubbles.")
        return boxes_data

    def draw_boxes(self, image_path: str, boxes_data: list, output_path: str):
        """
        Dibuja las cajas sobre la imagen original.
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image {image_path}")

        for item in boxes_data:
            x1, y1, x2, y2 = map(int, item['bbox'])
            # Dibujar rectangulo verde
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # Etiqueta
            label = f"Bubble: {item['confidence']:.2f}"
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
        cv2.imwrite(output_path, img)
        return output_path
