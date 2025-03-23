import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore

from config import CHILD_COLLECTION_NAME, CONV_COLLECTION_NAME, GCP_KEY, PROJECT_ID
from info.store_schema import Child
from info.store_schema import Conversation

cred = credentials.Certificate(GCP_KEY)
firebase_admin.initialize_app(cred)

db = firestore.Client(project = PROJECT_ID) 

def create_child_entry(child: Child):
    ref = db.collection(CHILD_COLLECTION_NAME).add(child.to_dict())
    print("Child created successfully with refID: ", ref[1].id)
    return ref[1].id


def update_child_entry(child_id: str, child: Child):
    """Update an existing child entry in Firestore."""
    ref = db.collection(CHILD_COLLECTION_NAME).document(child_id)
    # Check if the document exists
    if ref.get().exists:
        ref.update(child.to_dict())
        return (f"Child with ID: {child_id} updated successfully.")

    return (f"Child {child_id} does not exist or did not update.")

def get_child_entry(child_id: str):
    ref = db.collection(CHILD_COLLECTION_NAME).document(child_id)
    # Check if the document exists
    if ref.get().exists:
        print(f"Child {child_id} exists.")
        child_dict = ref.get().to_dict()
        if 'password' in child_dict:
            del child_dict['password']
        return child_dict

    print(f"Child {child_id} does not exist.")
    return None

def check_username_password(username: str, password: str):
    # Query the "Children" collection where "username" equals the provided username.
    query = db.collection(CHILD_COLLECTION_NAME).where("username", "==", username)
    docs = query.stream()
    for doc in docs:
        # Return the first matching document as a dictionary.
        child_dict = doc.to_dict()
        if password.strip() == child_dict.get('password',''):
            return ("Logged in Successfully", doc.id)
    
    return ("Invalid Credentials", None)

def add_new_conversation(child_id:str, conversation: Conversation):
    doc_ref = db.collection(f"{CHILD_COLLECTION_NAME}/{child_id}/{CONV_COLLECTION_NAME}")
    ref = doc_ref.add( conversation.to_dict() )
    # TODO: Add all the required details to make the function work 
    print("Conversation created successfully with refID: ", ref[1].id)

