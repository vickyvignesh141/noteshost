from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import os

app = Flask(_name_)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client['notesdb']
notes_collection = db['notes']

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Notes page
@app.route('/notes')
def notes():
    return render_template('notes.html')

# Add note API
@app.route('/add_note', methods=['POST'])
def add_note():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({"message": "Missing title or content"}), 400

    note = {
        "title": title,
        "content": content
    }
    notes_collection.insert_one(note)
    return jsonify({"message": "Note added successfully!"}), 200

if _name_ == "_main_":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)