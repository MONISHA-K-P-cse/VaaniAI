import firebase_admin
from firebase_admin import credentials, firestore, messaging
import os
import logging

# Path to your Firebase service account key JSON file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", os.path.join(BASE_DIR, "serviceAccountKey.json"))

_db = None
_initialized = False

def init_firebase():
    global _db, _initialized
    if _initialized:
        return
    
    try:
        if os.path.exists(SERVICE_ACCOUNT_PATH):
            cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
            firebase_admin.initialize_app(cred)
            _db = firestore.client()
            _initialized = True
            print("Firebase Admin initialized successfully.")
        else:
            print(f"Firebase service account file not found at {SERVICE_ACCOUNT_PATH}. Skipping initialization.")
    except Exception as e:
        print(f"Failed to initialize Firebase Admin: {e}")

def sync_call_to_firestore(call_data: dict):
    if not _initialized:
        return
    try:
        doc_ref = _db.collection("calls").document(call_data["id"])
        doc_ref.set(call_data)
    except Exception as e:
        print(f"Error syncing call to Firestore: {e}")

def send_push_notification(title: str, body: str, token: str = None):
    if not _initialized:
        return
    
    # If no token is provided, we might send to a topic like 'all_rms'
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            topic='alerts' if not token else None,
            token=token if token else None
        )
        response = messaging.send(message)
        print('Successfully sent message:', response)
    except Exception as e:
        print(f"Error sending push notification: {e}")
