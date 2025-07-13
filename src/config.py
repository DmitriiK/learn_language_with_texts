
import os
from dotenv import load_dotenv

load_dotenv()

SESSION_DATA_FILE_PATH = 'src/static/data'
LOGS_DIR = 'logs'
# Usage tracking
USAGE_DATA_PATH = 'data/audit/usage_stats.json'
LLM_MODEL = "gemini-2.0-flash"
MAX_PARAGRAPH_LENGTH = 1000
#  Azure TTL
SPEECH_REGION = 'westeurope'
SPEECH_KEY = os.getenv('SPEECH_KEY')
LIST_OF_VOICES_FILE_PATH = 'src/tts/tts_voices.yml'
SSML_TEMPLATE_PATH = 'src/tts/ssml_template.j2'
SSML_CHUNK_SIZE = 45  # looks like Azure TTS not able to cope with more than 50 voice alterations in the SSML
AUDIO_PAUSE_BREAK = 750  # Default pause, in ms break time for SSML after each sintagma


TEST_DATA_PATH = "src/tests/test_data/outputs/billing_text.json"  # Path to the test data file for testing purposes
OVERALL_TOTAL_TEXT_LENGTH_QUOTA = 1000000  # Overall text length quota for all users