import os
import tempfile
import json
from flask import Flask, request, render_template, jsonify
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- IMPORTANT SETUP ---
# Groq API Key must be set in your environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY not found. API calls will fail.")

@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

def get_groq_response(prompt):
    """Gets a chat completion from the Groq API."""
    if not GROQ_API_KEY:
        return "Sorry, I can't talk right now. My API key is missing on the server."
    
    client = Groq(api_key=GROQ_API_KEY)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly and helpful character in a video game named Ursy. Keep your responses concise and conversational."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-8b-instant"
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Groq LLM API Error: {e}")
        return "I'm having trouble connecting to my brain right now. Please try again."

@app.route('/process_audio', methods=['POST'])
def process_audio():
    """Receives audio blob, transcribes it, and generates an LLM response."""
    if 'audio_file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio_file']
    
    if not GROQ_API_KEY:
        return jsonify({"error": "Server API key is missing."}), 500

    client = Groq(api_key=GROQ_API_KEY)

    # 1. Save the received audio file temporarily
    temp_file_path = None
    try:
        # Groq Whisper API needs a file handle, so we save the incoming blob
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.filename.split('.')[-1]}")
        audio_file.save(temp_file.name)
        temp_file_path = temp_file.name
        temp_file.close()

        # 2. Transcribe the audio file using Groq Whisper
        with open(temp_file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(temp_file_path), file.read()),
                model="whisper-large-v3",
                response_format="json",
            )
            user_prompt = transcription.text.strip()
            
            if not user_prompt:
                return jsonify({
                    "user_prompt": "No clear speech detected.",
                    "llm_response": "I didn't quite catch that. Could you please speak up?"
                })

        # 3. Get LLM response
        llm_response = get_groq_response(user_prompt)

        return jsonify({
            "user_prompt": user_prompt,
            "llm_response": llm_response
        })

    except Exception as e:
        print(f"Server Processing Error: {e}")
        return jsonify({"error": f"An internal server error occurred: {e}"}), 500
    
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == '__main__':
    # Set host='0.0.0.0' for deployment environments like Canvas
    app.run(debug=True, host='0.0.0.0')
