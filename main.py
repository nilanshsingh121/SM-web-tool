from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import datetime
import math
from werkzeug.utils import secure_filename

# Safe import for PyPDF2
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

app = Flask(__name__)

# Better secret key handling
app.secret_key = os.environ.get('SECRET_KEY', 'studybuddy_secret_key_2026')

# Upload folder setup
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Mock Users
USERS = {
    'admin': 'password',
    'student': '123456'
}

# Translations (fixed encoding)
TRANSLATIONS = {
    'en': {
        'title': 'Study Buddy',
        'welcome': "Hey Friend! Let's Study",
        'planner': 'Study Planner',
        'analyzer': 'Resource Analyzer',
        'logout': 'Logout',
        'login': 'Login'
    },
    'hi': {
        'title': 'स्टडी बडी',
        'welcome': "चलो पढ़ाई शुरू करें!",
        'planner': 'स्टडी प्लानर',
        'analyzer': 'रिसोर्स एनालाइज़र',
        'logout': 'लॉगआउट',
        'login': 'लॉगिन'
    }
}

def get_locale():
    return session.get('lang', 'hi')


@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    lang = get_locale()
    return render_template('index.html', lang=lang, translations=TRANSLATIONS.get(lang, TRANSLATIONS['en']))


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        lang = request.form.get('lang', 'hi')

        if username in USERS and USERS[username] == password:
            session['username'] = username
            session['lang'] = lang
            return redirect(url_for('index'))

        return "Invalid credentials! Please try again."

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))


@app.route('/set_lang/<lang>')
def set_lang(lang):
    if lang in ['en', 'hi']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))


# Study Planner
@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data received'}), 400

        subjects_str = data.get('subjects')
        exam_date_str = data.get('exam_date')

        if not subjects_str or not exam_date_str:
            return jsonify({'error': 'Subjects and exam date are required.'}), 400

        subjects = [s.strip() for s in subjects_str.split(',') if s.strip()]
        if not subjects:
            return jsonify({'error': 'Please enter at least one subject.'}), 400

        exam_date = datetime.datetime.strptime(exam_date_str, '%Y-%m-%d').date()
        today = datetime.date.today()
        days_remaining = (exam_date - today).days

        if days_remaining < 1:
            return jsonify({'error': 'Please select a future date.'}), 400

        revision_days = max(1, math.ceil(days_remaining * 0.2))
        study_days = days_remaining - revision_days

        if study_days < len(subjects):
            return jsonify({'error': 'Not enough days. Reduce subjects or choose later date.'}), 400

        plan = {}
        day = 1
        idx = 0

        while idx < len(subjects) and day <= study_days:
            today_sub = [subjects[idx]]
            idx += 1

            if idx < len(subjects):
                today_sub.append(subjects[idx])
                idx += 1

            plan[f'Day {day}'] = " + ".join(today_sub)
            day += 1

        for i in range(study_days - (day - 1)):
            plan[f'Day {day + i}'] = f"Review: {subjects[i % len(subjects)]}"

        for i in range(revision_days):
            plan[f'Day {study_days + i + 1}'] = 'Revision'

        return jsonify({'plan': plan})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# PDF Upload
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF uploaded'}), 400

        file = request.files['pdf']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        text = ""

        if PyPDF2:
            try:
                reader = PyPDF2.PdfReader(filepath)
                for page in reader.pages:
                    text += page.extract_text() or ""
            except Exception:
                text = "Could not extract text from PDF."
        else:
            text = "PyPDF2 not installed."

        return jsonify({
            'summary': f"Summary of {filename}:\n\n{text[:800]}...",
            'flashcards': [
                {"q": "What is the main topic?", "a": "This PDF covers important concepts."},
                {"q": "Key takeaway?", "a": "Focus on definitions and examples."}
            ],
            'notes': "• Important definitions\n• Key formulas\n• Practice tips\n• Avoid mistakes",
            'filename': filename
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Video Processing
@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        data = request.get_json()
        url = data.get('url', '') if data else ''

        return jsonify({
            'summary': f"Video Summary from: {url}",
            'flashcards': [
                {"q": "What does the video teach?", "a": "Core concepts"},
                {"q": "Most important point?", "a": "Focus on examples"}
            ],
            'notes': "• Introduction\n• Explanation\n• Examples\n• Revision tips",
            'url': url
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
