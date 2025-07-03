import unittest
from src.tts.tts_generator import TTS_GEN

class TestTTS(unittest.TestCase):

    def test_turkish(self):
        #  https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts
        #  text = "Hello! 你好! Hola! नमस्ते! Bonjour! こんにちは! مرحبا! 안녕하세요! Ciao! Cześć! Привіт! வணக்கம்!"
        text = """Ben bunu bilmiyordum. Hava çok sıcak oldu."""
        tts = TTS_GEN('tr-TR-EmelNeural')
        tts.generate_audio(text, 'test_tts')

if __name__ == '__main__':
    ttts = TestTTS()
    ttts.test_turkish()
    