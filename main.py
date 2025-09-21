import ursina
from ursina import *
import sounddevice as sd
import numpy as np
import threading
import tempfile
import time
import os
import pyttsx3
import groq

# --- IMPORTANT SETUP ---
# Replace with your actual Groq API key.
# It is highly recommended to use environment variables for this.
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"

# --- GLOBAL VARIABLES & ENGINE SETUP ---
app = Ursina(title="LLM Character Demo", borderless=False)

# Ursina entities for the UI
status_text = Text(text="Click the button to talk to me!", origin=(0, 0), scale=2, y=0.3, background=True)
user_prompt_text = Text(text="", origin=(0, 0), scale=1, y=0.2, background=True)
llm_response_text = Text(text="", origin=(0, 0), scale=1, y=0.1, background=True)
mic_button = Button(text="Press to Talk", color=color.azure, scale=(.3, .1), y=-0.4)

# Character entity
character = Entity(
    model="ursina_cube", 
    color=color.blue,
    scale=1,
    y=0,
    z=2,
    collider='box'
)

# Set up the camera
EditorCamera(parent=character)

# --- AUDIO & API PROCESSING FUNCTIONS ---

# Function to record audio from the microphone
def record_audio():
    """Records audio from the microphone for a set duration."""
    global status_text
    status_text.text = "Listening..."
    
    # Recording parameters
    samplerate = 16000
    duration = 5
    
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    
    temp_audio_file = tempfile.mktemp(suffix=".wav")
    from scipy.io.wavfile import write
    write(temp_audio_file, samplerate, recording)
    
    return temp_audio_file

# Function to transcribe audio using Groq's Whisper API
def transcribe_audio_with_groq(file_path):
    """Transcribes an audio file to text using the Groq Whisper API."""
    global status_text, user_prompt_text
    status_text.text = "Transcribing..."
    
    if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        status_text.text = "Error: Please set your Groq API key in the code."
        return None

    client = groq.Groq(api_key=GROQ_API_KEY)
    
    try:
        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(file_path), file.read()),
                model="whisper-large-v3",
                response_format="json",
            )
            transcript_text = transcription.text
            user_prompt_text.text = f"You: {transcript_text}"
            return transcript_text
    except Exception as e:
        status_text.text = f"Transcription Error: {e}"
        print(f"Transcription Error: {e}")
        return None
    finally:
        os.remove(file_path)

# Function to get a response from the Groq LLM
def get_groq_response(prompt):
    """Gets a chat completion from the Groq API."""
    global status_text, llm_response_text
    status_text.text = "Thinking..."

    if not GROQ_API_KEY or GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE":
        status_text.text = "Error: Please set your Groq API key in the code."
        return "Sorry, I can't talk right now. My API key is missing!"
    
    client = groq.Groq(api_key=GROQ_API_KEY)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly and helpful character in a video game. Your name is Ursy. Keep your responses concise and conversational."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-8b-8192"
        )
        response_text = chat_completion.choices[0].message.content
        llm_response_text.text = f"Ursy: {response_text}"
        return response_text
    except Exception as e:
        status_text.text = f"Groq API Error: {e}"
        print(f"Groq API Error: {e}")
        return "I'm having trouble connecting to my brain right now. Please try again."

# Function to convert text to speech and play it using pyttsx3
def speak_text(text):
    """Converts text to speech and plays the audio using pyttsx3."""
    global status_text
    status_text.text = "Speaking..."
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        status_text.text = f"TTS Error: {e}"
        print(f"TTS Error: {e}")

# Main conversation flow triggered by the button
def start_conversation():
    mic_button.disable()
    
    thread = threading.Thread(target=process_conversation)
    thread.start()

def process_conversation():
    audio_file_path = record_audio()
    if not audio_file_path:
        mic_button.enable()
        return
        
    user_prompt = transcribe_audio_with_groq(audio_file_path)
    if not user_prompt:
        mic_button.enable()
        return

    groq_response = get_groq_response(user_prompt)
    
    speak_text(groq_response)
    
    status_text.text = "Conversation complete. Click the button to talk again!"
    mic_button.enable()

mic_button.on_click = start_conversation

app.run()
