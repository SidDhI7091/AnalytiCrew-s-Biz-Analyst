import firebase_admin
from firebase_admin import credentials, firestore , auth
import os

# Dynamically resolve the correct path to the credentials file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This is the "firebase/" directory
key_path = os.path.join(BASE_DIR, "firebase-admin-key.json")
# Initialize Firebase only once
if not firebase_admin._apps:
    # cred = credentials.Certificate("firebase/firebase-admin-key.json")
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)

# Firestore DB
db = firestore.client()

def store_parsed_content(filename, filetype, content):
    """Stores parsed document into Firestore"""
    doc_ref = db.collection("parsed_docs").document()
    doc_ref.set({
        "filename": filename,
        "type": filetype,
        "content": content,
        "status": "parsed",
        "timestamp": firestore.SERVER_TIMESTAMP
    })

