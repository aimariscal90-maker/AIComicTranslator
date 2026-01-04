import requests
import cv2
import numpy as np
import os
import time

def test_pipeline():
    # 1. Crear imagen de prueba (Fake comic page)
    # Fondo negro, rectangulo blanco (bocadillo), texto negro
    img = np.zeros((600, 600, 3), dtype=np.uint8)
    # Bocadillo 1
    cv2.rectangle(img, (50, 50), (250, 150), (255, 255, 255), -1)
    cv2.putText(img, "TEST TEXT 01", (60, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    # Bocadillo 2
    cv2.rectangle(img, (300, 300), (500, 400), (255, 255, 255), -1)
    cv2.putText(img, "TEST TEXT 02", (310, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    test_filename = "test_gen_image.jpg"
    cv2.imwrite(test_filename, img)
    print(f"Created test image: {test_filename}")

    url = "http://localhost:8000/process"
    
    try:
        print(f"Connecting to {url}...")
        with open(test_filename, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
            
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n----- SUCCESS -----")
            print(f"Bubbles Detected: {data.get('bubbles_count')}")
            print(f"Original URL: {data.get('original_url')}")
            print(f"Cleaned URL: {data.get('clean_url')}")
            print("-------------------")
        else:
            print("\n----- FAILED -----")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"\n[ERROR] Connection failed. Is the backend running? Exception: {e}")
        
    finally:
        # Cleanup
        if os.path.exists(test_filename):
            os.remove(test_filename)

if __name__ == "__main__":
    # Wait a bit if we just started the server
    time.sleep(2) 
    test_pipeline()
