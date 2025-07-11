
import os
from dotenv import load_dotenv

load_dotenv()

SESSION_DATA_FILE_PATH = 'src/static/data'
LLM_MODEL = "gemini-2.0-flash"
MAX_PARAGRAPH_LENGTH = 1000
#  Azure TTL
SPEECH_REGION = 'westeurope'
SPEECH_KEY = os.getenv('SPEECH_KEY')
LIST_OF_VOICES_FILE_PATH = 'src/tts/tts_voices.yml'
SSML_TEMPLATE_PATH = 'src/tts/ssml_template.j2'
AUDIO_PAUSE_BREAK = 750  # Default pause, in ms break time for SSML after each sintagma

# Usage tracking
USAGE_DATA_PATH = 'data/audit/usage_stats.json'

TEST_DATA_PATH = "src/tests/test_data/outputs/billing_text.json"  # Path to the test data file for testing purposes
OVERALL_TOTAL_TEXT_LENGTH_QUOTA = 1000000  # Overall text length quota for all users