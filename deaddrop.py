import os
import pickle
import random
import requests

from flask import Flask, render_template, request

# Configuration placholders
SECRET_KEY = "PLACEHOLDER"
SKYBIOMETRY_API_KEY = "PLACEHOLDER"
SKYBIOMETRY_API_SECRET = "PLACEHOLDER"

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('DEADDROP_SETTINGS')
app.secret_key = app.config["SECRET_KEY"]


class Profile:
    """ 
    Profile holds an agent's facial attributes as well as
    the secret message and the generated code to retrieve it.
    """
    def __init__(self):
        self.gender = None
        self.glasses = None
        self.smile = None
        self.lips = None
        self.eyes = None
        self.mood = None
        self.message = None
        self.code = random.getrandbits(20)


@app.route("/deaddrop/welcome")
def home():
    """Entry point for incoming phone calls."""
    say = say_text("Welcome, agent.")
    say += say_text("Please enter the code followed by the pound sign to hear the secret message.")
    say += say_text("Stay on the line to record a new secret message for another agent.")

    action = '<Gather action="/deaddrop/code" method="GET">{}</Gather>'.format(say)
    action += say_text("You are about to record a new secret message.")
    action += say_text("First, identify the agent for whom it is intended.")

    next = "/deaddrop/choose/gender"
    return get_response(action, next)

@app.route("/deaddrop/code")
def code():
    """Checks entered code for validity and play the message."""
    code = request.args.get("Digits")
    next = "/deaddrop/code"
    action = None

    if code is None:
        say = say_text("Please try again. Enter the code followed by the pound sign.")
        action = '<Gather action="{next}" method="GET">{say}</Gather>'
        action = action.format(next=next, say=say)
    else:
        profile = load_profile()
        if str(profile.code) == request.args.get("Digits"):
            action = '<Play>{}</Play><Hangup />'.format(profile.message)
            next = None

    return get_response(action, next)

@app.route("/deaddrop/choose/<attribute>")
def choose(attribute):
    """Presents the caller with the options to choose facial attributes."""

    # The entire interaction script is stored in get_attributes()
    attributes = get_attributes()
    action = None
    next = None

    # Find the attribute we're currently addressing
    for i, current_attr in enumerate(attributes):
        if current_attr["type"] == attribute:
            break;

    selection = request.args.get("Digits")
    if selection in current_attr["options"]:
        # A valid option has been chosen. Save to profile.
        profile = load_profile()
        setattr(profile, attribute, current_attr["options"][selection])
        save_profile(profile)

        if i < len(attributes) - 1:
            # Move to the next attribute
            next = "/deaddrop/choose/" + attributes[i + 1]["type"]
        else:
            # No more attributes in the interaction script, record the message
            next = "/deaddrop/record"
            say = say_text("Thank you, agent. Please record the secret message now.")
            action = '{say}<Record action="{next}" method="GET" maxLength="300" />'
            action = action.format(next=next, say=say)
    else:
        # Invalid or no option has been selected
        if i == 0:
            # Just landed on the first attribute, wipe the profile to start
            save_profile(Profile())

        # Read all of the options for this attribute
        next = "/deaddrop/choose/" + attribute
        say = ''.join(map(say_text, current_attr["prompts"]))
        action = '<Gather action="{next}" method="GET" numDigits="1">{say}</Gather>'
        action = action.format(next=next, say=say)

    return get_response(action, next)

@app.route("/deaddrop/record")
def record():
    """Once the message is recorded, save it and hang up."""
    profile = load_profile()
    profile.message = request.args.get("RecordingUrl")
    save_profile(profile)

    action = '<Hangup />'.format(profile.message)
    return get_response(action, None)

