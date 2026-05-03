from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import datetime
import math
from werkzeug.utils import secure_filename

# Optional PDF import (safe)
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

app = Flask(__name__)

# Better secret key handling
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret_key")

# Upload folder setup
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Mock Users
USERS = {
    "admin": "password",
    "student": "123456"
}

# Translations (fixed encoding)
TRANSLATIONS = {
    "en": {
        "title": "Study Buddy",
        "welcome": "Hey Friend! Let's Study",
        "planner": "Study Planner",
        "analyzer": "Resource Analyzer",
        "logout": "Logout",
        "login": "Login"
    },
    "hi": {
        "title": "स्टडी बडी",
        "welcome": "चलो पढ़ाई शुरू करें!",
        "planner": "स्टडी प्लानर",
        "analyzer": "रिसोर्स एनालाइज़र",
        "logout": "लॉगआउट",
        "login": "लॉगिन"
    }
}

def get_locale():
    return session.get("lang", "hi")
