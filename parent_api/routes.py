from flask import session
from flask.views import MethodView
from flask_smorest import Blueprint
from config import GEMINI_API_KEY
from firestore import check_username_exists, create_child_entry, delete_habitual_task, delete_learning_task, list_all_habitual_tasks, list_all_learning_tasks, update_child_entry, update_habitual_task, update_learning_task
from firestore_schema import Child
import google.generativeai as genai

from parent_api.schema import ChatSchema, ChildCreateSchema, ChildCredentialsUpdateSchma

parent_bp = Blueprint('Parent API', __name__, 
                    url_prefix='/parent', 
                    description="")

# Configure Google GenAI API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel( model_name="gemini-1.5-flash" )

# --------------------------------------------------------------------
# CHATBOT ROUTE
# --------------------------------------------------------------------

@parent_bp.route("/text_chat")
class ChatRoute(MethodView):
    # POST REQUEST 
    @parent_bp.response(status_code=201)
    @parent_bp.arguments(ChatSchema)
    def post(self, params):
        '''Text to Text Gemini Request Endpoint'''
        msg = params.get('chat','')
        chat_history = params.get('history', [])

        system_message = [
            {
                "role": "user", 
                "parts": "You are an expert consultant and doctor specializing in autism spectrum disorder (ASD) named Aasha. Your role is to provide compassionate, research-backed, and practical advice to parents seeking guidance on raising and supporting their neurodivergent child. Ensure that your responses are evidence-based, empathetic, and easy to understand. Limit to 200 words. Do not answer out of questions unrealted to advice regarding physchology." },
        ]

        full_history = system_message + chat_history
        chat_session = model.start_chat(history=full_history)

        try:
            response = chat_session.send_message(msg)
            print(response.text)
            return {"text":response.text}
        except Exception as e:
            return {"error" : str(e)}, 500


# --------------------------------------------------------------------
# Firestore route
# --------------------------------------------------------------------

@parent_bp.route("/child_create")
class ChildPOST(MethodView):
    # POST REQUEST 
    @parent_bp.response(status_code=201)
    @parent_bp.arguments(schema=ChildCreateSchema)
    def post(self, params):
        '''Creating a child document for the first time'''

        #Verify child params
        child = Child.from_dict(params)

        # Create a child document in firestore
        status, cid = create_child_entry(child) 
        if status==False:
            return {
                    "status":500,
                    "message":"Failed to create a child"
                    }, 500

        # Store child_id in session cookie
        session['child_id'] = cid
        return {"status" : 201,
                "message":"Successfully created child document" } 


@parent_bp.route("/child_cred_update")
class ChildCredPUT(MethodView):
    @parent_bp.response(status_code=200)
    @parent_bp.arguments(schema=ChildCredentialsUpdateSchma)
    def put(self, params):
        ''' Update the username and password for a child user'''
        # Check if username exists
        if check_username_exists(params['username']):
            return { "status":400, "message":"Username exists already"}

        # Create a child object to verify params
        child: Child = Child.from_dict(params)
        child_id = session.get('child_id', None)  

        # Child not found
        if child_id == None:
            return {"status":400,
                    "message": "Child_ID not found" }, 400

        # Update Child Entry
        status = update_child_entry(child_id, child) 
        return { "status": 200 , "message" : status }


# --------------------------------------------------------------------
# Depreciated routes
# --------------------------------------------------------------------

# We are not using the below function in the current version.
# @app.route("/stream", methods=["POST"])
# def stream():
#     """Streams AI responses for real-time chat interactions.
#
#     This function initiates a streaming session with the Gemini AI model,
#     continuously sending user inputs and streaming back the responses. It handles
#     POST requests to the '/stream' endpoint with a JSON payload similar to the
#     '/chat' endpoint.
#
#     Args:
#         None (uses Flask `request` object to access POST data)
#
#     Returns:
#         A Flask `Response` object that streams the AI-generated responses.
#     """
#     def generate():
#         data = request.json
#         msg = data.get('chat','')
#         chat_history = data.get('history',[])
#
#         chat_session = model.start_chat(history=chat_history)
#         response = chat_session.send_message(msg,stream=True)
#
#         for chunk in response:
#             yield f"{chunk.txt}"
#
#         return Response(stream_with_context(generate()), mimetype="text/event-stream")
#     
#
