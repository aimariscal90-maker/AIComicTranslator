
import shutil
import uuid
import os
import zipfile
import json
import cv2
import traceback
from datetime import datetime
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from database import get_db, SessionLocal
from models import Project, Page, Bubble
from services.queue_manager import JobManager

# Pre-import AI Services
print("[BOOT] Pre-loading AI Services...")
# Pre-import AI Services
print("[BOOT] Pre-loading AI Services...")
from services.detector import BubbleDetector
from services.inpainting import TextRemover
from services.ocr import OCRService
from services.translator import TranslatorService
from services.renderer import TextRenderer
from services.style_analyzer import StyleAnalyzer
import numpy as np
print("[BOOT] AI Services loaded successfully.")

app = FastAPI(title="AI Comic Translator API", version="0.8.0")
job_manager = JobManager()

# Configs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# CORS
origins = ["*"] # Allow all for dev, tighten for prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# --- CORE LOGIC ---

def process_comic_task(job_id: str, file_path: str, unique_filename: str, project_id: str = None, page_number: int = None, mode: str = "full"):
    """
    Main pipeline task.
    Modes:
    - 'full': Detect -> OCR -> Translate -> Inpaint -> Render
    - 'clean_only': Detect -> Inpaint (Skip OCR/Translate/Render)
    """
    try:
        job_manager.update_job(job_id, status="processing", progress=10, step="Initializing AI Models...")
        
        # 1. Image Optimization (Smart Downscaling)
        if not os.path.exists(file_path):
             raise Exception(f"File not found: {file_path}")
        
        file_size = os.path.getsize(file_path)
        print(f"[TASK] Processing {unique_filename} (Size: {file_size} bytes)")
        
        if file_size == 0:
             raise Exception("File is empty (0 bytes)")

        img_temp = cv2.imread(file_path)
        if img_temp is None:
            # Try valid image check
            print(f"[TASK WARNING] cv2.imread failed for {file_path}. Checking permissions/format.")
            raise Exception("Cv2 failed to read image. Corrupt or unsupported format.")
            
        h, w = img_temp.shape[:2]
        max_dim = 2500 # High res for comics
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            print(f"[TASK] Resizing image from {w}x{h} to {new_w}x{new_h}")
            success = cv2.imwrite(file_path, cv2.resize(img_temp, (new_w, new_h), interpolation=cv2.INTER_AREA))
            if not success:
                print(f"[TASK WARNING] Failed to overwrite resized image")

        # 2. Detector
        job_manager.update_job(job_id, progress=20, step="Detecting Bubbles 🕵️")
        detector = BubbleDetector()
        
        # Verify again before YOLO
        if not os.path.exists(file_path): raise Exception("File vanished before detection")
        
        bubbles = detector.detect(file_path)
        
        # Generate debug image
        debug_filename = f"debug_{unique_filename}"
        detector.draw_boxes(file_path, bubbles, os.path.join(UPLOAD_DIR, debug_filename))

        # 3. Contextual Processing based on Mode
        if mode == "full" or mode == "premium":
            # --- FULL & PREMIUM TRANSLATION PIPELINE ---
            
            # OCR
            job_manager.update_job(job_id, progress=40, step="Reading Text (OCR) 📖")
            ocr_service = OCRService()
            
            # Helper: Extract crops and run OCR
            img_cv = cv2.imread(file_path)
            
            # Initialize StyleAnalyzer if Premium
            if mode == "premium":
                style_analyzer = StyleAnalyzer()
                job_manager.update_job(job_id, progress=45, step="Analyzing Art Style 🎨")
            
            for bubble in bubbles:
                x1, y1, x2, y2 = map(int, bubble['bbox'])
                crop = img_cv[y1:y2, x1:x2]
                if crop.size > 0:
                    success, encoded = cv2.imencode('.jpg', crop)
                    if success:
                        res = ocr_service.detect_text(encoded.tobytes())
                        bubble['text'] = res.get('text', '')
                        bubble['clean_text'] = bubble['text'].replace('\n', ' ')
                        
                        # PREMIUM: Style Analysis
                        if mode == "premium":
                            try:
                                style = style_analyzer.analyze_roi(img_cv, bubble['bbox'])
                                # Inject Style into Bubble for Renderer
                                bubble['text_color'] = style.get('text_color', '#000000')
                                # bubble['font'] = style.get('font_match', 'AnimeAce') # Future
                                
                                # Store raw style for debug
                                bubble['style_data'] = style
                            except Exception as e:
                                print(f"Style Analysis failed for bubble: {e}")

            # Translate
            job_manager.update_job(job_id, progress=60, step="Translating 🤖")
            translator = TranslatorService(target_lang='es')
            texts = [b.get('clean_text', '') for b in bubbles if b.get('clean_text')]
            if texts:
                translations, _ = translator.translate_batch_with_context(texts)
                t_idx = 0
                for b in bubbles:
                    if b.get('clean_text'):
                        b['translation'] = translations[t_idx] if t_idx < len(translations) else ""
                        t_idx += 1
            
            # Inpaint
            job_manager.update_job(job_id, progress=75, step="Cleaning Text 🎨")
            remover = TextRemover()
            clean_filename = f"clean_text_{unique_filename}"
            # Use 'text' mask mode for Premium to respect bubbles
            mask_mode = 'text' if (mode == "premium") else 'bubble'
            # ACTUALLY: We already forced 'text' masking as default in inpainting.py based on user request ("El borrado selectivo")
            # So mode doesn't matter much here, but let's be explicit
            remover.remove_text(file_path, bboxes=bubbles, output_path=os.path.join(UPLOAD_DIR, clean_filename), fast_mode=True)
            
            # Render
            job_manager.update_job(job_id, progress=90, step="Rendering Text ✍️")
            renderer = TextRenderer()
            final_filename = f"final_{unique_filename}"
            renderer.render_text(os.path.join(UPLOAD_DIR, clean_filename), bubbles, os.path.join(UPLOAD_DIR, final_filename))
            
            final_url = f"/uploads/{final_filename}"
            clean_url = f"/uploads/{clean_filename}"

        elif mode == "clean_only":
            # --- CLEANER ONLY PIPELINE ---
            job_manager.update_job(job_id, progress=50, step="Removing Bubbles (Magic Eraser)...")
            remover = TextRemover()
            clean_filename = f"clean_text_{unique_filename}"
            # In clean_only, we might want 'mask_mode="bubbles"' to clear the whole bubble or 'text' to keep bubble shape?
            # User said "borrar los bocadillos y textos". Let's assume standard text removal for now.
            # Usually strict clean removes the text. If they want to remove the *bubble shape* that's 'inpainting whole bbox'.
            # TextRemover `mask_mode` defaults to 'text' (text mask).
            # If we want to remove the bubble, we should pass mask_mode='bbox' or similar if supported.
            # Assuming 'text' is safer for now to preserve art behind text.
            remover.remove_text(file_path, bboxes=bubbles, output_path=os.path.join(UPLOAD_DIR, clean_filename), fast_mode=True)
            
            final_url = f"/uploads/{clean_filename}" # Final result IS the clean image
            clean_url = f"/uploads/{clean_filename}"
            
            # Clear text data for safety
            for b in bubbles:
                b['text'] = ""
                b['translation'] = ""

        # Save Metadata
        json_path = os.path.join(UPLOAD_DIR, f"metadata_{unique_filename}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(bubbles, f, default=str)

        # Database (If Project)
        if project_id:
            try:
                db = SessionLocal()
                page = Page(
                    project_id=project_id,
                    filename=unique_filename,
                    original_url=f"/uploads/{unique_filename}",
                    final_url=final_url,
                    clean_url=clean_url,
                    debug_url=f"/uploads/{debug_filename}",
                    status="completed"
                )
                db.add(page)
                db.commit()
                db.close()
            except Exception as e:
                print(f"[DB ERROR] {e}")

        # Complete
        result = {
            "id": unique_filename,
            "filename": unique_filename,
            "original_url": f"/uploads/{unique_filename}",
            "final_url": final_url,
            "clean_url": clean_url,
            "bubbles_data": bubbles
        }
        job_manager.update_job(job_id, status="completed", progress=100, result=result)

    except Exception as e:
        traceback.print_exc()
        job_manager.update_job(job_id, status="failed", error=str(e))

# --- ENDPOINTS ---

@app.get("/")
def root():
    return {"status": "ok", "version": "0.8.0"}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Legacy upload endpoint (useful for tests)
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Invalid file")
    ext = file.filename.split(".")[-1]
    name = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, name)
    
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"filename": name, "url": f"/uploads/{name}"}

