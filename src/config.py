
import os
from dotenv import load_dotenv

load_dotenv()

SESSION_DATA_FILE_PATH = 'src/static/data'
llm_model = "gemini-2.0-flash"
max_paragraph_length = 1000
#  Azure TTL
SPEECH_REGION = 'westeurope'
SPEECH_KEY = os.getenv('SPEECH_KEY')
LIST_OF_VOICES_FILE_PATH = 'src/tts/tts_voices.yml'
SSML_TEMPLATE_PATH = 'src/tts/ssml_template.j2'
AUDIO_PAUSE_BREAK = 750  # Default pause, in ms break time for SSML after each sintagma

# Usage tracking
USAGE_DATA_PATH = 'data/audit/usage_stats.json'

test_data_path = "src/tests/test_data/outputs/billing_text.json"  # Path to the test data file for testing purposes