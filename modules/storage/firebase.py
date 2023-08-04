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
    {"databaseURL": os.environ["DATABASE_URL"]},
)

# get the root reference
root = db.reference()


class FirebaseStorage:
    def __init__(self, path: str = ""):
        self.path = path
        self.ref = root.child(path) if path else root

    def __getitem__(self, key) -> any:
        return self.ref.child(key).get() or None

    def __setitem__(self, key, value) -> None:
        self.ref.child(key).set(value)

    def set(self, value) -> None:
        self.ref.set(value)

    @property
    def value(self, empty=None) -> any:
        return self.ref.get() or empty

    def update(self, value) -> None:
        self.ref.update(value)

    def delete(self) -> None:
        self.ref.delete()

    def push(self, value) -> None:
        self.ref.push(value)

    # allow sub references, create new FirebaseStorage object
    def child(self, path: str) -> "FirebaseStorage":
        return FirebaseStorage(f"{self.path}{'/' if self.path else ''}{path}")


# example usage of class
"""
storage = FirebaseStorage()

storage["key"] = "value"



"""


def resetusage():
    print("Resetting usage...")
    storage = FirebaseStorage()
    historic = storage.child("historic")
    current_global_usage = storage.child("usage").child("global").value
    current_user_usage = storage.child("usage").child("user").value

    storage.child("historic")["global"] = (
        storage.child("historic")["global"] or 0
    ) + current_global_usage

    for user in current_user_usage:
        historic.child("user").child(user).set(
            (historic.child("user").child(user).value or 0) + current_user_usage[user]
        )

    storage.child("usage").set({"global": 0, "user": {}})
