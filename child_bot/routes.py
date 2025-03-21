import os
from flask import abort, send_file, jsonify
from flask_smorest import Blueprint
from flask.views import MethodView
from werkzeug.utils import secure_filename
from marshmallow import ValidationError
from child_bot.config import UPLOAD_FOLDER
from child_bot.helper import call_chirp, call_gemini, call_tts, extract_emotion
from child_bot.schema import AudioSchema, TextSchema

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

child_bp = Blueprint('Child Bot API', __name__, 
                    url_prefix='/child', 
                    description="")

sys_instr = "You are SAATHI, an AI psychiatrist designed to support neurodivergent children aged 5-15. You speak in a warm, friendly tone, using simple words and short sentences to ensure clarity and comfort. Your goal is to provide actionable, reassuring advice by offering practical coping strategies, relatable examples, and clear explanations without using complex language or long paragraphs. When a child shares their emotions, you acknowledge their feelings with kindness and suggest helpful ways to cope, such as deep breathing or talking to a trusted adult. If a child mentions self-harm, bullying, or distress, you gently encourage them to seek help from a responsible person. You tailor your responses to different neurodivergent needs, providing short, engaging tips for ADHD, clear and direct language for autism, and calming techniques for anxiety. You avoid using special characters like *, #, or emojis and ensure all messages are easy to read and formatted in plain text. By following these guidelines, you create a safe, supportive, and effective space for neurodivergent children to express themselves and receive guidance."

# @child_bp.route("/gemini_text")
# class RootRoute(MethodView):
#     # POST REQUEST 
#     @child_bp.response(status_code=201, schema = TextSchema)
#     @child_bp.arguments(schema=TextSchema)
#     def post(self, params):
#         '''Text to Text Gemini Request Endpoint'''
#         return {"text": call_gemini(params['text'], sys_instr) } 


@child_bp.route("/voice_gemini")
class AudioRoute(MethodView):
    # POST REQUEST
    @child_bp.response(status_code=201, schema = AudioSchema)
    @child_bp.arguments(schema = AudioSchema, location='files')
    def post(self, params):
        ''' Voice to Voice Gemini Request Endpoint '''

        # Acquiring the audio file provided
        file = params['file']
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER,  filename)
        file.save(file_path)

        # Transcribing it to text from audio
        try:
            transcribed_resp = call_chirp(file_path)
            print("Transribe: ", transcribed_resp)
        except Exception as e:
            return jsonify({"error":"Google Chirp Failed to Transcribe.", 
                            "message": str(e) })

        # Extracting emotion from audio
        try: 
            emotion = extract_emotion(file_path)
            transcribed_resp += "The user feels might be feeling the following emotion but we dont know for sure: " + emotion
        except Exception as e:
            return jsonify({"error":"SER Failed.", 
                            "message": str(e) })

        # Generating Repsonse using Gemini
        try:
            reply = call_gemini(transcribed_resp, sys_instr)
            print("Reply: ",reply)
        except Exception as e:
            return jsonify({"error":"Google Gemini Failed to Reply", 
                            "message": str(e) })

        # Generating Speech from Test using TTS
        output_file_path = 'output.wav'
        try:
            call_tts( reply, output_file_path )
        except Exception as e:
            return jsonify({"error":"Google TTS Failed to make it into Audio", 
                            "message": str(e) })

        # Sending Newly created File
        if not os.path.exists(output_file_path):
            abort(404, description="File not found")
        return send_file(
            output_file_path,
            mimetype='audio/wav',
            as_attachment=True, 
            download_name= output_file_path 
        )


