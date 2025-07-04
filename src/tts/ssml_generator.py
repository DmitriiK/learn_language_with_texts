from jinja2 import Template
from src.data_classes.bilingual_text import BilingualText
import os

# Path to the SSML template file
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'ssml_template.jinja')

def load_ssml_template():
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        return f.read()

# Function to generate SSML
def generate_ssml(bilingual_text: BilingualText, source_language_voice: str, target_language_voice: str, break_time: str) -> str:
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

