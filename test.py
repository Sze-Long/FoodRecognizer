import smtplib
from email.message import EmailMessage
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

USE_KEY = os.getenv("USE_KEY")
PAS_KEY = os.getenv("PAS_KEY")

# Email content
msg = EmailMessage()
msg['Subject'] = 'Hello from Python'
msg['From'] = USE_KEY
msg['To'] = USE_KEY
msg.set_content('This is a test email sent from Python.')

# Gmail SMTP settings
smtp_server = 'smtp.gmail.com'
smtp_port = 587

# Send email
try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(USE_KEY, PAS_KEY)  # Use app-specific password
        server.send_message(msg)
        print('Email sent successfully!')
except Exception as e:
    print(f'Error sending email: {e}')
