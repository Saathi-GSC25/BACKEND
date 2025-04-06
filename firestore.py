from datetime import datetime, timezone
from typing import Dict, List, Optional
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore

from collections import Counter
from child_api.helper import call_gemini
from config import CHILD_COLLECTION_NAME, CONV_COLLECTION_NAME, GCP_KEY, HABITUAL_TASKS_COLLECTION_NAME, LEARNING_TASKS_COLLECTION_NAME, PROJECT_ID
from firestore_schema import Child, ConversationSummary, HabitualTask, LearningTask
from firestore_schema import Conversation

cred = credentials.Certificate(GCP_KEY)
firebase_admin.initialize_app(cred)

db = firestore.Client(project = PROJECT_ID) 

# -----------------------------------------------------------------
# Child Helper Functions
# -----------------------------------------------------------------

def create_child_entry(child: Child):
    try:
        ref = db.collection(CHILD_COLLECTION_NAME).add(child.to_dict())
        if not ref or not ref[1]:  
            raise ValueError("Firestore did not return a valid reference")
        print("Child created successfully with refID: ", ref[1].id)
        return ( True, ref[1].id )
    except Exception as e:
        return ( False, str(e) )

def update_child_entry(child_id: str, child: Child):
    """Update an existing child entry in Firestore."""
    try:
        ref = db.collection(CHILD_COLLECTION_NAME).document(child_id)
        # Check if the document exists
        if ref.get().exists:
            ref.update(child.to_dict())
            return (f"Child with ID: {child_id} updated successfully.")

        return (f"Child {child_id} does not exist")
    except Exception as e:
        return (f"Exception occured while updating: {str(e)}")

def get_child_entry(child_id:Optional[str] = None, 
                    parent_uuid:Optional[str] = None):
    try:
        if parent_uuid:
            query = db.collection(CHILD_COLLECTION_NAME).where("parent_uuid","==",parent_uuid)
            docs = query.stream()
            for doc in docs:
                # Return the first matching document as a dictionary.
                child_dict = doc.to_dict()
                return (child_dict, doc.id)
            
            return None

        elif child_id:
            ref = db.collection(CHILD_COLLECTION_NAME).document(child_id)
            # Check if the document exists
            if ref.get().exists:
                print(f"Child {child_id} exists.")
                child_dict = ref.get().to_dict()
                if 'password' in child_dict:
                    del child_dict['password']
                return ( child_dict, child_id )

            print(f"Child {child_id} does not exist.")
            return None
    except Exception as e:
        return (f"Exception occured while fetching child details: {str(e)}")

def check_username_password(username: str, password: str):
    try:
        # Query the "Children" collection where "username" equals the provided username.
        query = db.collection(CHILD_COLLECTION_NAME).where("username", "==", username)
        docs = query.stream()
        for doc in docs:
            # Return the first matching document as a dictionary.
            child_dict = doc.to_dict()
            if password.strip() == child_dict.get('password',''):
                return ("Logged in Successfully", doc.id)
        
        return ("Invalid Credentials", None)
    except Exception as e:
        return (f"Exception occured while logging in: {str(e)}", None)

def check_username_exists(username: str):
    try:
        query = db.collection(CHILD_COLLECTION_NAME).where("username", "==", username)
        docs = query.stream()
        for _ in docs:
            return True
        return False
    except Exception as e:
        print(f"Exception occured while checking username: {str(e)}")
        return True
    
# -----------------------------------------------------------------
# Conversation Helper Functions
# -----------------------------------------------------------------

summarize_prompt = "Make a summary as short as possible with maximum 100 words of the chat history. Mention only important points."
positive_prompt = "What are the activities that have a positive impact on the user (which is not me) that you understand in the chat so far? Limit to 80 words"


def most_frequent(lst):
    return Counter(lst).most_common(1)[0][0]

def add_new_conversation(child_id:str, 
                         chat_history: List, 
                         emotion:List[str],
                         duration: int
                         ):
    try:
        # make API call to summarize chat_history
        summary = call_gemini(summarize_prompt, chat_history, None)
        # make API call to extract positive impacts (interests)
        interests = call_gemini(positive_prompt, chat_history, None)
        # Current date and time according to server
        date_time = datetime.now(timezone.utc)
        # Checking which emotion is the most dominant in the conversation 
        dominant_emotion = most_frequent(emotion)
    except Exception as e:
        return (False, str(e))

    # Stress is still left 
    conversation = Conversation(
        date = datetime.today().date(), 
        time = datetime.today().time(),
        interests=interests, 
        duration = duration,
        summary = summary,
        emotion = dominant_emotion,
        stress = "lorem",
        stressSummary="ipsum"
        )


    doc_ref = db.collection(f"{CHILD_COLLECTION_NAME}/{child_id}/{CONV_COLLECTION_NAME}")
    ref = doc_ref.add( conversation.to_dict() )

    print("Conversation created successfully with refID: ", ref[1].id)

    # Updating the child summary
    doc_ref = db.collection(CHILD_COLLECTION_NAME).document(child_id)
    doc = doc_ref.get()
    if doc_ref.get().exists:
        chat_summary = doc.to_dict().get("chat_summary") 
        if chat_summary:
            conv_sum = ConversationSummary.from_dict(chat_summary)
            
            # Updating the object
            if conv_sum.conversations:
                conv_sum.conversations = conv_sum.conversations + 1
            conv_sum.last_updated = datetime.now()
            conv_sum.stress = "moderate"
            conv_sum.stressSummary = "loremIpsum"
            conv_sum.interests_summary = "Summary of interests"
            conv_sum.emotion = dominant_emotion
            if conv_sum.total_duration:
                conv_sum.total_duration = conv_sum.total_duration + duration

            # Storing it back
            try:
                doc_ref.update({"chat_summary":conv_sum.to_dict()})
                return (True, "successfully updated")
            except Exception as e:
                return (False, str(e))

        else:
            print("Chat summary does not exist.. Creating one for the first time")
            conv_sum = ConversationSummary(
                        last_updated = datetime.now(),
                        emotion = dominant_emotion, 
                        conversations=1, 
                        stress="lorem",
                        stressSummary="ipsum",
                        total_duration=duration,
                        interests_summary=interests
                    )
            # Storing it back
            try:
                doc_ref.update({"chat_summary":conv_sum.to_dict()})
                return (True, "successfully updated")
            except Exception as e:
                return (False, str(e))

    else:
        return (False, "Failed because child_id invalid")

