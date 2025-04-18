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
positive_prompt = "What are the activities that have a positive impact on the user (which is not me) that you understand in the chat so far? Limit to 40 words"
stress_prompt = "Based on the chat history what is the level of stress of the user? Answer in 1 word ONLY out of the 4 words - Stressless / Low / Moderate / High. Only use title case. "
stress_reason_prompt = "Based on the chat history can you answer in 30 words why the user is stressed and if they do not seem stressed just reply with \"User not stressed\". "
stress_summary_prompt = "Can you state a crisp reason for stress from the following messages and write \"No Stress\" if there is none."


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
        # make API call to extract stress level
        stress = call_gemini(stress_prompt, chat_history, None)
        if len(stress) > 0:
            stress = stress.strip()
        # make API call to find possible reason for stress
        stress_reason = call_gemini(stress_reason_prompt, chat_history, None)
        # Checking which emotion is the most dominant in the conversation 
        dominant_emotion = most_frequent(emotion)
        if isinstance(dominant_emotion, str):
            dominant_emotion = dominant_emotion.title()
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
        stress = stress,
        stressSummary=stress_reason
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
            conv_sum.stress = stress
            conv_sum.stressSummary = call_gemini( stress_summary_prompt + conv_sum.stressSummary + stress_reason, [], None)
            conv_sum.interests_summary = interests
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
                        stress=stress,
                        stressSummary=stress_reason,
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

def fetch_all_conversations(child_id: str):
    try:
        collection_ref = db.collection(
            f"{CHILD_COLLECTION_NAME}/{child_id}/{CONV_COLLECTION_NAME}"
        )

        # Sort by date field in descending order (latest first)
        docs = collection_ref.order_by("date", direction=firestore.Query.DESCENDING).order_by("time", direction=firestore.Query.DESCENDING).stream()

        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print("Error fetching conversations:", e)
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
    task_doc_ref = db.collection(
            CHILD_COLLECTION_NAME+"/"+
            child_id+"/"+ 
            HABITUAL_TASKS_COLLECTION_NAME
            ).document(task_id)
    try:
        task_dict = ht.to_dict()
        task_doc_ref.update(task_dict)
    except Exception as e:
        return (False, str(e))

    # If this is task being updated as done, add the points
    if 'is_done' in task_dict and task_dict['is_done']:

        # Fetch how many points
        old_points = task_doc_ref.get().to_dict()['points']

        # Get how many points it had previously
        try:
            ret = get_child_entry(child_id=child_id)
            if ret:
                child_dict, _ = ret
                if 'points' in child_dict:
                    new_points = child_dict['points'] 
                    update_child_entry(child_id, Child(points=old_points+new_points))

        except Exception as e:
            return (False, str(e))

    return (True, "Successfully updated task")
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


