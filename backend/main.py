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
        
        # Detector
        detector = BubbleDetector()
        bubbles = detector.detect(file_path)
        
        # Debug: Dibujar cajas
        debug_filename = f"debug_{unique_filename}"
        debug_path = os.path.join(UPLOAD_DIR, debug_filename)
        detector.draw_boxes(file_path, bubbles, debug_path)
        
        # Inpainting (Remover texto)
        remover = TextRemover()
        clean_filename = f"clean_{unique_filename}"
        clean_path = os.path.join(UPLOAD_DIR, clean_filename)
        remover.remove_text(file_path, bboxes=bubbles, output_path=clean_path)
        
        return {
            "status": "success",
            "original_url": f"/uploads/{unique_filename}",
            "debug_url": f"/uploads/{debug_filename}",
            "clean_url": f"/uploads/{clean_filename}",
            "bubbles_count": len(bubbles),
            "bubbles_data": bubbles
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI Processing failed: {str(e)}")
