from flask.views import MethodView
from flask_smorest import Blueprint
from config import GEMINI_API_KEY
from parent_bot.schema import ChatSchema 
import google.generativeai as genai

parent_bp = Blueprint('Parent Bot API', __name__, 
                    url_prefix='/parent', 
                    description="")

# Configure Google GenAI API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel( model_name="gemini-1.5-flash" )


@parent_bp.route("/chat_gemini")
class ChatRoute(MethodView):
    # POST REQUEST 
    @parent_bp.response(status_code=201)
    @parent_bp.arguments(ChatSchema)
    def post(self, params):
        '''Text to Text Gemini Request Endpoint'''
        msg = params.get('chat','')
        chat_history = params.get('history', [])

        system_message = [
            {"role": "user", "parts": "You are an expert consultant and doctor specializing in autism spectrum disorder (ASD) named Aasha. Your role is to provide compassionate, research-backed, and practical advice to parents seeking guidance on raising and supporting their neurodivergent child. Ensure that your responses are evidence-based, empathetic, and easy to understand. Limit to 200 words. Do not answer out of questions unrealted to advice regarding physchology." },
        ]

        full_history = system_message + chat_history
        chat_session = model.start_chat(history=full_history)

        try:
            response = chat_session.send_message(msg)
            print(response.text)
            return {"text":response.text}
        except Exception as e:
            return {"error" : str(e)}, 500






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
