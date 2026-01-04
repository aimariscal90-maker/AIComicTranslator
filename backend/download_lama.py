import os
from huggingface_hub import hf_hub_download

def download_lama_model():
    repo_id = "fashn-ai/LaMa"
    filename = "big-lama.pt"
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    print(f"Downloading {filename} from {repo_id}...")
    try:
        model_path = hf_hub_download(repo_id=repo_id, filename=filename, local_dir=models_dir)
        print(f"Model downloaded successfully to: {model_path}")
    except Exception as e:
        print(f"Failed to download model: {e}")
        # Fallback to another repo if needed
        print("Trying alternative repo: smartywu/big-lama")
        try:
             # SmartyWU often has it as big-lama.pt or inside zip. 
             # Let's try another direct pt source if first fails.
             repo_id_2 = "anyisalin/big-lama" # Another common one
             filename_2 = "big-lama.pt"
             model_path = hf_hub_download(repo_id=repo_id_2, filename=filename_2, local_dir=models_dir)
             print(f"Model downloaded successfully to: {model_path}")
        except Exception as e2:
             print(f"Fallback failed: {e2}")

if __name__ == "__main__":
    download_lama_model()
