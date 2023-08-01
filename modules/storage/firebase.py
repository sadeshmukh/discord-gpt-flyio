# Class to handle Firebase storage

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
import os
import base64


# initialize w/ cridentials
# credentials are in the FIREBASE environment variable as BASE64 encoded JSON

original = os.environ["FIREBASE"]
cert = base64.b64decode(original)


firebase_admin.initialize_app(
    credentials.Certificate(json.loads(cert)),
    {"databaseURL": "https://discord-gpt-1884c-default-rtdb.firebaseio.com/"},
)

# get the root reference
root = db.reference()


class FirebaseStorage:
    def __init__(self, path: str = ""):
        self.path = path
        self.ref = root.child(path) if path else root

    def __getitem__(self, key):
        return self.ref.child(key).get() or None

    def __setitem__(self, key, value):
        self.ref.child(key).set(value)

    def set(self, value):
        self.ref.set(value)

    @property
    def value(self, empty=None):
        return self.ref.get() or empty

    def update(self, value):
        self.ref.update(value)

    def delete(self):
        self.ref.delete()

    def push(self, value):
        self.ref.push(value)

    # allow sub references, create new FirebaseStorage object
    def child(self, path: str) -> "FirebaseStorage":
        return FirebaseStorage(f"{self.path}{'/' if self.path else ''}{path}")


# example usage of class
"""
storage = FirebaseStorage("dm_system_messages")

storage.set({"123456789": "Hello, world!"})



"""
