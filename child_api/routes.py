import os
import base64
from flask import abort, send_file, jsonify, session
from flask_smorest import Blueprint
from flask.views import MethodView
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER
from child_api.helper import call_chirp, call_gemini, call_tts, extract_emotion, get_wav_duration
from child_api.schema import AudioSchema, ChildLoginSchma
from firestore import add_new_conversation, check_username_password, fetch_all_conversations, fetch_chat_summary

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

child_bp = Blueprint('Child API', __name__, 
                    url_prefix='/child', 
                    description="")

# -----------------------------------------------------------------
# CHATBOT ROUTES
# -----------------------------------------------------------------

@child_bp.route("/voice_chat")
class AudioRoute(MethodView):
    # POST REQUEST
    @child_bp.response(status_code=201, schema = AudioSchema)
    @child_bp.arguments(schema = AudioSchema, location='files')
    def post(self, params):
        ''' Voice to Voice Gemini Request Endpoint '''

        # Acquiring the audio file provided
        file = params['file']
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER,filename)
        file.save(file_path)

        # Getting the duration of audio sent
        prompt_audio_duration = get_wav_duration(file_path)

        # Transcribing it to text from audio
        try:
            transcribed_resp = call_chirp(file_path)
            print("Transribe: ", transcribed_resp)
        except Exception as e:
            return jsonify({"error":"Google Chirp Failed to Transcribe.", 
                            "message": str(e) }), 500

        # Extracting emotion from audio
        try: 
            emotion = extract_emotion(file_path)
        except Exception as e:
            return jsonify({"error":"SER Failed.", 
                            "message": str(e) }), 500

        # Storing emotion
        emotion_arr = session.get('emotion',[]) + [emotion]
        session['emotion'] = emotion_arr

        # Loading previos chat history
        chat_history = session.get('chat_history', [])

        # Generating Repsonse using Gemini
        try:
            reply = call_gemini(transcribed_resp, chat_history, emotion)
            print("Reply: ",reply)
        except Exception as e:
            return jsonify({"error":"Google Gemini Failed to Reply", 
                            "message": str(e) }), 500

        # Generating Speech from Test using TTS
        output_file_path = 'output.wav'
        try:
            call_tts( reply, output_file_path )
        except Exception as e:
            return jsonify({"error":"Google TTS Failed to make it into Audio", 
                            "message": str(e) }), 500

        # Sending Newly created File
        if not os.path.exists(output_file_path):
            abort(404, description="File not found")

        # Read and encode file as Base64
        with open(output_file_path, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("utf-8")


        reply_audio_duration = get_wav_duration(output_file_path) 

        # Setting up chat history
        user_conv = {
                "role":"user",
                "parts":transcribed_resp,
                }
        model_conv = {
                "role":"model",
                "parts": reply ,
                }

        if len(chat_history) == 0:
            chat_history = [ user_conv, model_conv ]
        else:
            chat_history += [ user_conv, model_conv ]

        # Storing session variables
        session['chat_history'] = chat_history
        session['duration'] = ( session.get('duration', 0)
                                + prompt_audio_duration 
                                + reply_audio_duration )


        # print(session.get('emotion', ''))
        # print(session.get('chat_history', ''))
        # print(session.get('duration', ''))

        return send_file(
            output_file_path,
            mimetype='audio/wav',
            as_attachment=True, 
            download_name= output_file_path 
        )

@child_bp.route("/end_chat")
class EndChat(MethodView):
    @child_bp.response(status_code=200)
    def post(self):
        ''' End call endpoint to save chat information '''
        
        # Fetch all required information from session cookie
        child_id = session.get('child_id', None)
        emotion = session.get('emotion', None)
        duration = session.get('duration', None)
        chat_history = session.get('chat_history', None)
        if not child_id:
            return {"status":404, "message": "Child_ID not found"}, 404
        if not chat_history:
            return {"status":404, "message": "No chat found"}, 404
        if not emotion:
            return {"status":404, "message": "Emotions not found"}, 404
        if not duration:
            return {"status":404, "message": "Duration not found"}, 404

        # Save all of them as a new conversation document in Firestore
        status, mssg = add_new_conversation( child_id, chat_history , emotion, duration )

        if status == False:
            return { "status":400, "message":mssg}, 400
        return { "status": 200 , "message":mssg }

# -----------------------------------------------------------------
# FIRESTORE ROUTES
# -----------------------------------------------------------------

@child_bp.route("/login")
class ChildLoginPOST(MethodView):
    # POST REQUEST 
    @child_bp.response(status_code=200)
    @child_bp.arguments(schema=ChildLoginSchma)
    def post(self, params):
        ''' Login Endpoint for the child user '''
        # Check if the username password combination matches any child user
        status, child_id = check_username_password(params['username'], params['password']) 

        # If yes, store the child_id from now onwards
        session['child_id'] = child_id
        if child_id is None:
            return {"message" : "Forbidden: Incorrect username or password.", "status": 404 }, 404

        # Now the child has logged in 
        session['child_id'] = child_id
        return {"message" : status,  
                "status": 200 }

@child_bp.route("/fetch_summary")
class ChildSummary(MethodView):
    @child_bp.response(status_code=200)
    def get(self):
        '''Return back the summary and a list of all the conversations of this child'''
        child_id = session.get('child_id', None)  
        if child_id == None:
            return {"status":404,
                    "message": "Child_ID not found" }, 404
        # Fetch chat summary 
        chat_summary = fetch_chat_summary(child_id)
        if chat_summary == None:
            return {"status":404,
                    "message": "Chat Summary not found" }, 404

        # Fetch conversation list
        chat_summary['conversation_list'] = fetch_all_conversations(child_id)

        return chat_summary

# ---------------------
# DEV ONLY Routes
# ---------------------

@child_bp.route("/clear_session_cookies")
class ClearCookies(MethodView):
    @child_bp.response(status_code=200)
    def get(self):
        '''delete all session cookies'''
        session.pop("chat_history", None)
        session.pop("child_id", None)
        session.pop("duration", None)
        session.pop("emotion", None)
        return {"status":200, "message":"Cleared all session cookies"}