@app.post("/process")
async def process_comic(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    project_id: Optional[str] = Form(None),
    mode: str = Form("full")
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Invalid file type")
    
    ext = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, unique_name)
    
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    job_id = job_manager.create_job()
    background_tasks.add_task(process_comic_task, job_id, path, unique_name, project_id, None, mode)
    return {"job_id": job_id, "status": "queued"}

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    return job_manager.get_job(job_id)

# Projects
@app.get("/projects")
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).options(joinedload(Project.pages)).order_by(Project.created_at.desc()).all()

# We need the Pydantic models
class CreateProjectSchema(BaseModel):
    name: str
    description: Optional[str] = None

@app.post("/projects")
def create_project_endpoint(req: CreateProjectSchema, db: Session = Depends(get_db)):
    p = Project(name=req.name, description=req.description)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@app.get("/projects/{pid}")
def get_project(pid: str, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == pid).first()
    if not p: raise HTTPException(404, "Not found")
    return p

@app.get("/projects/{pid}/export")
def export_project(pid: str, format: str = "cbz", db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == pid).first()
    if not project: raise HTTPException(404, "Not found")
    
    pages = db.query(Page).filter(Page.project_id == pid).order_by(Page.page_number).all()
    if not pages: raise HTTPException(400, "No pages")
    
    safe_name = "".join([c for c in project.name if c.isalnum() or c in (' ','-')]).strip()
    fname = f"{safe_name}.{format}"
    zip_path = os.path.join(UPLOAD_DIR, fname)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for i, p in enumerate(pages):
            url = p.final_url or p.clean_url or p.original_url
            if url:
                dname = url.split("/")[-1]
                if os.path.exists(os.path.join(UPLOAD_DIR, dname)):
                    ext = dname.split(".")[-1]
                    zf.write(os.path.join(UPLOAD_DIR, dname), f"Page_{i+1:03}.{ext}")
                    
    return FileResponse(zip_path, filename=fname)

# Editing
class UpdateBubbleModel(BaseModel):
    bubble_index: int
    new_text: str
    font: str = "ComicNeue"

@app.patch("/process/{filename}/update-bubble")
async def update_bubble(filename: str, req: UpdateBubbleModel):
    # Retrieve metadata -> Update JSON -> Render -> Return
    try:
        json_path = os.path.join(UPLOAD_DIR, f"metadata_{filename}.json")
        with open(json_path, "r") as f: data = json.load(f)
        
        data[req.bubble_index]['translation'] = req.new_text
        data[req.bubble_index]['font'] = req.font
        
        with open(json_path, "w") as f: json.dump(data, f)
        
        # Render
        clean_path = os.path.join(UPLOAD_DIR, f"clean_text_{filename}")
        if not os.path.exists(clean_path): clean_path += ".jpg" # Fallback extension
        
        renderer = TextRenderer()
        final_path = os.path.join(UPLOAD_DIR, f"final_{filename}.jpg")
        renderer.render_text(clean_path, data, final_path)
        
        return {"final_url": f"/uploads/final_{filename}.jpg"}
    except Exception as e:
        raise HTTPException(500, str(e))
