import re

from jinja2 import Template
from src.data_classes.bilingual_text import BilingualText
from src.config import SSML_TEMPLATE_PATH, SSML_CHUNK_SIZE

def load_ssml_template():
    with open(SSML_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


# Function to generate SSML
def generate_ssml(
    bilingual_text: BilingualText,
    break_time: str,
    source_language_voice: str,
    target_language_voice: str = None,
    # Optional parameter for target language voice, if not - only one language will be used for TTS
    repeat_slowly: bool = False,  # if yes - the source text will be repeated slowly
) -> str:
    ssml_template = load_ssml_template()
    template = Template(ssml_template)
    ssml_output = template.render(
        paragraphs=bilingual_text.paragraphs,
        source_language=bilingual_text.source_language,
        target_language=bilingual_text.target_language,
        source_language_voice=source_language_voice,
        target_language_voice=target_language_voice,
        break_time=break_time,
        repeat_slowly=repeat_slowly,
    )
    return ssml_output


def chunk_ssml(ssml: str, chunk_size: int = SSML_CHUNK_SIZE) -> list:
    """
    Splits SSML into chunks of specified size.
    chuning border is voice tag.
    thus, for chunk_size = 3 and intput like:
    ```<speak version="1.0" xml:lang="tr-TR">
        <voice name="tr-TR-AhmetNeural">
           Kenan Bey, erkenden uyandı.
        </voice>

        <voice name="en-GB-RyanNeural"> Kenan Bey woke up early. </voice>

        <voice name="tr-TR-AhmetNeural">
           Eşi ve çocukları hâlâ uyuyordu.
        </voice>

        <voice name="en-GB-RyanNeural"> His wife and children were still sleeping. </voice>
        <voice name="tr-TR-AhmetNeural">
           O çok heyecanlıydı.
        </voice>

    </speak>
    ```
    it should give:
    ```xml
     ```<speak version="1.0" xml:lang="tr-TR">
        <voice name="tr-TR-AhmetNeural">
           Kenan Bey, erkenden uyandı.
        </voice>

        <voice name="en-GB-RyanNeural"> Kenan Bey woke up early. </voice>

        <voice name="tr-TR-AhmetNeural">
           Eşi ve çocukları hâlâ uyuyordu.
        </voice>

    </speak>
    '''
    and
    ```xml
    ```<speak version="1.0" xml:lang="tr-TR">
       <voice name="en-GB-RyanNeural"> His wife and children were still sleeping. </voice>
        <voice name="tr-TR-AhmetNeural">
           O çok heyecanlıydı.
        </voice>

    </speak>```
    """
    # Extract the <speak ...> tag with all attributes and the closing </speak>
    speak_open_match = re.match(r"\s*(<speak[^>]*>)", ssml)
    speak_close_match = re.search(r"(</speak>)\s*$", ssml)
    if not speak_open_match or not speak_close_match:
        raise ValueError("SSML must have a root <speak> tag.")

    speak_open = speak_open_match.group(1)
    speak_close = speak_close_match.group(1)

    # Find all <voice ...>...</voice> blocks
    voice_blocks = re.findall(r"(<voice[^>]*>.*?</voice>)", ssml, re.DOTALL)
    chunks = []
    current_chunk = []
    count = 0

    for block in voice_blocks:
        current_chunk.append(block)
        count += 1
        if count >= chunk_size:
            chunk_ssml = speak_open + "\n" + "\n".join(current_chunk) + "\n" + speak_close
            chunks.append(chunk_ssml)
            current_chunk = []
            count = 0

    if current_chunk:
        chunk_ssml = speak_open + "\n" + "\n".join(current_chunk) + "\n" + speak_close
        chunks.append(chunk_ssml)

    return chunks
