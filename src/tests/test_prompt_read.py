from unittest import TestCase
from src.prompts.prompt_reader import read_prompt, PromptName

class TestPromptReader(TestCase):
    def test_read_prompt_success(self):
        result = read_prompt(PromptName.MAKE_BILINGUAL, target_language="Russian")
        assert len(result) > 0, "Prompt content should not be empty"
        print (f"Prompt content: {result}")
