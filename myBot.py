import os
import openai
from colorama import Fore, Back, Style
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)

CORS(app) 

openai.api_key = "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"

# Load the JSON file
with open('BotParams.json', 'r') as f:
    data = json.load(f)

keys = {}
for key in data.keys():
    keys[key] = data[key]

INSTRUCTIONS = f"""As a healthcare professional, you want to ensure that you stay up-to-date with the latest scientific research on health, nutrition, exercise, and sports performance. Write a research question related to one of these topics, and use peer-reviewed journal articles to answer the question. It is mandatory to provide the references and URLs for any articles you use, and be sure to highlight any opposing views that exist in the literature. provide information on general macronutrient recommendations for different populations based on peer-reviewed research. If user asks vague questions, ask him questions to share a more personalised reply"""

TEMPERATURE = 0.7
MAX_TOKENS = 1200
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0
# limits how many questions we include in the prompt
MAX_CONTEXT_QUESTIONS = 10


def get_response(instructions, previous_questions_and_answers, new_question):
    """Get a response from ChatCompletion

    Args:
        instructions: The instructions for the chat bot - this determines how it will behave
        previous_questions_and_answers: Chat history
        new_question: The new question to ask the bot

    Returns:
        The response text
    """
    # build the messages
    messages = [
        { "role": "system", "content": instructions },
    ]
    # add the previous questions and answers
    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({ "role": "user", "content": question })
        messages.append({ "role": "assistant", "content": answer })
    # add the new question
    messages.append({ "role": "user", "content": new_question })
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=1,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
    )
    return completion.choices[0].message.content


def get_moderation(question):
    """
    Check the question is safe to ask the model

    Parameters:
        question (str): The question to check

    Returns a list of errors if the question is not safe, otherwise returns None
    """

    errors = {
        "hate": "Content that expresses, incites, or promotes hate based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
        "hate/threatening": "Hateful content that also includes violence or serious harm towards the targeted group.",
        "self-harm": "Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
        "sexual": "Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness).",
        "sexual/minors": "Sexual content that includes an individual who is under 18 years old.",
        "violence": "Content that promotes or glorifies violence or celebrates the suffering or humiliation of others.",
        "violence/graphic": "Violent content that depicts death, violence, or serious physical injury in extreme graphic detail.",
    }
    response = openai.Moderation.create(input=question)
    if response.results[0].flagged:
        # get the categories that are flagged and generate a message
        result = [
            error
            for category, error in errors.items()
            if response.results[0].categories[category]
        ]
        return result
    return None

# Define your API endpoint
previous_questions_and_answers = []
@app.route("/body-intel-search-box", methods=["POST"])
def generate_text():
    # keep track of previous questions and answers
    while True:
        # ask the user for their question
        new_question = request.json.get("message")
        # check the question is safe
        errors = get_moderation(new_question)
        if errors:
            print(
                Fore.RED
                + Style.BRIGHT
                + "Sorry, you're question didn't pass the moderation check:"
            )
            for error in errors:
                print(error)
            print(Style.RESET_ALL)
            continue
        print(previous_questions_and_answers)
        print(new_question)
        response = get_response(INSTRUCTIONS, previous_questions_and_answers, new_question)

        previous_questions_and_answers.append((new_question, response))
        return jsonify(response)

# Start your Flask appss
if __name__ == "__main__":
    app.run(debug=True, port=3001)