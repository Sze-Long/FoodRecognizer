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

load_dotenv()

GEM_KEY = os.getenv("GEM_KEY")
USA_KEY = os.getenv("USA_KEY")
API_KEY = os.getenv("API_KEY")


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

def save_image(food):
    # Set your image file path (this can be the path where your image is currently stored)
    image_file_path = 'captured_photo.jpg'

    # Get the current date in YYYY-MM-DD format
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H-%M-%S')

    # Create a folder with the current date (if it doesn't already exist)
    folder_path = f'images/{current_date}'
    os.makedirs(folder_path, exist_ok=True)

    # Set the destination path where the image will be saved
    destination_path = os.path.join(folder_path, f'{current_time} {food}.jpg')

    # Move or copy the image to the folder
    shutil.copy(image_file_path, destination_path)

    print(f"Image saved to: {destination_path}")


def get_weight(food):
    client = genai.Client(api_key=GEM_KEY)

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=f"Just return of one serving of weight in grams {food} of as a number"
    )
    return(int(response.text))


def get_details(food):
    usa_key = USA_KEY

    # Construct the URL for the search request
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "query": food,
        "api_key": usa_key,
        # "dataType": ["Foundation", "SR Legacy"],  # avoid branded items
        "pageSize": 1  # just get the top match
    }

    
    # Send the GET request
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response

        food_data = response.json()

        # Get the first food item from the search results
        
        results = food_data.get('foods', [])

        food_item = results[0]

        return food_item
            
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


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
            if name == "Clothing" or name == "Person": 
                continue
            return name
            # score = obj['score']
            # box = obj['boundingPoly']['normalizedVertices']
            # print(f"- {name} ({score:.2f})")
            # for i, vertex in enumerate(box):
            #     x = vertex.get('x', 0)
            #     y = vertex.get('y', 0)
            #     print(f"  Vertex {i+1}: x={x:.2f}, y={y:.2f}")
    else:
        print(f"API error {response.status_code}:")
        print(response.text)


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        take_photo()
        
        food = localize_objects("captured_photo.jpg", API_KEY)
        print(food)
        serving_size = 1

        save_image(food)

        weight = get_weight(food)

        food_item = get_details(food)

        ratio = 0

        if 'servingSize' in food_item:
            print(f"Serving Size: {food_item['servingSize']} {food_item['servingSizeUnit']}")
            data_serving_size = food_item['servingSize']
            ratio = serving_size * weight / data_serving_size
        else:
            print("Serving size information not available.")

        Nutrients = ["Protein", "Energy", "Total Sugars","Total lipid (fat)","Carbohydrate, by difference","Fiber, total dietary","Calcium, Ca","Iron, Fe","Sodium, Na","Vitamin A, IU","Vitamin C, total ascorbic acid","Cholesterol","Fatty acids, total trans","Fatty acids, total saturated"]
        Using = []
        # Loop through the nutrients and print their values
        for nutrient in food_item['foodNutrients']:
            if nutrient['nutrientName'] in Nutrients:
                if nutrient['value'] != 0:
                    row = [nutrient['nutrientName'], nutrient['value'] * ratio, nutrient['unitName']]
                    Using.append(row)

        custom_order = {
            "Energy": 0,
            "Protein": 1,
            "Total lipid (fat)": 2,
            "Carbohydrate, by difference": 3
        }

        # Assign a default sort key if not found in custom_order
        Using_sorted = sorted(Using, key=lambda x: custom_order.get(x[0], 100))

        for each in Using_sorted:
            print(f"{each[0]} and {each[1]} and {each[2]}")
        return render_template('index.html', results=Using_sorted)
    else:
        return render_template('index.html', results="none")

#type in console -> python -m flask run
#use link in url -> http://127.0.0.1:5000/
