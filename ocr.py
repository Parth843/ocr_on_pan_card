from PIL import Image
import pytesseract
import argparse
import cv2
import os
import re
import io
import json
import ftfy

# To be able to take args from terminal
ap = argparse.ArgumentParser()
ap.add_argument(
    "--image",
    required=True,
    help="Path to image of PAN card"
)
args = vars(ap.parse_args())

# Read image and perform preprocessing
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# Add pytesseract-ocr to path
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract'

# Create and save a temporary file to apply ocr 
filename = "{}.png".format(os.getpid())
cv2.imwrite(filename, gray)

# Load the temporary file as PIL image and use tesseract on it
text = pytesseract.image_to_string(Image.open(filename), lang='eng')

# Delete the temporary file
os.remove(filename)

# Clean the character strings recognised
text = ftfy.fix_text(text)
text = ftfy.fix_encoding(text)
text = text.split('\n')
#print(text.split('\n'))

# Extract PAN Number and Date of Birth from the recognised strings
def get_data_from_text(pattern, text_list):
    for element in text_list:
        data = re.search(pattern, element)
        if data:
            found_str = data.groups(0)[0]
            return found_str

dob = get_data_from_text(r'(\d+/\d+/\d+)', text)

pan = get_data_from_text('([A-Z]{5}[0-9]{4}[A-Z])', text)

# Print the extracted values to console
data = {}
data['Date of Birth'] = dob
data['PAN Number'] = pan

for k, v in data.items():
    print(f'{k}: {v}')
