import os
from flask import Flask

app = Flask(_name_)

@app.route("/")
def home():
    return "Hello, world!"

if _name_ == "_main_":
    port = int(os.environ.get("PORT", 5000))  # Get port from environment or default to 5000
    app.run(host="0.0.0.0", port=port)       # Bind to 0.0.0.0 to accept external connections