@app.route("/deaddrop", methods=["GET", "POST"])
def access():
    """Entry point for the code retrieval web application."""
    if request.method == "GET":
        return render_template("access.html")

    # Once the form is POSTed, send the image URL
    # to the SkyBiometry API for facial recognition.
    url = "http://api.skybiometry.com/fc/faces/detect.json"
    payload = {"api_key": app.config["SKYBIOMETRY_API_KEY"],
               "api_secret": app.config["SKYBIOMETRY_API_SECRET"],
               "attributes": "all",
               "urls": request.form["url"]}

    response = requests.get(url, params=payload)
    data = response.json()

    message = "Please provide a valid image URL with a single face."
    current_profile = None

    if (data["status"] == "success" and
            len(data["photos"]) == 1 and
            len(data["photos"][0]["tags"]) == 1):
        # A valid image of one face has been recognized
        attributes = data["photos"][0]["tags"][0]["attributes"]

        # Map SkyBiometry data to our profile object
        current_profile = Profile()
        if "gender" in attributes:
            current_profile.gender = attributes["gender"]["value"]
        if "glasses" in attributes:
            current_profile.glasses = attributes["glasses"]["value"]
        if "smiling" in attributes:
            current_profile.smile = attributes["smiling"]["value"]
        if "lips" in attributes:
            current_profile.lips = attributes["lips"]["value"]
        if "eyes" in attributes:
            current_profile.eyes = attributes["eyes"]["value"]
        if "mood" in attributes:
            current_profile.mood = attributes["mood"]["value"]

        try:
            # Compare the recognized profile to the saved one
            saved_profile = load_profile()
            if (current_profile.gender == saved_profile.gender and
                    current_profile.glasses == saved_profile.glasses and
                    current_profile.smile == saved_profile.smile and
                    current_profile.lips == saved_profile.lips and
                    current_profile.eyes == saved_profile.eyes and
                    current_profile.mood == saved_profile.mood):
                # Agent recognized, display the random code to retrieve the message
                message = "Success! The secret code is " + str(saved_profile.code)
            elif saved_profile.message is None:
                message = "No messages have been recorded. Please try again later."
            else:
                message = "Your face does not match the expected profile."
        except:
            message = "No messages have been recorded. Please try again later."
    
    return render_template("access.html", form=request.form, profile=current_profile, message=message)

def get_profile_path():
    """Stores profile in a local file. NOT THREAD-SAFE!"""
    return os.path.join(os.path.dirname(__file__), "files/profile.dat")

def load_profile():
    """Helper method for reading a profile out of a file."""
    return pickle.load(open(get_profile_path(), "rb"))

def save_profile(profile):
    """Helper method for saving a profile to a file."""
    pickle.dump(profile, open(get_profile_path(), "wb"))

def say_text(text):
    """Defines the voice and accent for the text-to-speech synthesizer."""
    return '<Say voice="woman" language="en-gb">{}</Say><Pause />'.format(text)

def get_response(action, next):
    """Returns a fairly standard Twilio response template."""
    response = """<?xml version="1.0" encoding="UTF-8"?>
                  <Response>
                      {action}<Redirect method="GET">{next}</Redirect>
                  </Response>"""
    return response.format(action=action, next=next)

def get_attributes():
    """Defines the phone interaction script."""
    return [{"type": "gender",
             "options": {"1": "male",
                         "2": "female"},
             "prompts": ["If the agent is male, press 1.",
                         "If the agent is female, press 2."]},
            {"type": "glasses",
             "options": {"1": "true", 
                         "2": "false"},
             "prompts": ["If the agent will be wearing glasses, press 1.",
                         "If the agent will not be wearing glasses, press 2."]},
            {"type": "smile",
             "options": {"1": "true",
                         "2": "false"},
             "prompts": ["If the agent will be smiling, press 1.",
                         "If the agent will not be smiling, press 2."]}, 
            {"type": "lips",
             "options": {"1": "sealed",
                         "2": "parted"},
             "prompts": ["If the agent's lips will be sealed, press 1.",
                         "If the agent's lips will be parted, press 2."]},
            {"type": "eyes",
             "options": {"1": "open",
                         "2": "closed"},
             "prompts": ["If the agent's eyes will be open, press 1.",
                         "If the agent's eyes will be closed, press 2."]},
            {"type": "mood",
             "options": {"1": "neutral",
                         "2": "happy",
                         "3": "sad",
                         "4": "angry",
                         "5": "surprised",
                         "6": "disgusted",
                         "7": "scared"},
             "prompts": ["If the agent will look neutral, press 1.",
                         "If the agent will look happy, press 2.",
                         "If the agent will look sad, press 3.",
                         "If the agent will look angry, press 4.",
                         "If the agent will look surprised, press 5.",
                         "If the agent will look disgusted, press 6.",
                         "If the agent will look scared, press 7."]}]

if __name__ == "__main__":
    app.run()
