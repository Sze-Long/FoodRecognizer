from flask import Flask, render_template
import os

env = os.environ
API_KEY = env.get("API_KEY")

app = Flask(__name__)

"""
from google import genai

client = genai.Client(api_key="AIzaSyAiI-jt059i4mH4UTI7rkV4jhJF01kSthg")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents=f"Just return calories of {highest_label} as a number"
)
print(int(response.text))
"""

@app.route("/")
def index():
    return render_template('index.html')


#type in console -> python -m flask run
#use link in url -> http://127.0.0.1:5000/