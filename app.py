import cv2
from google import genai
from flask import Flask, render_template, request
import os
import json
import io
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

def take_photo():
    # Open the webcam (0 is the default camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()
    ret, frame = cap.read()

    cv2.imwrite('captured_photo.jpg', frame)
    print("Photo captured and saved as 'captured_photo.jpg'")

    cap.release()

GEM_KEY = os.getenv("GEM_KEY")
def Calories(food):
    client = genai.Client(api_key=GEM_KEY)

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=f"Just return calories {food} of as a number"
    )
    print(int(response.text))

Calories("Banana")

API_KEY = os.getenv("API_KEY")

"""
def localize_objects(image_path, api_key):
    # Read image file
    with io.open(image_path, 'rb') as image_file:
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
                "features": [{"type": "OBJECT_LOCALIZATION", "maxResults": 10}]
            }
        ]
    }

    # Send request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Handle response
    if response.status_code == 200:
        objects = response.json()['responses'][0].get('localizedObjectAnnotations', [])
        if not objects:
            print("No objects localized.")
            return

        print("Objects localized:")
        for obj in objects:
            name = obj['name']
            score = obj['score']
            box = obj['boundingPoly']['normalizedVertices']
            print(f"- {name} ({score:.2f})")
            for i, vertex in enumerate(box):
                x = vertex.get('x', 0)
                y = vertex.get('y', 0)
                print(f"  Vertex {i+1}: x={x:.2f}, y={y:.2f}")
    else:
        print(f"API error {response.status_code}:")
        print(response.text)

# Example usage
api_key = API_KEY  # Replace this with your actual API key
localize_objects("captured_photo.jpg", api_key)
"""


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        take_photo()
        return render_template('index.html')
    else:
        return render_template('index.html')

#type in console -> python -m flask run
#use link in url -> http://127.0.0.1:5000/