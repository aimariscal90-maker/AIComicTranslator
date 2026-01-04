from ultralytics import YOLO
import os

def check():
    model_path = os.path.join("models", "comic_yolov8m_seg.pt")
    if not os.path.exists(model_path):
        print("Model not found")
        return

    print(f"Loading {model_path}...")
    model = YOLO(model_path)
    print(f"Model Task: {model.task}")
    
    # Try a dummy prediction
    # results = model("test.jpg") # Need an image
    # print(f"Results masks: {results[0].masks}")

if __name__ == "__main__":
    check()
