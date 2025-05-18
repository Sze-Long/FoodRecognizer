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

load_dotenv()

GEM_KEY = os.getenv("GEM_KEY")
USA_KEY = os.getenv("USA_KEY")
API_KEY = os.getenv("API_KEY")
MON_KEY = os.getenv("MON_KEY")

def take_photo():
    # Open the webcam (0 is the default camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
        
    ret, frame = cap.read()

    cv2.imwrite('captured_photo.jpg', frame)
    print("Photo captured and saved as 'captured_photo.jpg'")

    cap.release()

    image_file_path = 'captured_photo.jpg'
    
    #second image save
    # Create a folder with the current date (if it doesn't already exist)
    folder_path = f'static/uploads'
    os.makedirs(folder_path, exist_ok=True)

    # Set the destination path where the image will be saved
    destination_path = os.path.join(folder_path, f'captured_photo.jpg')

    # Move or copy the image to the folder
    shutil.copy(image_file_path, destination_path)

    print(f"Image saved to: {destination_path}")

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

    return f'images/{current_date}/{current_time} {food}.jpg'

def move_image(path):
    # Set your image file path (this can be the path where your image is currently stored)
    image_file_path = path

    # Create a folder with the current date (if it doesn't already exist)
    folder_path = f'static/uploads'
    os.makedirs(folder_path, exist_ok=True)

    # Set the destination path where the image will be saved
    destination_path = os.path.join(folder_path, 'captured_photo.jpg')

    shutil.copy(image_file_path, destination_path)

def save_data(food, image, Using):
    current_date = datetime.now().strftime('%Y-%m-%d')
    MON_KEY = os.getenv("MON_KEY")
    MONGO_URI = MON_KEY
    DATABASE_NAME = "foodDB"
    COLLECTION_NAME = current_date

    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # Food document example
    food_data = {
        "food_name": food,
        "image_name": image,
        "nutrient_grid": Using
    }

    # Insert the document into the database
    result = collection.insert_one(food_data)
    print("Document inserted with ID:", result.inserted_id)

def get_data(date,num):
    MONGO_URI = MON_KEY
    client = MongoClient(MONGO_URI)
    db = client["foodDB"]
    collection = db[date]

    # Query: Find all documents with food_name, image_name, and nutrient_grid
    results = collection.find({}, {
        "_id": 0,  # exclude MongoDB's internal _id field
        "food_name": 1,
        "image_name": 1,
        "nutrient_grid": 1
    }).skip(num).limit(1)

    doc = next(results, None)  # Get the first (and only) result or None

    if not doc:
        print("No data found in the database.")
        return None, []  # Safe fallback
    # Print the results
    for doc in results:
        print("Food Name:", doc["food_name"])
        print("Image Name:", doc["image_name"])
        print("Nutrient Grid:")
        for row in doc["nutrient_grid"]:
            print("  ", row)
        print("-" * 40)

    return doc["image_name"], doc["nutrient_grid"]

def get_weight(food):
    client = genai.Client(api_key=GEM_KEY)

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=f"Estimate the weight in grams of a serving of '{food}'. Just give a number.",
    )
    print(int(response.text))

    return int(response.text)
    
def get_food(candidates):
    client = genai.Client(api_key=GEM_KEY)

    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=f"From this list of items, get the first item that is a specific food. Just give the name only: {candidates}, otherwise say None",
    )
    print(response.text)

    return response.text


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
    candidates = []
    
    # Handle response
    if response.status_code == 200:
        
        # Handle label detections
        labels = response.json()['responses'][0].get('labelAnnotations', [])
        if not labels:
            print("No labels detected.")
        else:
            print("Labels detected:")
            for label in labels:
                description = label['description']
                score = label['score']
                print(f"- {description} ({score:.2f})")
                if score > 0.3:
                    candidates.append(description)
        
        objects = response.json()['responses'][0].get('localizedObjectAnnotations', [])
        if not objects:
            print("No objects localized.")
            return None

        print("Objects localized:")
        for obj in objects:
            name = obj['name']
            score = obj['score']
            print(f"- {name} ({score:.2f})")
            if score > 0.3:
                candidates.append(name)
    else:
        print(f"API error {response.status_code}:")
        print(response.text)

    return candidates

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        take_photo()
        
        candidates = localize_objects("static/uploads/captured_photo.jpg", API_KEY)
        
        servings = float(request.form.get("servings")) if request.form.get("servings") else 1

        food = get_food(candidates).strip()
        weight = get_weight(food)
        image = save_image(food)
        
        #image is the image path saved in images/2025-05-17/11-03-14 food.jpg

        if not food:
            return render_template('index.html')

        print(weight)

        food_item = get_details(food)
        
        ratio = 0

        if 'servingSize' in food_item:
            print(f"Serving Size: {food_item['servingSize']} {food_item['servingSizeUnit']}")
            serving_size = food_item['servingSize']
            ratio = servings * weight / serving_size
        else:
            print("Serving size information not available.")

        Nutrients = ["Protein", "Energy", "Total Sugars","Total lipid (fat)","Carbohydrate, by difference","Fiber, total dietary","Calcium, Ca","Iron, Fe","Sodium, Na","Vitamin A, IU","Vitamin C, total ascorbic acid","Cholesterol","Fatty acids, total trans","Fatty acids, total saturated"]
        Using = []
        row = ["Food", food, ""]
        Using.append(row)
        row = ["Serving(s)", servings, ""]
        Using.append(row)
        # Loop through the nutrients and print their values
        for nutrient in food_item['foodNutrients']:
            if nutrient['nutrientName'] in Nutrients:
                if nutrient['value'] != 0:
                    row = [nutrient['nutrientName'], nutrient['value'] * ratio, nutrient['unitName']]
                    Using.append(row)

        custom_order = {
            "Food": 0,
            "Serving(s)": 1,
            "Energy": 2,
            "Protein": 3,
            "Total lipid (fat)": 4,
            "Carbohydrate, by difference": 5
        }

        # Assign a default sort key if not found in custom_order
        Using_sorted = sorted(Using, key=lambda x: custom_order.get(x[0], 100))

        save_data(food,image,Using_sorted)
        #image is the path to the file when saved
        for each in Using_sorted:
            print(f"{each[0]} and {each[1]} and {each[2]}")
        
        # Get date from user or default to today
        now_date = str(datetime.now().strftime('%Y-%m-%d'))
        return render_template('index.html', cur_date=now_date,image_path=image, results=Using_sorted)
    
    elif request.method == 'GET':
        now_date = str(datetime.now().strftime('%Y-%m-%d'))
        return render_template('index.html', cur_date=now_date)

@app.route('/history/<date>/<int:num>', methods=['GET', 'POST'])
def history(date, num):
    path, Using = get_data(date,num)
    if request.method == "GET":
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        if path != None:
            move_image(path)
            fail = False
        else:
            fail = True
        
        return render_template('history.html', image_path=path, selected_date=date, num=num, results=Using,fail=fail)
    elif request.method == "POST":

        new_date = request.form.get("date")
        if new_date:
            return render_template('history.html', image_path=path, selected_date=new_date, num=num, results=Using)
        else:
            return render_template('history.html', image_path=path, selected_date=date, num=num, results=Using)

#type in console -> python -m flask run
#use link in url -> http://127.0.0.1:5000/

app.run(debug=True)