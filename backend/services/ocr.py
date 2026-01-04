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

    def detect_text(self, image_content):
        """
        Detects text in an image using Google Cloud Vision.
        Returns a dict with 'text' and 'blocks' (coordinates).
        """
        image = vision.Image(content=image_content)

        # Usar document_text_detection para mejor precision en bloques
        response = self.client.document_text_detection(image=image)
        
        if response.error.message:
            raise Exception(f'{response.error.message}')

        # El primer elemento de text_annotations es todo el texto
        full_text = response.full_text_annotation.text if response.full_text_annotation else ""
        
        # Extraer bloques de palabras para la mascara fina (Method B)
        blocks = []
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        # Obtener vertices de la palabra
                        verts = [(v.x, v.y) for v in word.bounding_box.vertices]
                        blocks.append(verts)

        return {
            "text": full_text,
            "word_boxes": blocks # Lista de listas de tuplas [(x,y),...]
        }

    def detect_text_from_path(self, image_path: str) -> str:
        """
        Helper para leer desde archivo.
        """
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        return self.detect_text(content)
