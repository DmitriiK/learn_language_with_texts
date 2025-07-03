import unittest
import os
from src.tts.tts_generator import TTS_GEN

OUTPUT_DIR = 'src/tests/test_data/outputs/audio'
class TestTTS(unittest.TestCase):

    def test_turkish(self):
        #  https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts
        #  text = "Hello! 你好! Hola! नमस्ते! Bonjour! こんにちは! مرحبا! 안녕하세요! Ciao! Cześć! Привіт! வணக்கம்!"
        text = """Ben bunu bilmiyordum. Hava çok sıcak oldu."""
        output_file_name = os.path.join(OUTPUT_DIR, 'test_tts')
        tts = TTS_GEN('tr-TR-EmelNeural')
        tts.generate_audio(input_tts=text, output_file_name=output_file_name, is_ssml=False, skip_if_exists=False)

    def test_ssml(self):
        # Test generating audio from SSML using the example from SSML.xml
        with open('src/tests/test_data/outputs/SSML.xml', 'r', encoding='utf-8') as f:
            ssml = f.read()
        tts = TTS_GEN()
        output_file_name = os.path.join(OUTPUT_DIR, 'test_ssml')
        tts.generate_audio(input_tts=ssml, output_file_name=output_file_name, is_ssml=True, skip_if_exists=False)

if __name__ == '__main__':
    ttts = TestTTS()
    ttts.test_turkish()
    ttts.test_ssml()
