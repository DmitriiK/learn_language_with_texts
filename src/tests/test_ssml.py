
import unittest
import json

from src.tts.ssml_generator import generate_ssml
from src.data_classes.bilingual_text import BilingualText

OUTPUT_DIR = 'src/tests/test_data/outputs/audio'
class TestSSML(unittest.TestCase):

    def test_ssml_gen(self):
        with open("src/tests/test_data/outputs/billing_text.json", "r", encoding="utf-8") as f:
            dict_data= json.load(f)
            bilingual_text_instance = BilingualText.model_validate(dict_data)
        # Define additional parameters
        source_language_voice = "tr-TR-AhmetNeural"
        target_language_voice = "en-US-AvaNeural"
        break_time = "750ms"

        # Generate SSML
        ssml_output = generate_ssml(
            bilingual_text=bilingual_text_instance,
            source_language_voice=source_language_voice,
            target_language_voice=target_language_voice,
            break_time=break_time
        )

        # Print the SSML output
        print(ssml_output)