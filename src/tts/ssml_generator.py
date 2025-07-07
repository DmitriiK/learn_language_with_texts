from jinja2 import Template
from src.data_classes.bilingual_text import BilingualText
import os
from src.config import SSML_TEMPLATE_PATH



def load_ssml_template():
    with open(SSML_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        return f.read()

# Function to generate SSML
def generate_ssml(bilingual_text: BilingualText
                  , break_time: str
                  , source_language_voice: str
                  , target_language_voice: str = None
                  # Optional parameter for target language voice, if not - only one language will be used for TTS
                  ) -> str:
    ssml_template = load_ssml_template()
    template = Template(ssml_template)
    ssml_output = template.render(
        paragraphs=bilingual_text.paragraphs,
        source_language=bilingual_text.source_language,
        target_language=bilingual_text.target_language,
        source_language_voice=source_language_voice,
        target_language_voice=target_language_voice,
        break_time=break_time
    )
    return ssml_output

