from pymongo import MongoClient
from datetime import datetime
import shutil
from datetime import datetime

# Replace with your MongoDB Atlas connection string
MONGO_URI = 
DATABASE_NAME = "foodDB"
COLLECTION_NAME = "food"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

food = "Banana"
current_date = datetime.now().strftime('%Y-%m-%d')
COLLECTION_NAME = current_date

# Food document example
food_data = {
    "food_name": food,
    "image_name": "avocado_toast.jpg",
    "date_added": datetime.now(),
    "nutrition": ["Calories", "Protein", "Fat"],
    "numbers": [250, 6, 20],
    "units": ["kcal", "g", "g"]
}

# Insert the document into the database
result = collection.insert_one(food_data)
print("Document inserted with ID:", result.inserted_id)
