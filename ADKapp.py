import os
import tempfile
import json
from flask import Flask, request, render_template, jsonify
# Import the Groq library for the Whisper ASR service
from groq import Groq
# Import the requests library for making HTTP requests to the external API
import requests 
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- EXTERNAL CHAT API CONFIG ---
# URL for the external chat service
EXTERNAL_CHAT_URL = "https://adkweb.pythonanywhere.com/api/chat/"
# Basic Auth credentials (Must be set in .env for security)
CHAT_USERNAME = os.getenv("ADK_CHAT_USERNAME")
CHAT_PASSWORD = os.getenv("ADK_CHAT_PASSWORD")

# --- WHISPER API CONFIG (Still using Groq for ASR) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY not found. ASR/Whisper API calls will fail.")
if not (CHAT_USERNAME and CHAT_PASSWORD):
    print("Warning: ADK_CHAT_USERNAME or ADK_CHAT_PASSWORD not found. External chat calls will fail.")


@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

def get_external_chat_response(prompt, session_id='ae89f544'):
    """
    Sends the user prompt to the external ADK chat API 
    and retrieves the response using Basic Authentication.
    """
    if not (CHAT_USERNAME and CHAT_PASSWORD):
        return "I cannot connect to my external brain. Missing credentials."
    
    # Set the query parameters including the session ID (using the default from Postman)
    params = {'session_id': session_id}
    
    # JSON payload containing the user's message
    payload = {
        "message": prompt
    }
    
    # Basic Authentication tuple
    auth = (CHAT_USERNAME, CHAT_PASSWORD)
    
    try:
        # Make the POST request to the external API
        response = requests.post(
            EXTERNAL_CHAT_URL, 
            params=params,
            auth=auth, 
            json=payload, 
            timeout=15 
        )
        response.raise_for_status() # Raise exception for 4xx or 5xx status codes

        data = response.json()
        
        # --- MODIFIED LOGIC: Look for 'response' key instead of 'reply' ---
        if 'response' in data:
            return data['response']
        else:
            print(f"External API returned unexpected structure: {data}")
            return "The external chat service is responding, but I can't understand its reply format."
        # ------------------------------------------------------------------

    except requests.exceptions.RequestException as e:
        print(f"External Chat API Error: {e}")
        return f"I failed to connect to the external chat service: {e}. Check your connection or credentials."
    except json.JSONDecodeError:
        print(f"External Chat API Error: Failed to decode JSON response: {response.text}")
        return "The chat service returned an unreadable response."


@app.route('/process_audio', methods=['POST'])
def process_audio():
    """Receives audio blob, transcribes it, and generates a chat response."""
    if 'audio_file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio_file']
    
    if not GROQ_API_KEY:
        return jsonify({"error": "Server ASR API key (GROQ) is missing."}), 500

    # Initialize Groq client only for Whisper ASR
    client = Groq(api_key=GROQ_API_KEY)

    # 1. Save the received audio file temporarily
    temp_file_path = None
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.filename.split('.')[-1]}")
        audio_file.save(temp_file.name)
        temp_file_path = temp_file.name
        temp_file.close()

        # 2. Transcribe the audio file using Groq Whisper (ASR)
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

        # 3. Get CHAT response from the external ADK API (LLM replaced)
        # We use a fixed session ID placeholder from the Postman example
        llm_response = get_external_chat_response(user_prompt, session_id='ae89f544')

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
    app.run(debug=True, host='0.0.0.0')
