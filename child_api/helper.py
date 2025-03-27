import google.generativeai as genai
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech
from config import GEMINI_API_KEY
from scipy.io import wavfile
from transformers import pipeline

from config import GCP_KEY


# ----------------------------------------------------------------------
# GOOGLE GEMINI Model
# ----------------------------------------------------------------------

gemini_context = "You are Aasha, an AI psychiatrist designed to support neurodivergent children aged 5-15. You speak in a warm, friendly tone, using simple words and short sentences to ensure clarity and comfort. Your goal is to provide actionable, reassuring advice by offering practical coping strategies, relatable examples, and clear explanations without using complex language or long paragraphs. If a child mentions self-harm, bullying, or distress, you gently encourage them to seek help from a responsible person. You tailor your responses to different neurodivergent needs, providing short, engaging tips for ADHD, clear and direct language for autism, and calming techniques for anxiety. You should not special characters like *, #, or emojis and ensure all messages are easy to read and formatted in plain text. Limit to 50 words"

def call_gemini(prompt: str, chat_history: list, emotion:str|None):
    """ Used for calling Gemini with a prompt"""
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash"
    )
    global gemini_context
    if emotion and len(emotion) > 0:
        gemini_context+= " The user has a small chance of being " + emotion

    # Insert system instruction at the beginning of history if provided
    if gemini_context and len(chat_history)==0:
        chat_history.insert(0, {"role": "model", "parts": gemini_context})

    chat_session = model.start_chat(history = chat_history)
    response = chat_session.send_message(prompt)
    return response.text



# ----------------------------------------------------------------------
# GOOGLE Chirp Model
# ----------------------------------------------------------------------

def call_chirp(input_file: str):
    """ Calling Google Chirp to convert audio to text """
    sample_rate = convert_to_mono(input_file, "temp.wav")
    client = speech.SpeechClient.from_service_account_file(GCP_KEY) #Requires Service Account

    with open("temp.wav", 'rb') as audio_file:
        # Making the parameters
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
                encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz = sample_rate,
                language_code = 'en-US'
                )
        # Making a request to Recognize text in Audio
        response = client.recognize(config = config, audio = audio)
        # print(response)
        try:
            return response.results[0].alternatives[0].transcript
        except Exception as e:
            return "Chirp Model Failed to recognize Text from Speech" + str(e)

# ----------------------------------------------------------------------
# GOOGLE TTS Model
# ----------------------------------------------------------------------

def call_tts(text: str, output_file: str):
    """ Calling Google's Text to Speech Model """ 
    client = texttospeech.TextToSpeechClient.from_service_account_file(GCP_KEY)

    # Making Required Parameters
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-IN",
        name="en-IN-Standard-A",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )
    # Perform the text-to-speech request
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    # Write the binary audio content to a file.
    with open(output_file, "wb") as out_file:
        out_file.write(response.audio_content)

# ----------------------------------------------------------------------
# Speech Emotion Recognition Model from huggingface.co
# ----------------------------------------------------------------------

pipe = pipeline("audio-classification", 
                model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition")
def extract_emotion(input_file : str):
    results = pipe(input_file)
    
    # Find the emotion with the highest score
    best_result = max(results, key=lambda x: x['score'])
    
    print("Emotion Detected: ", best_result['label'])
    return best_result['label']


# ----------------------------------------------------------------------
# Helper function for Audio Related Tasks
# ----------------------------------------------------------------------

def get_wav_duration(file_path):
    sample_rate, data = wavfile.read(file_path)
    duration = len(data) / sample_rate  # Duration in seconds
    return duration

def convert_to_mono(input_file: str, output_file: str):
    """ Converting a file to Mono Audio using SciPy """ 
    sample_rate, data = wavfile.read(input_file)

    if data.ndim == 2: #if Dual Audio then convert to Mono
        mono_data = data.mean(axis=1).astype(data.dtype)
    else: # Already mono
        mono_data = data

    wavfile.write(output_file, sample_rate, mono_data)
    return sample_rate
