# Takes secret from .secrets/FIREBASE.json and sets it as an environment variable

import os
import json

# Get the path to the .secrets folder
secrets_path = os.path.join(os.path.dirname(__file__), ".secrets")

# Get the path to the FIREBASE.json file
firebase_path = os.path.join(secrets_path, "FIREBASE.json")

# Open the file and load the JSON
with open(firebase_path) as f:
    firebase_json = json.load(f)

# Set the environment variable
os.environ["FIREBASE"] = json.dumps(firebase_json)
print(f"Set FIREBASE environment variable: {os.environ['FIREBASE']}")

# To set the environment variable in the terminal, make sure to base64 encode the JSON
