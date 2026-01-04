from huggingface_hub import list_repo_files

def list_files():
    repo_id = "kitsumed/yolov8m_seg-speech-bubble"
    print(f"Listing files for {repo_id}...")
    files = list_repo_files(repo_id)
    for f in files:
        print(f)

if __name__ == "__main__":
    list_files()
