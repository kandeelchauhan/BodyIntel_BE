from flask import Flask, request, jsonify
import os
import openai
import json
from colorama import Fore, Back, Style
import Main
app = Flask(__name__)

# Define your API endpoint
@app.route("/call-chatbot", methods=["POST"])
def generate_text():
    # Get the request data from your frontend app
    answer = request.json.get("answer")
    # Return the response data as JSON
    return jsonify(response.choices[0].text)

# Start your Flask app
if __name__ == "__main__":
    app.run(debug=True)