from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB Atlas connection URI (replace <username>, <password>, <cluster-url> with your details)
MONGO_URI = os.environ.get("MONGO_URI", "your-mongodb-atlas-uri-here")

client = MongoClient(MONGO_URI)
db = client['notesdb']
notes_collection = db['notes']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/notes')
def notes():
    return render_template('notes.html')

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)