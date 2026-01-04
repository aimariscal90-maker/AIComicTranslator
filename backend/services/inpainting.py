import cv2
import numpy as np

class TextRemover:
    def __init__(self):
        # Future: Load LaMa model here
        pass

    def remove_text(self, image_path: str, bboxes: list = None, output_path: str = None):
        """
        Removes text from the image using inpainting.
        If bboxes provided, creates a mask from bboxes.
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image {image_path}")
            
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        
        # If we have bboxes, create mask
        if bboxes:
            for item in bboxes:
                # bbox format: [x1, y1, x2, y2]
                x1, y1, x2, y2 = map(int, item['bbox'])
                
                # Expand slightly to cover edge artifacts (padding)
                pad = 10
                h, w = mask.shape
                x1 = max(0, x1 - pad)
                y1 = max(0, y1 - pad)
                x2 = min(w, x2 + pad)
                y2 = min(h, y2 + pad)
                
                cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
                
        # Simple telea inpainting for MVP (OpenCV built-in)
        # Radius 3, generic algorithm
        result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
        
        if output_path:
            cv2.imwrite(output_path, result)
            return output_path, result
            
        return result
