import unittest
import os
import json
from io import BytesIO

from src.data_classes.bilingual_text import BilingualText
from src.tts.tts_generator import TTS_GEN

OUTPUT_DIR = 'src/tests/test_data/outputs/audio'


class TestTTS(unittest.TestCase):

    def test_turkish(self):
        #  https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts
        #  text = "Hello! 你好! Hola! नमस्ते! Bonjour! こんにちは! مرحبا! 안녕하세요! Ciao! Cześć! Привіт! வணக்கம்!"
        text = """Ben bunu bilmiyordum. Hava çok sıcak oldu."""
        output_file_name = os.path.join(OUTPUT_DIR, 'test_tts')
        tts = TTS_GEN('tr-TR-EmelNeural')
        tts.generate_audio_file(input_tts=text, output_file_name=output_file_name, is_ssml=False, skip_if_exists=False)

    def test_ssml(self):
        # Test generating audio from SSML using the example from SSML.xml
        with open('src/tests/test_data/outputs/SSML.xml', 'r', encoding='utf-8') as f:
            ssml = f.read()
        tts = TTS_GEN()
        output_file_name = os.path.join(OUTPUT_DIR, 'test_ssml')
        tts.generate_audio_file(input_tts=ssml, output_file_name=output_file_name, is_ssml=True)

    def test_binlingual_to_audio(self):
        with open("src/tests/test_data/outputs/billing_text.json", "r", encoding="utf-8") as f:
            dict_data = json.load(f)
            bilingual_text_instance = BilingualText.model_validate(dict_data)
        break_time = "750ms"
        output_file_name = os.path.join(OUTPUT_DIR, 'test_bilingual')
        tts = TTS_GEN()
        tts.binlingual_to_audio(bln=bilingual_text_instance, break_time=break_time, output_file_name=output_file_name)

    def test_merge_audio_streams(self):
        tts = TTS_GEN()
        astr1: BytesIO = tts.generate_audio_stream(input_tts="First part ", is_ssml=False)
        astr2: BytesIO = tts.generate_audio_stream(input_tts="Second part", is_ssml=False)
        output_file_name = os.path.join(OUTPUT_DIR, 'test_merge_tts')
        
        # Concatenate audio streams
        merged_audio = BytesIO()
        merged_audio.write(astr1.read())
        merged_audio.write(astr2.read())
        merged_audio.seek(0)
        
        # Write the merged audio to file
        with open(f"{output_file_name}.mp3", "wb") as output_file:
            output_file.write(merged_audio.read())
        
        # Verify the file exists
        self.assertTrue(os.path.exists(f"{output_file_name}.mp3"))
        # Check the file size is greater than 0
        self.assertGreater(os.path.getsize(f"{output_file_name}.mp3"), 0)

    def test_generate_audio_file_from_multiple_inputs(self):
        # Test generating audio from multiple inputs
        tts = TTS_GEN()
        
        # Create test inputs
        input1 = "This is the first part of the audio."
        input2 = "This is the second part of the audio."
        
        # Set output file name
        output_file_name = os.path.join(OUTPUT_DIR, 'test_multiple_inputs')
        
        # Generate concatenated audio file
        tts.generate_audio_file_from_multiple_inputs(
            input_ttss=[input1, input2],
            is_ssml=False,
            output_file_name=output_file_name
        )
        
        # Verify the file exists
        self.assertTrue(os.path.exists(f"{output_file_name}.mp3"))
        # Check the file size is greater than 0
        self.assertGreater(os.path.getsize(f"{output_file_name}.mp3"), 0)
        
    def test_generate_audio_file_from_multiple_ssml_inputs(self):
        # Test generating audio from multiple SSML inputs
        with open('src/tests/test_data/outputs/SSML.xml', 'r', encoding='utf-8') as f:
            ssml = f.read()
        
        tts = TTS_GEN()
        output_file_name = os.path.join(OUTPUT_DIR, 'test_multiple_ssml_inputs')
        
        # Generate concatenated audio file with the same SSML repeated twice
        tts.generate_audio_file_from_multiple_inputs(
            input_ttss=[ssml, ssml],
            is_ssml=True,
            output_file_name=output_file_name
        )
        
        # Verify the file exists
        self.assertTrue(os.path.exists(f"{output_file_name}.mp3"))
        # Check the file size is greater than 0
        self.assertGreater(os.path.getsize(f"{output_file_name}.mp3"), 0)


if __name__ == '__main__':
    ttts = TestTTS()
    ttts.test_turkish()
    ttts.test_ssml()
    ttts.test_binlingual_to_audio()
    ttts.test_merge_audio_streams()
    ttts.test_generate_audio_file_from_multiple_inputs()
    ttts.test_generate_audio_file_from_multiple_ssml_inputs()
