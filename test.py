import cv2
from google import genai
from flask import Flask, render_template, request
import os
import json
import io
import base64
import requests
from dotenv import load_dotenv
import shutil
from datetime import datetime
from pymongo import MongoClient
from werkzeug.utils import secure_filename
# Load environment variables from .env file
load_dotenv()

# Retrieve API credentials
GEM_KEY = os.getenv("GEM_KEY")
USA_KEY = os.getenv("USA_KEY")
API_KEY = os.getenv("API_KEY")  # Ensure this points to the correct service account JSON path
MON_KEY = os.getenv("MON_KEY")

# Load environment variables from .env file
load_dotenv()
api_key = API_KEY
# Set your Google Cloud credentials path here
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = api_key  # Update this with the correct path

# Open the default webcam (index 0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Read a single frame from the webcam
ret, frame = cap.read()

# Release the webcam
cap.release()

# Check if frame was read successfully
if ret:
    # Save the captured frame
    cv2.imwrite("captured_photo.jpg", frame)
    print("Photo saved as 'captured_photo.jpg'")
else:
    print("Error: Could not read frame from webcam.")
# Read image file
    with io.open('captured_photo.jpg', 'rb') as image_file:
        content = image_file.read()

    # Base64 encode image
    encoded_image = base64.b64encode(content).decode('utf-8')

    # Vision API endpoint
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    headers = {"Content-Type": "application/json"}

    # Object Localization request payload
payload = {
    "requests": [
        {
            "image": {"content": encoded_image},
            "features": [
                {"type": "OBJECT_LOCALIZATION", "maxResults": 5},
                {"type": "LABEL_DETECTION", "maxResults": 5}
            ]
        }
    ]
}

# Send request
response = requests.post(url, headers=headers, data=json.dumps(payload))

print(response)