import shutil
import uuid
import os
import zipfile
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from models import Project, Page, Bubble
from services.queue_manager import JobManager

app = FastAPI(title="AI Comic Translator API", version="0.1.0")
job_manager = JobManager()

# Configuración de Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Configuración de CORS
origins = [
    "http://localhost:3000",
    os.getenv("ALLOWED_ORIGINS"), # Production Vercel URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler para asegurar CORS en TODOS los errores
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "true",
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": "There was an error parsing the body", "errors": str(exc)},
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "true",
        }
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

# --- BATCH PROCESSING (DAY 27) ---
# --- BATCH PROCESSING (DAY 27 & 30 OPTIMIZATIONS) ---
# Dynamic Worker Tuning: Use available cores but leave one for system/API
import os
try:
    cpu_cores = os.cpu_count() or 1
    # En Railway free tier a veces reporta muchos cores virtuales pero poco power.
    # Limitamos a un rango sensato (1-4).
    MAX_PARALLEL_WORKERS = max(1, min(4, cpu_cores - 1))
except:
    MAX_PARALLEL_WORKERS = 1

print(f"[PERFORMANCE] Configured MAX_PARALLEL_WORKERS = {MAX_PARALLEL_WORKERS}")

def log_to_file(msg):
    try:
        with open("backend_debug.log", "a", encoding="utf-8") as f:
            import datetime
            ts = datetime.datetime.now().isoformat()
            f.write(f"[{ts}] {msg}\n")
    except:
        pass

def process_batch_task(project_id: str, batch_id: str, tasks: list):
    """
    Procesa múltiples páginas en paralelo usando ThreadPoolExecutor.
    """
    try:
        msg = f"[BATCH {batch_id}] INIT: Starting process_batch_task with {len(tasks)} tasks"
        print(msg)
        log_to_file(msg)
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        from threading import Lock
        
        # Verify database connection
        try:
            db = SessionLocal()
            log_to_file(f"[BATCH {batch_id}] DB Session created")
        except Exception as e:
            log_to_file(f"[BATCH FATAL] DB Connect failed: {e}")
            raise

        total = len(tasks)
        completed_lock = Lock()
        completed_count = 0
        
        log_to_file(f"[BATCH {batch_id}] Starting parallel processing: {total} pages with {MAX_PARALLEL_WORKERS} workers")
        
        def process_single_task(task_data):
            """Wrapper para procesar una tarea individual"""
            nonlocal completed_count
            i = task_data['index']
            task = task_data['task']
            
            try:
                log_to_file(f"[BATCH {batch_id}] 🚀 Starting page {i+1}/{total}: {task['filename']}")
                
                # Procesar esta página
                process_comic_task(
                    job_id=task['job_id'],
                    file_path=task['file_path'],
                    unique_filename=task['filename'],
                    project_id=project_id,
                    page_number=task.get('page_number', i + 1)
                )
                
                with completed_lock:
                    completed_count += 1
                    log_to_file(f"[BATCH {batch_id}] ✅ Page {i+1}/{total} completed")
                
                return {'success': True, 'index': i}
                
            except Exception as e:
                err_msg = f"[BATCH ERROR] ❌ Page {i+1} failed: {e}"
                print(err_msg)
                log_to_file(err_msg)
                import traceback
                traceback.print_exc()
                log_to_file(traceback.format_exc())
                return {'success': False, 'index': i, 'error': str(e)}
        
        # Preparar tareas con índices
        indexed_tasks = [{'index': i, 'task': task} for i, task in enumerate(tasks)]
        
        # Procesar en paralelo con ThreadPoolExecutor
        log_to_file(f"[BATCH {batch_id}] submitting tasks to executor...")
        with ThreadPoolExecutor(max_workers=MAX_PARALLEL_WORKERS) as executor:
            # Submit all tasks
            futures = {executor.submit(process_single_task, task_data): task_data for task_data in indexed_tasks}
            
            # Wait for completion
            for future in as_completed(futures):
                result = future.result()
        
        log_to_file(f"[BATCH {batch_id}] 🎉 Complete! Processed {total} pages")
        
        db.close()
        
    except Exception as e:
        err_msg = f"[BATCH FATAL ERROR] process_batch_task crashed: {e}"
        print(err_msg)
        log_to_file(err_msg)
        import traceback
        traceback.print_exc()
        log_to_file(traceback.format_exc())

