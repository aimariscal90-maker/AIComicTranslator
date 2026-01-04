from google.cloud import vision
import os
import io

class OCRService:
    def __init__(self):
        # Asegurarse de que la variable de entorno apunte al JSON
        # (Idealmente, esto ya deberia estar en .env o setado, pero lo forzamos por si acaso)
        cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "google_credentials.json")
        if os.path.exists(cred_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
        
        self.client = vision.ImageAnnotatorClient()

    def detect_text(self, image_bytes: bytes) -> str:
        """
        Detecta texto en una imagen (formato bytes).
        Retorna el string completo detectado.
        """
        try:
            image = vision.Image(content=image_bytes)
            # DOCUMENT_TEXT_DETECTION optimizado para bloques de texto denso
            response = self.client.document_text_detection(image=image)
            
            if response.error.message:
                raise Exception(f"Google Vision API Error: {response.error.message}")

            return response.full_text_annotation.text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

    def detect_text_from_path(self, image_path: str) -> str:
        """
        Helper para leer desde archivo.
        """
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        return self.detect_text(content)
