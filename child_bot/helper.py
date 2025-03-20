from google import genai
from google.cloud import speech_v1 as speech
from google.cloud import texttospeech
from google.genai import types
from child_bot.config import GEMINI_API_KEY
from scipy.io import wavfile
from transformers import pipeline

pipe = pipeline("audio-classification", model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition")
def call_gemini(prompt: str, context: str):
    """ Used for calling Gemini with a prompt"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(model="gemini-2.0-flash", 
                                              contents = prompt, 
                                              config=types.GenerateContentConfig(
                                                system_instruction=context)
                                              )
    return response.text

def convert_to_mono(input_file: str, output_file: str):
    """ Converting a file to Mono Audio using SciPy """ 
    sample_rate, data = wavfile.read(input_file)

    if data.ndim == 2: #if Dual Audio then convert to Mono
        mono_data = data.mean(axis=1).astype(data.dtype)
    else: # Already mono
        mono_data = data

    wavfile.write(output_file, sample_rate, mono_data)
    return sample_rate

def call_chirp(input_file: str):
    """ Calling Google Chirp to convert audio to text """
    sample_rate = convert_to_mono(input_file, "temp.wav")
    client = speech.SpeechClient.from_service_account_file("gcp_key.json") #Requires Service Account

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
        try:
            return response.results[0].alternatives[0].transcript
        except:
            return "Chirp Model Failed to recognize Text from Speech"

def call_tts(text: str, output_file: str):
    """ Calling Google's Text to Speech Model """ 
    client = texttospeech.TextToSpeechClient.from_service_account_file(
            "gcp_key.json")

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

def extract_emotion(input_file : str):
    results = pipe(input_file)
    
    # Find the emotion with the highest score
    best_result = max(results, key=lambda x: x['score'])
    
    print("Emotion Detected: ", best_result['label'])
    return best_result['label']
