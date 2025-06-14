from enum import StrEnum
from pathlib import Path

class PromptName(StrEnum):
    """
    Enum for prompt names used in text processing.
    """
    MAKE_BILINGUAL = "src/prompts/make_text_bilingual.md"

def read_prompt(prompt_name: PromptName, **kwargs) -> str:
    """
    Reads a prompt from a file and returns its content.

    Args:
        prompt_name (PromptName): The name of the prompt file to read.

    Returns:
        str: The content of the prompt file.
        kwargs: Optional keyword arguments to format the prompt content.
    """
    try:
        path = Path(prompt_name.value)
        with path.open('r', encoding='utf-8') as file:
            file_content = file.read()
            return file_content if not kwargs else file_content.format(**kwargs)
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file '{prompt_name.value}' not found.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the prompt: {e}")