import cv2
import pytesseract
from PIL import Image

# 1. Point to the Tesseract executable (Required for Windows users)
# If Tesseract is in your PATH, you can comment this line out.
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    try:
        # 2. Load the image using OpenCV
        image = cv2.imread(image_path)

        # 3. Pre-processing: Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 4. Optional: Apply thresholding to make text stand out (Useful for handwriting)
        # This converts the image to black and white only
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # 5. Perform OCR
        # '--psm 6' assumes a single uniform block of text. 
        # Use '--psm 3' for fully automatic page segmentation.
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(gray, config=custom_config)

        return text

    except Exception as e:
        return f"An error occurred: {e}"