def fetch_chat_summary(child_id:str):
    try:
        ref = db.collection(CHILD_COLLECTION_NAME).document(child_id)
        # Check if the document exists
        if ref.get().exists:
            print(f"Child {child_id} exists.")
            child_dict = ref.get().to_dict()
            if 'chat_summary' not in child_dict:
                return None
            return child_dict['chat_summary']
    except Exception as e:
        return None

def fetch_all_conversations(child_id:str):
    try:
        collection_ref = db.collection(
                CHILD_COLLECTION_NAME+"/"+child_id+"/"+CONV_COLLECTION_NAME)

        # Fetch all documents
        docs = collection_ref.stream()
        list_of_conv = []
        for doc in docs:
            list_of_conv += [doc.to_dict()]

        return list_of_conv
    except:
        return []


# -----------------------------------------------------------------
# Habitual Tasks Helper Functions
# -----------------------------------------------------------------


def add_habitual_task( child_id:str, ht: HabitualTask):
    try:
        ref = db.collection(
                CHILD_COLLECTION_NAME+"/"+
                child_id+"/"+
                HABITUAL_TASKS_COLLECTION_NAME
            ).add(ht.to_dict())

        if not ref or not ref[1]:  
            raise ValueError("Firestore did not return a valid reference")
        print("Habitual Task created successfully with refID: ", ref[1].id)
        return ( True, ref[1].id )
    except Exception as e:
        return ( False, str(e) )

def list_all_habitual_tasks(child_id:str):
    collection_ref = db.collection(
            CHILD_COLLECTION_NAME+"/"+child_id+"/"+ HABITUAL_TASKS_COLLECTION_NAME)

    # Fetch all documents
    docs = collection_ref.stream()
    list_of_tasks = []
    for doc in docs:
        doc_dict = doc.to_dict()
        doc_dict['task_id'] = doc.id
        list_of_tasks += [doc_dict]

    return list_of_tasks

def update_habitual_task(child_id:str, task_id:str, ht:HabitualTask):
    doc_ref = db.collection(
            CHILD_COLLECTION_NAME+"/"+
            child_id+"/"+ 
            HABITUAL_TASKS_COLLECTION_NAME
            ).document(task_id)
    try:
        doc_ref.update(ht.to_dict())
        return (True, "Successfully updated task")
    except Exception as e:
        return (False, str(e))

def delete_habitual_task(child_id:str, task_id:str):
    doc_ref = db.collection(
            CHILD_COLLECTION_NAME+"/"+
            child_id+"/"+ 
            HABITUAL_TASKS_COLLECTION_NAME
            ).document(task_id)

    try:
        doc_ref.delete()
        return (True, "Successfully delete task")
    except Exception as e:
        return (False, str(e))


# -----------------------------------------------------------------
# Learning Tasks Helper Functions
# -----------------------------------------------------------------

def list_all_learning_tasks(child_id:str):
    collection_ref = db.collection(
            CHILD_COLLECTION_NAME+"/"+child_id+"/"+ LEARNING_TASKS_COLLECTION_NAME)

    # Fetch all documents
    docs = collection_ref.stream()
    list_of_tasks = []
    for doc in docs:
        doc_dict = doc.to_dict()
        doc_dict['task_id'] = doc.id
        list_of_tasks += [doc_dict]

    return list_of_tasks

def add_learning_task( child_id:str, lt: LearningTask):
    try:
        ref = db.collection(
                CHILD_COLLECTION_NAME+"/"+
                child_id+"/"+
                LEARNING_TASKS_COLLECTION_NAME
            ).add(lt.to_dict())

        if not ref or not ref[1]:  
            raise ValueError("Firestore did not return a valid reference")
        print("Learning Task created successfully with refID: ", ref[1].id)
        return ( True, ref[1].id )
    except Exception as e:
        return ( False, str(e) )

def update_learning_task(child_id:str, task_id:str, lt:LearningTask):
    doc_ref = db.collection(
            CHILD_COLLECTION_NAME+"/"+
            child_id+"/"+ 
            LEARNING_TASKS_COLLECTION_NAME
            ).document(task_id)
    try:
        doc_ref.update(lt.to_dict())
        return (True, "Successfully updated task")
    except Exception as e:
        return (False, str(e))

def delete_learning_task(child_id:str, task_id:str):
    doc_ref = db.collection(
            CHILD_COLLECTION_NAME+"/"+
            child_id+"/"+ 
            LEARNING_TASKS_COLLECTION_NAME
            ).document(task_id)

    try:
        doc_ref.delete()
        return (True, "Successfully deleted task")
    except Exception as e:
        return (False, str(e))