# --- ASYNC TASK LOGIC ---
def process_comic_task(job_id: str, file_path: str, unique_filename: str, project_id: str = None, page_number: int = None):
    try:
        job_manager.update_job(job_id, status="processing", progress=10, step="Iniciando Modelos AI...")
        
        # Lazy imports para evitar errores si las dependencias aun se instalan
        from services.detector import BubbleDetector
        from services.inpainting import TextRemover
        from services.ocr import OCRService
        from services.translator import TranslatorService
        from services.renderer import TextRenderer
        import cv2
        import numpy as np

        # --- OPTIMIZATION 1: SMART DOWNSCALING (Day 30) ---
        # Si la imagen es gigante (>1920px), la reducimos para acelerar x3 la detección/inpainting
        # manteniendo calidad HD suficiente para cómic.
        img_temp = cv2.imread(file_path)
        if img_temp is not None:
            h, w = img_temp.shape[:2]
            max_dim = 1920
            if max(h, w) > max_dim:
                scale = max_dim / max(h, w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                
                print(f"[OPTIMIZATION] Resizing image from {w}x{h} to {new_w}x{new_h}")
                job_manager.update_job(job_id, progress=15, step=f"Optimizando Tamaño ({new_w}x{new_h})...")
                
                img_resized = cv2.resize(img_temp, (new_w, new_h), interpolation=cv2.INTER_AREA)
                cv2.imwrite(file_path, img_resized) # Sobreescribimos para que todo el pipeline use la versión optimizada
            else:
                print(f"[OPTIMIZATION] Image size {w}x{h} is OK.")
        # --------------------------------------------------

        # 1. Detección
        job_manager.update_job(job_id, progress=20, step="Detectando Bocadillos 🕵️")
        detector = BubbleDetector()
        bubbles = detector.detect(file_path)
        
        # 2. OCR
        job_manager.update_job(job_id, progress=40, step="Leyendo Texto (OCR) 📖")
        ocr_service = OCRService()
        
        # 3. Traducción (Day 24: Contextual Batch Translation)
        job_manager.update_job(job_id, progress=50, step="Traduciendo (Gemini con Contexto) 🤖")
        translator = TranslatorService(target_lang='es')
        
        # Leer imagen para recortes
        img_cv = cv2.imread(file_path)
        
        # Procesar cada burbuja para extraer texto y traducir
        print("Extracting text and detecting colors...")
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
                        h_crop, w_crop = crop.shape[:2]
                        y1_c = int(h_crop * 0.25)
                        y2_c = int(h_crop * 0.75)
                        x1_c = int(w_crop * 0.25)
                        x2_c = int(w_crop * 0.75)
                        
                        if y2_c > y1_c and x2_c > x1_c:
                            center_sample = crop[y1_c:y2_c, x1_c:x2_c]
                        else:
                            center_sample = crop

                        bg_color_bgr = np.median(center_sample, axis=(0, 1)).astype(int)
                        diff = crop.astype(int) - bg_color_bgr
                        dist = np.linalg.norm(diff, axis=2)
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
                    ocr_result = ocr_service.detect_text(content)
                    
                    text = ocr_result.get("text", "")
                    word_boxes = ocr_result.get("word_boxes", [])
                    bubble['text'] = text
                    
                    abs_word_boxes = []
                    for wb in word_boxes:
                        abs_wb = []
                        for point in wb:
                            px, py = point
                            abs_wb.append((px + x1, py + y1))
                        abs_word_boxes.append(abs_wb)
                    bubble['word_boxes'] = abs_word_boxes
                    
                    if text and len(text.strip()) > 0:
                        text_to_translate = text.replace('\n', ' ').replace('\r', ' ')
                        text_to_translate = text_to_translate.replace('- ', '') 
                        import re
                        text_to_translate = re.sub(' +', ' ', text_to_translate).strip()
                        bubble['clean_text'] = text_to_translate  # Store for batch translation
                    else:
                        bubble['clean_text'] = ""
            else:
                bubble['text'] = ""
                bubble['translation'] = ""
                bubble['translation_provider'] = "None"
                bubble['word_boxes'] = []

        # DAY 25: Bubble Classification
        # Clasificar tipos ANTES de traducir
        bubbles_with_text = [(i, b) for i, b in enumerate(bubbles) if b.get('clean_text', '').strip()]
        
        if bubbles_with_text:
            texts_for_classification = [b['clean_text'] for _, b in bubbles_with_text]
            
            try:
                print(f"[DAY 25] Classifying {len(texts_for_classification)} bubbles...")
                print(f"[DAY 25 DEBUG] Texts to classify: {texts_for_classification[:5]}...")  # Primeros 5
                bubble_types = translator.classify_bubbles_batch(texts_for_classification)
                
                # Asignar tipos
                for idx, (i, bubble) in enumerate(bubbles_with_text):
                    if idx < len(bubble_types):
                        bubbles[i]['bubble_type'] = bubble_types[idx]
                    else:
                        bubbles[i]['bubble_type'] = "speech"
                        
                print(f"[DAY 25] Classification complete. Types: {set(bubble_types)}")

                
            except Exception as e:
                print(f"[ERROR] Bubble classification failed: {e}")
                # Fallback: todos speech
                for i, _ in bubbles_with_text:
                    bubbles[i]['bubble_type'] = "speech"
        
        # DAY 24: Batch Contextual Translation
        # Recopilar textos para traducción contextual
        bubbles_with_text = [(i, b) for i, b in enumerate(bubbles) if b.get('clean_text', '').strip()]
        
        if bubbles_with_text:
            texts_to_translate = [b['clean_text'] for _, b in bubbles_with_text]
            
            try:
                print(f"[DAY 24] Translating {len(texts_to_translate)} texts with context...")
                translations, provider = translator.translate_batch_with_context(texts_to_translate)
                
                # Asignar traducciones
                for idx, (i, bubble) in enumerate(bubbles_with_text):
                    if idx < len(translations):
                        bubbles[i]['translation'] = translations[idx]
                        bubbles[i]['translation_provider'] = provider
                    else:
                        bubbles[i]['translation'] = bubble['clean_text']
                        bubbles[i]['translation_provider'] = "Error: Missing translation"
                        
                print(f"[DAY 24] Batch translation successful with {provider}")
                
            except Exception as e:
                print(f"[ERROR] Batch translation failed: {e}")
                # Fallback: traducir individualmente
                for i, b in bubbles_with_text:
                    try:
                        trans, prov = translator.translate(b['clean_text'])
                        bubbles[i]['translation'] = trans
                        bubbles[i]['translation_provider'] = prov
                    except:
                        bubbles[i]['translation'] = b['clean_text']
                        bubbles[i]['translation_provider'] = "Error"
        
        # Asegurar que todos los bubbles tienen translation
        for bubble in bubbles:
            if 'translation' not in bubble:
                bubble['translation'] = ""
                bubble['translation_provider'] = "None"
        
        # 4. Inpainting
        job_manager.update_job(job_id, progress=70, step="Borrando Texto (Fast Mode) 🎨")
        
        debug_filename = f"debug_{unique_filename}"
        debug_path = os.path.join(UPLOAD_DIR, debug_filename)
        detector.draw_boxes(file_path, bubbles, debug_path)
        
        remover = TextRemover()
        clean_text_filename = f"clean_text_{unique_filename}"
        clean_text_path = os.path.join(UPLOAD_DIR, clean_text_filename)
        clean_bubble_filename = None
        
        # FORCE FAST MODE for performance (CPU friendly)
        remover.remove_text(file_path, bboxes=bubbles, output_path=clean_text_path, mask_mode='text', fast_mode=True)
        
        # 5. Text Rendering (El Gran Final)
        job_manager.update_job(job_id, progress=90, step="Renderizando Español ✍️")
        renderer = TextRenderer()
        final_filename = f"final_{unique_filename}"
        final_path = os.path.join(UPLOAD_DIR, final_filename)
        
        success = renderer.render_text(clean_text_path, bubbles, final_path)
        final_url_val = f"/uploads/{final_filename}" if success else None
        
        # Guardar metadatos en JSON para futura edición (Day 15)
        import json
        json_filename = f"metadata_{unique_filename}.json"
        json_path = os.path.join(UPLOAD_DIR, json_filename)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(bubbles, f, default=str, ensure_ascii=False)

        
        # 6. Guardar en Base de Datos (Day 23)
        if project_id:
            try:
                from database import SessionLocal
                db = SessionLocal()
                
                # Crear registro Page
                page = Page(
                    project_id=project_id,
                    filename=unique_filename,
                    original_url=f"/uploads/{unique_filename}",
                    final_url=final_url_val,
                    debug_url=f"/uploads/{debug_filename}",
                    clean_url=f"/uploads/{clean_text_filename}",
                    page_number=page_number,  # Day 27: Batch upload
                    status="completed"
                )
                db.add(page)
                db.commit()
                db.refresh(page)
                
                # Save ID before closing session
                page_id = page.id
                
                # Crear registros Bubble
                for bubble_data in bubbles:
                    bubble = Bubble(
                        page_id=page_id,
                        bbox=bubble_data['bbox'],
                        original_text=bubble_data.get('text', ''),
                        translated_text=bubble_data.get('translation', ''),
                        font=bubble_data.get('font', 'ComicNeue'),
                        confidence=int(bubble_data.get('confidence', 0)),
                        bubble_type='speech',  # Por ahora todos speech
                        translation_provider=bubble_data.get('translation_provider', 'Unknown')
                    )
                    db.add(bubble)
                db.commit()
                db.close()
                
                print(f"[DB] Page saved: {page_id} with {len(bubbles)} bubbles")
            except Exception as db_error:
                print(f"[DB ERROR] Failed to save to database: {db_error}")
                import traceback
                traceback.print_exc()
        
        # 7. Update Job Complete
        result_data = {
            "id": unique_filename,
            "filename": unique_filename,
            "original_url": f"/uploads/{unique_filename}",
            "final_url": final_url_val,
            "debug_url": f"/uploads/{debug_filename}",
            "clean_url": f"/uploads/{clean_text_filename}",
            "clean_bubble_url": f"/uploads/{clean_bubble_filename}" if clean_bubble_filename else None,
            "bubbles_count": len(bubbles),
            "bubbles_data": bubbles
        }
        
        job_manager.update_job(job_id, status="completed", progress=100, step="¡Completado!", result=result_data)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        job_manager.update_job(job_id, status="failed", error=str(e), step="Error Interno")

class ProcessRequest(BaseModel):
    project_id: Optional[str] = None

@app.post("/process")
async def process_comic(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    project_id: Optional[str] = Form(None)
):
    # 1. Validar y Guardar imagen
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image")
    
    # Debug log
    print(f"[DEBUG] Received project_id: {project_id}")
    
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 2. Crear Job y Encolar
    job_id = job_manager.create_job()
    background_tasks.add_task(process_comic_task, job_id, file_path, unique_filename, project_id)
    
    return {"job_id": job_id, "status": "queued"}

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# --- EDITING ENDPOINTS ---
class UpdateBubbleRequest(BaseModel):
    bubble_index: int
    new_text: str
    font: str = "ComicNeue"

@app.patch("/process/{filename}/update-bubble")
async def update_bubble(filename: str, request: UpdateBubbleRequest):
    """
    Actualiza el texto/fuente de un bocadillo específico y regenera la imagen.
    """
    try:
        import json
        import cv2
        import numpy as np
        from PIL import Image
        from services.renderer import TextRenderer

        # 1. Cargar metadatos
        json_path = os.path.join(UPLOAD_DIR, f"metadata_{filename}.json")
        if not os.path.exists(json_path):
            raise HTTPException(status_code=404, detail="Metadata not found")
        
        with open(json_path, "r", encoding="utf-8") as f:
            bubbles = json.load(f)

        if request.bubble_index < 0 or request.bubble_index >= len(bubbles):
            raise HTTPException(status_code=400, detail="Invalid bubble index")

        # 2. Actualizar datos
        bubbles[request.bubble_index]['translation'] = request.new_text
        bubbles[request.bubble_index]['font'] = request.font # Guardamos la fuente
        
        # Guardar cambios
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(bubbles, f, default=str, ensure_ascii=False)

        # 3. Regenerar Imagen (Text Rendering)
        clean_text_filename = f"clean_text_{filename}"
        clean_text_path = os.path.join(UPLOAD_DIR, clean_text_filename)
        
        if not os.path.exists(clean_text_path):
             # Intentar fallback
             clean_text_path = os.path.join(UPLOAD_DIR, f"clean_text_{filename}.jpg")
             if not os.path.exists(clean_text_path):
                 raise HTTPException(status_code=404, detail="Clean image source not found")

        # Cargar imagen limpia (Clean Image)
        clean_img_cv = cv2.imread(clean_text_path)
        if clean_img_cv is None:
             raise HTTPException(status_code=500, detail="Failed to load clean image")

        clean_img_pil = Image.fromarray(cv2.cvtColor(clean_img_cv, cv2.COLOR_BGR2RGB))

        # Renderizar
        renderer = TextRenderer()
        final_filename = f"final_{filename}.jpg"
        final_path = os.path.join(UPLOAD_DIR, final_filename)
        
        
        renderer.render_text(clean_img_pil, bubbles, final_path)
        
        # 4. Actualizar en Base de Datos (Day 23)
        try:
            from database import SessionLocal
            db = SessionLocal()
            
            # Buscar página por filename
            page = db.query(Page).filter(Page.filename == filename).first()
            
            if page and page.bubbles:
                # Buscar bubble por índice (asumiendo mismo orden que en JSON)
                if request.bubble_index < len(page.bubbles):
                    bubble_db = page.bubbles[request.bubble_index]
                    bubble_db.translated_text = request.new_text
                    bubble_db.font = request.font
                    db.commit()
                    print(f"[DB] Bubble {bubble_db.id} updated in database")
            
            db.close()
        except Exception as db_error:
            print(f"[DB WARNING] Failed to update bubble in database: {db_error}")
            # No lanzamos error, la edición en JSON ya está hecha
        
        return {
            "status": "updated",
            "final_url": f"/uploads/{final_filename}",
            "bubbles_data": bubbles
        }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

class UpdateAllFontsRequest(BaseModel):
    font: str

@app.patch("/process/{filename}/update-all-fonts")
async def update_all_fonts(filename: str, request: UpdateAllFontsRequest):
    """
    Actualiza la fuente de TODOS los bocadillos y regenera la imagen.
    """
    try:
        import json
        import cv2
        import numpy as np
        from PIL import Image
        from services.renderer import TextRenderer

        # 1. Cargar metadatos
        json_path = os.path.join(UPLOAD_DIR, f"metadata_{filename}.json")
        if not os.path.exists(json_path):
            raise HTTPException(status_code=404, detail="Metadata not found")
        
        with open(json_path, "r", encoding="utf-8") as f:
            bubbles = json.load(f)

        # 2. Actualizar datos (Bulk Update)
        for bubble in bubbles:
            bubble['font'] = request.font
        
        # Guardar cambios
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(bubbles, f, default=str, ensure_ascii=False)

        # 3. Regenerar Imagen (Text Rendering)
        clean_text_filename = f"clean_text_{filename}"
        clean_text_path = os.path.join(UPLOAD_DIR, clean_text_filename)
        
        if not os.path.exists(clean_text_path):
             clean_text_path = os.path.join(UPLOAD_DIR, f"clean_text_{filename}.jpg")
             if not os.path.exists(clean_text_path):
                 raise HTTPException(status_code=404, detail="Clean image source not found")

        # Renderizar
        renderer = TextRenderer()
        final_filename = f"final_{filename}.jpg"
        final_path = os.path.join(UPLOAD_DIR, final_filename)
        
        renderer.render_text(clean_text_path, bubbles, final_path)
        
        return {
            "status": "updated_all",
            "final_url": f"/uploads/{final_filename}",
            "bubbles_data": bubbles
        }
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Bulk Update failed: {str(e)}")

# --- EXPORT ENDPOINTS ---
@app.get("/process/{filename}/download-zip")
async def download_project_zip(filename: str):
    """
    Empaqueta SOLAMENTE la imagen final traducida en un ZIP (Solicitud del Usuario).
    """
    try:
        # Definir archivos a incluir (Solo Final)
        files_to_zip = {
            "Traduccion_Final.jpg": f"final_{filename}.jpg"
        }
        
        # Nombre del ZIP de salida
        zip_filename = f"Comic_Translated_{filename}.zip"
        zip_path = os.path.join(UPLOAD_DIR, zip_filename)
        
        # Crear ZIP
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for zip_name, disk_name in files_to_zip.items():
                disk_path = os.path.join(UPLOAD_DIR, disk_name)
                if os.path.exists(disk_path):
                    zipf.write(disk_path, arcname=zip_name)
        
        return FileResponse(zip_path, media_type='application/zip', filename=zip_filename)

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# --- PROJECT MANAGEMENT ENDPOINTS (DAY 22) ---
class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None

@app.post("/projects")
def create_project(request: CreateProjectRequest, db: Session = Depends(get_db)):
    """
    Crear un nuevo proyecto (serie/capítulo de cómic).
    """
    project = Project(
        name=request.name,
        description=request.description
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@app.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    """
    Listar todos los proyectos ordenados por fecha de creación.
    """
    from sqlalchemy.orm import joinedload
    projects = db.query(Project).options(joinedload(Project.pages)).order_by(Project.created_at.desc()).all()
    return projects

@app.get("/projects/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db)):
    """
    Obtener detalles de un proyecto específico con sus páginas.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.get("/projects/{project_id}/pages")
def get_project_pages(project_id: str, db: Session = Depends(get_db)):
    """
    Obtener todas las páginas de un proyecto.
    """
    pages = db.query(Page).filter(Page.project_id == project_id).order_by(Page.page_number).all()
    return pages

@app.delete("/projects/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    """
    Eliminar un proyecto (cascade eliminará páginas y bocadillos).
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"status": "deleted", "project_id": project_id}

# --- DOWNLOAD ENDPOINTS ---
@app.get("/process/{filename}/download-final")
async def download_final_image(filename: str):
    """
    Descarga directa de la imagen final traducida (Forzando attachment).
    """
    try:
        final_filename = f"final_{filename}.jpg"
        file_path = os.path.join(UPLOAD_DIR, final_filename)
        
        if not os.path.exists(file_path):
             # Fallback check
             if os.path.exists(os.path.join(UPLOAD_DIR, f"final_{filename}")):
                 final_filename = f"final_{filename}"
                 file_path = os.path.join(UPLOAD_DIR, final_filename)
             else:
                 raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            file_path, 
            media_type='image/jpeg', 
            filename=f"Traduccion_{filename}.jpg",
            headers={"Content-Disposition": f"attachment; filename=Traduccion_{filename}.jpg"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

# --- PROJECT EXPORT (DAY 28 & 30) ---
@app.get("/projects/{project_id}/export")
async def export_project(project_id: str, format: str = "cbz", db: Session = Depends(get_db)):
    """
    Exporta todo el proyecto como un archivo CBZ, ZIP o PDF.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    pages = db.query(Page).filter(Page.project_id == project_id).order_by(Page.page_number).all()
    if not pages:
        raise HTTPException(status_code=400, detail="Project has no pages")

    try:
        # Preparar nombre y path temporal
        safe_name = "".join([c for c in project.name if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
        export_filename = f"{safe_name}.{format}"
        zip_path = os.path.join(UPLOAD_DIR, export_filename)

        # Recopilar archivos
        files_to_pack = []
        for i, page in enumerate(pages):
            # Preferir imagen final, luego clean, luego original
            source_url = page.final_url or page.clean_url or page.original_url
            if source_url:
                local_filename = source_url.split("/")[-1] # /uploads/filename.jpg -> filename.jpg
                local_path = os.path.join(UPLOAD_DIR, local_filename)
                
                if os.path.exists(local_path):
                    # Extensión original
                    ext = local_filename.split(".")[-1]
                    # Nombre secuencial: 001.jpg
                    archive_name = f"{i+1:03d}.{ext}"
                    files_to_pack.append((local_path, archive_name))
        
        if not files_to_pack:
             raise HTTPException(status_code=404, detail="No valid images found to export")

        # Crear archivo (CBZ/ZIP son lo mismo)
        if format in ['cbz', 'zip']:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for disk_path, arc_name in files_to_pack:
                    zipf.write(disk_path, arcname=arc_name)
            
            media_type = 'application/vnd.comicbook+zip' if format == 'cbz' else 'application/zip'
            
        elif format == 'pdf':
             # TODO: Implement PDF export using img2pdf if requested
             # Fallback to ZIP for now or implement if dependency exists
             pass

        return FileResponse(
            zip_path, 
            media_type=media_type, 
            filename=export_filename,
            headers={"Content-Disposition": f"attachment; filename={export_filename}"}
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# --- BATCH UPLOAD ENDPOINT (DAY 27) ---
    Descarga directa de la imagen final traducida (Forzando attachment).
    """
    try:
        final_filename = f"final_{filename}.jpg"
        file_path = os.path.join(UPLOAD_DIR, final_filename)
        
        if not os.path.exists(file_path):
             # Fallback check
             if os.path.exists(os.path.join(UPLOAD_DIR, f"final_{filename}")):
                 final_filename = f"final_{filename}"
                 file_path = os.path.join(UPLOAD_DIR, final_filename)
             else:
                 raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            file_path, 
            media_type='image/jpeg', 
            filename=f"Traduccion_{filename}.jpg",
            headers={"Content-Disposition": f"attachment; filename=Traduccion_{filename}.jpg"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

# --- BATCH UPLOAD ENDPOINT (DAY 27) ---
@app.post("/projects/{project_id}/upload-batch")
async def upload_batch(
    project_id: str,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(None),
    zip_file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """
    Day 27: Sube múltiples imágenes o un ZIP para procesamiento en batch.
    Acepta:
    - files: Lista de archivos de imagen
    - zip_file: Un archivo ZIP con imágenes
    """
    # Validar proyecto existe
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    batch_id = str(uuid.uuid4())
    tasks = []
    
    try:
        # Función helper para extraer imágenes de archivos
        def extract_images_from_archive(file_path: str, file_type: str) -> list:
            """Extrae imágenes de PDF, ZIP, CBZ, CBR"""
            extract_dir = os.path.join(UPLOAD_DIR, f"extract_{batch_id}")
            os.makedirs(extract_dir, exist_ok=True)
            image_files = []
            
            if file_type == 'pdf':
                # Extraer PDF a imágenes
                from pdf2image import convert_from_path
                print(f"[BATCH] Converting PDF to images...")
                try:
                    pages = convert_from_path(file_path, dpi=300)
                    for i, page in enumerate(pages):
                        img_path = os.path.join(extract_dir, f"page_{i+1:03d}.jpg")
                        page.save(img_path, 'JPEG')
                        image_files.append(img_path)
                except Exception as e:
                    print(f"[ERROR] PDF conversion failed: {e}")
                    print("NOTA: PDF requiere poppler. Instala con: choco install poppler (Windows) o brew install poppler (Mac)")
                    raise
            
            elif file_type in ['zip', 'cbz']:
                # Descomprimir ZIP/CBZ
                import zipfile
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Buscar imágenes
                for root, dirs, filenames in os.walk(extract_dir):
                    for filename in sorted(filenames):
                        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp')):
                            image_files.append(os.path.join(root, filename))
            
            elif file_type == 'cbr':
                # Descomprimir RAR/CBR
                import rarfile
                with rarfile.RarFile(file_path, 'r') as rar_ref:
                    rar_ref.extractall(extract_dir)
                
                # Buscar imágenes
                for root, dirs, filenames in os.walk(extract_dir):
                    for filename in sorted(filenames):
                        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp')):
                            image_files.append(os.path.join(root, filename))
            
            return sorted(image_files)
        
        # Caso 1: Archivo especial (PDF, ZIP, CBZ, CBR)
        if zip_file and zip_file.filename:
            filename_lower = zip_file.filename.lower()
            
            # Detectar tipo de archivo
            if filename_lower.endswith('.pdf'):
                file_type = 'pdf'
            elif filename_lower.endswith('.cbz') or (filename_lower.endswith('.zip') and not filename_lower.endswith('.cbz')):
                file_type = 'zip'
            elif filename_lower.endswith('.cbr'):
                file_type = 'cbr'
            else:
                raise HTTPException(status_code=400, detail="Formato no soportado. Use: PDF, ZIP, CBZ, o CBR")
            
            print(f"[BATCH {batch_id}] Processing {file_type.upper()}: {zip_file.filename}")
            
            # Guardar archivo temporalmente
            file_extension = '.pdf' if file_type == 'pdf' else ('.cbr' if file_type == 'cbr' else '.zip')
            temp_path = os.path.join(UPLOAD_DIR, f"temp_{batch_id}{file_extension}")
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(zip_file.file, buffer)
            
            # Extraer imágenes usando función helper
            image_files = extract_images_from_archive(temp_path, file_type)
            
            # Crear tareas
            for i, img_path in enumerate(image_files):
                unique_filename = f"{uuid.uuid4()}.jpg"
                dest = os.path.join(UPLOAD_DIR, unique_filename)
                shutil.copy(img_path, dest)
                
                job_id = job_manager.create_job()
                job_manager.update_job(job_id, status="pending", progress=0, step="En cola...")
                
                tasks.append({
                    "file_path": dest,
                    "filename": unique_filename,
                    "page_number": i + 1,
                    "job_id": job_id
                })
            
            # Limpiar archivos temporales
            extract_dir = os.path.join(UPLOAD_DIR, f"extract_{batch_id}")
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            print(f"[BATCH {batch_id}] {file_type.upper()} extracted: {len(tasks)} images")
        
        # Caso 2: Múltiples archivos
        elif files and len(files) > 0:
            print(f"[BATCH {batch_id}] Processing {len(files)} files")
            
            for i, file in enumerate(files):
                # Guardar archivo
                unique_filename = f"{uuid.uuid4()}.jpg"
                file_path = os.path.join(UPLOAD_DIR, unique_filename)
                
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # Crear job
                job_id = job_manager.create_job()
                job_manager.update_job(job_id, status="pending", progress=0, step="En cola...")
                
                tasks.append({
                    "file_path": file_path,
                    "filename": unique_filename,
                    "page_number": i + 1,
                    "job_id": job_id
                })
        
        else:
            raise HTTPException(status_code=400, detail="No files or zip provided")
        
        
        # Procesar en background usando Thread directo para asegurar ejecución
        # A veces BackgroundTasks de FastAPI puede fallar silenciosamente con pools anidados
        from threading import Thread
        thread = Thread(target=process_batch_task, args=(project_id, batch_id, tasks))
        thread.start()
        
        print(f"[BATCH API] Thread started for batch {batch_id}")
        
        return {
            "batch_id": batch_id,
            "total_pages": len(tasks),
            "job_ids": [t["job_id"] for t in tasks],
            "message": f"Batch processing started: {len(tasks)} pages"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")


