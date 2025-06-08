from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key_here")  # session secret key

# MongoDB configuration
MONGO_URI = os.environ.get("MONGO_URI", "your-mongodb-uri")
client = MongoClient(MONGO_URI)
db = client['notesdb']
users_collection = db['users']
notes_collection = db['notes']

# Home route
@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('notes'))
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if users_collection.find_one({'username': username}):
            return "User already exists", 400

        hashed_password = generate_password_hash(password)
        users_collection.insert_one({'username': username, 'password': hashed_password})
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect(url_for('notes'))
        else:
            return "Invalid username or password", 401

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Notes page (protected)
@app.route('/notes')
def notes():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('notes.html')

# Add note API (protected)
@app.route('/add_note', methods=['POST'])
def add_note():
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"message": "Missing title or content"}), 400

    note = {
        "title": title,
        "content": content,
        "username": session['user']  # Link note to user
    }
    notes_collection.insert_one(note)
    return jsonify({"message": "Note added successfully!"}), 200

# Run the Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)