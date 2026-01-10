
import cv2
import numpy as np

def create_demo_comic():
    # Create white canvas
    img = np.full((600, 800, 3), 255, dtype=np.uint8)
    
    # 1. Panel 1: The Shout (Big Text)
    # Draw border
    cv2.rectangle(img, (50, 50), (350, 250), (0, 0, 0), 2)
    # Draw speech bubble (Oval)
    cv2.ellipse(img, (200, 150), (120, 80), 0, 0, 360, (0, 0, 0), 2)
    # Text
    text = "STOP!"
    font_scale = 2.0
    thickness = 4
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
    text_x = 200 - text_size[0] // 2
    text_y = 150 + text_size[1] // 2
    cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)
    
    # 2. Panel 2: The Whisper (Small Text)
    cv2.rectangle(img, (450, 50), (750, 250), (0, 0, 0), 2)
    cv2.ellipse(img, (600, 150), (100, 60), 0, 0, 360, (0, 0, 0), 1)
    text = "please help..."
    font_scale = 0.5
    thickness = 1
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
    text_x = 600 - text_size[0] // 2
    text_y = 150 + text_size[1] // 2
    cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)
    
    # 3. Panel 3: Color Text (Red)
    cv2.rectangle(img, (50, 300), (350, 500), (0, 0, 0), 2)
    cv2.rectangle(img, (100, 350), (300, 450), (0, 0, 0), 2) # Box bubble
    text = "DANGER"
    font_scale = 1.2
    thickness = 3
    color = (0, 0, 255) # Red in BGR
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
    text_x = 200 - text_size[0] // 2
    text_y = 400 + text_size[1] // 2
    cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
    
    # 4. Panel 4: Inverted (White on Black)
    cv2.rectangle(img, (450, 300), (750, 500), (0, 0, 0), -1) # Filled black panel
    text = "DARKNESS"
    font_scale = 1.0
    thickness = 2
    color = (255, 255, 255) # White
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
    text_x = 600 - text_size[0] // 2
    text_y = 400 + text_size[1] // 2
    cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

    output_path = "demo_comic.png"
    cv2.imwrite(output_path, img)
    print(f"✅ Demo image created at: {output_path}")

if __name__ == "__main__":
    create_demo_comic()
