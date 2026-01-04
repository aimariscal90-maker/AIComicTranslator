from huggingface_hub import hf_hub_download
import shutil
import os

def download_model():
    repo_id = "kitsumed/yolov8m_seg-speech-bubble"
    filename = "model.pt"
    local_dir = "models"
    
    print(f"Downloading {filename} from {repo_id}...")
    
    # Crear carpeta models si no existe
    os.makedirs(local_dir, exist_ok=True)
    
    # Descargar el archivo
    model_path = hf_hub_download(repo_id=repo_id, filename=filename)
    
    # Moverlo a nuestra carpeta models con un nombre claro
    destination = os.path.join(local_dir, "comic_yolov8m_seg.pt")
    
    shutil.copy(model_path, destination)
    print(f"Model saved to {destination}")

if __name__ == "__main__":
    download_model()
