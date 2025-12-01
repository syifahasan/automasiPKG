import cv2
import numpy as np
import pytesseract
from PIL import Image
import matplotlib.pyplot as plt
import requests
from io import BytesIO

class SimpleCaptchaSolver:
    def __init__(self):
        self.preprocessing_methods = [
            self._threshold,
            self._denoise,
            self._morphology
        ]
    
    def preprocess_image(self, image):
        """Preprocess CAPTCHA image for better OCR results"""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply preprocessing techniques
        processed = gray.copy()
        for method in self.preprocessing_methods:
            processed = method(processed)
        
        return processed
    
    def _threshold(self, image):
        """Apply thresholding"""
        _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
    
    def _denoise(self, image):
        """Remove noise"""
        denoised = cv2.medianBlur(image, 3)
        return denoised
    
    def _morphology(self, image):
        """Apply morphological operations"""
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        return cleaned
    
    def solve_captcha(self, image_path):
        """Solve CAPTCHA using OCR"""
        # Load image
        if isinstance(image_path, str):
            image = cv2.imread(image_path)
        else:
            image = image_path
        
        # Preprocess
        processed = self.preprocess_image(image)
        
        # OCR configuration for CAPTCHA
        config = '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        # Extract text
        text = pytesseract.image_to_string(processed, config=config)
        
        return text.strip()

# Usage example
solver = SimpleCaptchaSolver()
# result = solver.solve_captcha('captcha.png')
# print(f"Detected text: {result}")