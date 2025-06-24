from unittest import TestCase
from src.text_processing.llm_communicator import create_bilingual_text

class TestLLM(TestCase):
    def test_create_bilingual_text(self):
        with open("src/tests/test_data/inputs/turkish_text.txt", "r") as file:
            input_text = file.read()

        target_language = "Russian"
        result = create_bilingual_text(input_text, target_language)
        assert len(result.paragraphs) > 0, "Result should contain at least one paragraph"
        assert result.source_language in ["Turkish",'tr'], "Source language should be Turkish"
        print(result.to_yaml())