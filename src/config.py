
import os
from dotenv import load_dotenv

load_dotenv()

llm_model = "gemini-2.0-flash"
max_paragraph_length = 1000
#  Azure TTL
SPEECH_REGION = 'westeurope'
SPEECH_KEY = os.getenv('SPEECH_KEY')
LIST_OF_VOICES_FILE_PATH = 'src/tts/tts_voices.yml'
SESSION_DATA_FILE_PATH = 'data'