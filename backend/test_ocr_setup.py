from google.cloud import vision
import os
import io

def test_ocr():
    # Setup credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_credentials.json"
    
    # Initialize client
    client = vision.ImageAnnotatorClient()
    
    # Use a dummy image or create one
    # Let's create a simple text image using PIL if possible, or just try to connect
    print("Google Vision Client initialized.")
    
    # Attempt to read a file (we can use one of the uploads if any, or just a dummy request)
    # Better: just check if we can instantiate without error first
    try:
        # Construct an image object (empty/dummy just to check auth, 
        # though empty byte content might raise error, let's use a real file if possible)
        # We can use the 'test_gen_image.jpg' created by test_api_local.py or just create a new one
        pass
    except Exception as e:
        print(f"Error: {e}")

    print("Credentials file found and loaded into env.")
    
if __name__ == "__main__":
    if not os.path.exists("google_credentials.json"):
        print("ERROR: google_credentials.json not found!")
    else:
        test_ocr()
