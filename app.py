from flask import Flask, request, jsonify, render_template, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from functools import wraps
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key")  # Set in .env

# MongoDB connection URI from .env
MONGO_URI = os.getenv("MONGO_URI", "your-mongodb-uri")
client = MongoClient(MONGO_URI)
db = client['notesdb']
notes_collection = db['notes']
users_collection = db['users']

# Decorator to require login for protected routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return render_template('login.html')
        return f(*args, **kwargs)
    return decorated_function

# Home route → show login page
@app.route('/')
def home():
    return render_template('login.html')

# Registration route
@app.route('/register', methods=['POST'])
def register():
    data = request.form
    first = data.get('firstName')
    last = data.get('lastName')
    email = data.get('email')
    password = data.get('password')
    confirm = data.get('confirmPassword')

    if not all([first, last, email, password, confirm]):
        return "Missing fields", 400
    if password != confirm:
        return "Passwords do not match", 400
    if users_collection.find_one({"email": email}):
        return "Email already registered", 400

    hashed = generate_password_hash(password)
    users_collection.insert_one({
        "firstName": first,
        "lastName": last,
        "email": email,
        "password": hashed
    })
    return render_template('login.html')

# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.form
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({"email": email})
    if user and check_password_hash(user['password'], password):
        session['user_id'] = str(user['_id'])
        return redirect('/notes')
    else:
        return "Invalid credentials", 401

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return render_template('login.html')

# Notes page - protected route
@app.route('/notes')
@login_required
def notes():
    return render_template('notes.html')

# Get notes
@app.route('/api/notes', methods=['GET'])
@login_required
def get_notes():
    user_id = session['user_id']
    user_notes = list(notes_collection.find({"user_id": user_id}))
    for note in user_notes:
        note['_id'] = str(note['_id'])  # Convert ObjectId to string
    return jsonify(user_notes), 200

# Add new note
@app.route('/api/notes', methods=['POST'])
@login_required
def add_note():
    user_id = session['user_id']
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"message": "Missing title or content"}), 400

    note = {
        "user_id": user_id,
        "title": title,
        "content": content
    }
    result = notes_collection.insert_one(note)
    note['_id'] = str(result.inserted_id)
    return jsonify(note), 201

# Delete note
@app.route('/api/notes/<note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    user_id = session['user_id']
    result = notes_collection.delete_one({"_id": ObjectId(note_id), "user_id": user_id})
    if result.deleted_count == 0:
        return jsonify({"message": "Note not found"}), 404
    return jsonify({"message": "Note deleted"}), 200

# Run the app
if __name__ == "_main_":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)