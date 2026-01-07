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
from database import get_db
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

# --- ASYNC TASK LOGIC ---
def process_comic_task(job_id: str, file_path: str, unique_filename: str, project_id: str = None):
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

        # 1. Detección
        job_manager.update_job(job_id, progress=20, step="Detectando Bocadillos 🕵️")
        detector = BubbleDetector()
        bubbles = detector.detect(file_path)
        
        # 2. OCR
        job_manager.update_job(job_id, progress=40, step="Leyendo Texto (OCR) 📖")
        ocr_service = OCRService()
        
        # 3. Traducción
        job_manager.update_job(job_id, progress=50, step="Traduciendo (Gemini) 🤖")
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

        # 4. Inpainting
        job_manager.update_job(job_id, progress=70, step="Borrando Texto Original 🎨")
        
        debug_filename = f"debug_{unique_filename}"
        debug_path = os.path.join(UPLOAD_DIR, debug_filename)
        detector.draw_boxes(file_path, bubbles, debug_path)
        
        remover = TextRemover()
        clean_text_filename = f"clean_text_{unique_filename}"
        clean_text_path = os.path.join(UPLOAD_DIR, clean_text_filename)
        clean_bubble_filename = None
        remover.remove_text(file_path, bboxes=bubbles, output_path=clean_text_path, mask_mode='text')
        
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
                    status="completed"
                )
                db.add(page)
                db.commit()
                db.refresh(page)
                
                # Crear registros Bubble
                for bubble_data in bubbles:
                    bubble = Bubble(
                        page_id=page.id,
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
                
                print(f"[DB] Page saved: {page.id} with {len(bubbles)} bubbles")
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
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
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
