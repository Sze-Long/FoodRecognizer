from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
MON_KEY = os.getenv("MON_KEY")
MONGO_URI = MON_KEY
client = MongoClient(MONGO_URI)
db = client["foodDB"]
collection = db["2025-05-17"]

# Query: Find all documents with food_name, image_name, and nutrient_grid
results = collection.find({}, {
    "_id": 0,  # exclude MongoDB's internal _id field
    "food_name": 1,
    "image_name": 1,
    "nutrient_grid": 1
}).skip(0).limit(1)

# Print the results
for doc in results:
    print("Food Name:", doc["food_name"])
    print("Image Name:", doc["image_name"])
    print("Nutrient Grid:")
    for row in doc["nutrient_grid"]:
        print("  ", row)
    print("-" * 40)

