import shutil
import uuid
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AI Comic Translator API", version="0.1.0")

# Configuración de Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Configuración de CORS
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar carpeta estática para servir las imágenes
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/")
async def root():
    return {"message": "Backend Online", "service": "AI Comic Translator"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Validar extensión (opcional pero recomendado)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image")
    
    # Generar nombre único
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Guardar en disco
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {
        "filename": unique_filename,
        "url": f"/uploads/{unique_filename}",
        "original_name": file.filename
    }

@app.post("/process")
async def process_comic(file: UploadFile = File(...)):
    # 1. Validar y Guardar imagen (reutilizamos logica basica)
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image")
    
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 2. Procesamiento AI
    try:
        # Lazy imports para evitar errores si las dependencias aun se instalan
        from services.detector import BubbleDetector
        from services.inpainting import TextRemover
        from services.ocr import OCRService
        from services.inpainting import TextRemover
        from services.translator import TranslatorService
        from services.renderer import TextRenderer
        import cv2
        import numpy as np
        
        # Detector
        detector = BubbleDetector()
        bubbles = detector.detect(file_path)
        
        # OCR Service
        ocr_service = OCRService()
        
        # Translator Service (Day 10)
        translator = TranslatorService(target_lang='es')
        
        # Leer imagen para recortes
        img_cv = cv2.imread(file_path)
        
        # Procesar cada burbuja para extraer texto y traducir
        print("Extracting and translating text...")
        for i, bubble in enumerate(bubbles):
            x1, y1, x2, y2 = map(int, bubble['bbox'])
            
            # Validar coordenadas
            h, w = img_cv.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            # Solo si el recorte es valido
            if x2 > x1 and y2 > y1:
                crop = img_cv[y1:y2, x1:x2]
                
                # Convertir a bytes jpg
                success, encoded_image = cv2.imencode('.jpg', crop)
                
                # --- COLOR DETECTION Start (Contrast Mode v2 - Center Sample) ---
                try:
                    if crop.size > 0:
                        # Para evitar coger el borde del globo (rojo/negro) o el fondo de la viñeta (azul),
                        # nos quedamos solo con la parte CENTRAL del crop (el "corazón" del globo).
                        h_crop, w_crop = crop.shape[:2]
                        # Definimos un margen de seguridad del 25% por cada lado 
                        # (nos quedamos con el 50% central)
                        y1_c = int(h_crop * 0.25)
                        y2_c = int(h_crop * 0.75)
                        x1_c = int(w_crop * 0.25)
                        x2_c = int(w_crop * 0.75)
                        
                        # Si el crop es muy pequeñito, usamos todo
                        if y2_c > y1_c and x2_c > x1_c:
                            center_sample = crop[y1_c:y2_c, x1_c:x2_c]
                        else:
                            center_sample = crop

                        # 1. Detectar color de fondo (Background) - Mediana del CENTRO
                        bg_color_bgr = np.median(center_sample, axis=(0, 1)).astype(int)
                        
                        # 2. Calcular distancias (Usamos el crop entero para buscar tinta, 
                        # pero comparando contra el bg del centro)
                        diff = crop.astype(int) - bg_color_bgr
                        dist = np.linalg.norm(diff, axis=2)
                        
                        # 3. Filtrar pixeles que son "Tinta"
                        threshold = np.percentile(dist, 90)
                        
                        if threshold < 20: 
                            text_color_bgr = np.array([0, 0, 0]) 
                            if np.mean(bg_color_bgr) < 50:
                                text_color_bgr = np.array([255, 255, 255])
                        else:
                            mask = dist >= threshold
                            if np.any(mask):
                                text_color_bgr = np.median(crop[mask], axis=0).astype(int)
                            else:
                                text_color_bgr = np.array([0, 0, 0])

                        # Output RGB
                        bg_color_rgb = (int(bg_color_bgr[2]), int(bg_color_bgr[1]), int(bg_color_bgr[0]))
                        text_color_rgb = (int(text_color_bgr[2]), int(text_color_bgr[1]), int(text_color_bgr[0]))
                        
                    else:
                        bg_color_rgb = (255, 255, 255)
                        text_color_rgb = (0, 0, 0)
                except Exception as e:
                    print(f"Error detecting color: {e}")
                    bg_color_rgb = (255, 255, 255)
                    text_color_rgb = (0, 0, 0)
                    
                bubble['bg_color'] = bg_color_rgb
                bubble['text_color'] = text_color_rgb
                # --- COLOR DETECTION End ---
                
                if success:
                    content = encoded_image.tobytes()
                    ocr_result = ocr_service.detect_text(content) # Ahora devuelve dict
                    
                    text = ocr_result.get("text", "")
                    word_boxes = ocr_result.get("word_boxes", [])
                    
                    bubble['text'] = text
                    
                    # Ajustar coordenadas de 'word_boxes' (vienen del crop, pasar a imagen global)
                    # word_boxes es una lista de listas de tuplas: [[(x,y), (x,y)...], ...]
                    abs_word_boxes = []
                    for wb in word_boxes:
                        abs_wb = []
                        for point in wb:
                            px, py = point
                            # Sumar offset del crop (x1, y1)
                            abs_wb.append((px + x1, py + y1))
                        abs_word_boxes.append(abs_wb)
                    bubble['word_boxes'] = abs_word_boxes
                    
                    # Traducir (Si hay texto)
                    if text and len(text.strip()) > 0:
                        # Limpieza para traducción (Flattening):
                        # Convertimos "HELLO\nWORLD" en "HELLO WORLD" para que el traductor entienda el contexto.
                        text_to_translate = text.replace('\n', ' ').replace('\r', ' ')
                        # Corregir separación de palabras por guiones (e.g. "Amaz-\ning" -> "Amazing")
                        text_to_translate = text_to_translate.replace('- ', '') 
                        
                        # Doble espacios a uno
                        import re
                        text_to_translate = re.sub(' +', ' ', text_to_translate).strip()
                        
                        trans_text, trans_provider = translator.translate(text_to_translate)
                        bubble['translation'] = trans_text
                        bubble['translation_provider'] = trans_provider
                    else:
                        bubble['translation'] = ""
                        bubble['translation_provider'] = "None"
            else:
                bubble['text'] = ""
                bubble['translation'] = ""
                bubble['translation_provider'] = "None"
                bubble['word_boxes'] = []

        # Debug: Dibujar cajas
        debug_filename = f"debug_{unique_filename}"
        debug_path = os.path.join(UPLOAD_DIR, debug_filename)
        detector.draw_boxes(file_path, bubbles, debug_path)
        
        # Inpainting (Remover texto)
        remover = TextRemover()
        
        # Opcion A: Borrar Globo Entero (Backup - DESACTIVADO POR RENDIMIENTO)
        # clean_bubble_filename = f"clean_bubble_{unique_filename}"
        # clean_bubble_path = os.path.join(UPLOAD_DIR, clean_bubble_filename)
        # remover.remove_text(file_path, bboxes=bubbles, output_path=clean_bubble_path, mask_mode='bubble')
        clean_bubble_filename = None
        
        # Opcion B: Borrar Solo Texto (Primary Strategy)
        clean_text_filename = f"clean_text_{unique_filename}"
        clean_text_path = os.path.join(UPLOAD_DIR, clean_text_filename)
        remover.remove_text(file_path, bboxes=bubbles, output_path=clean_text_path, mask_mode='text')
        
        # 3. Text Rendering (El Gran Final)
        renderer = TextRenderer()
        final_filename = f"final_{unique_filename}"
        final_path = os.path.join(UPLOAD_DIR, final_filename)
        
        # Usamos la imagen limpia (clean_text_path) y le pintamos encima
        success = renderer.render_text(clean_text_path, bubbles, final_path)
        
        final_url_val = f"/uploads/{final_filename}" if success else None

        return {
            "status": "success",
            "original_url": f"/uploads/{unique_filename}",
            "debug_url": f"/uploads/{debug_filename}",
            # "clean_url" apunta ahora a la Opcion B (Texto) por defecto
            "clean_url": f"/uploads/{clean_text_filename}",
            "clean_bubble_url": f"/uploads/{clean_bubble_filename}" if clean_bubble_filename else None,
            "final_url": final_url_val,
            "bubbles_count": len(bubbles),
            "bubbles_data": bubbles
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI Processing failed: {str(e)}")
