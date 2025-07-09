from pydantic import BaseModel

from src.tts.tts_generator import AudioOutputFormat


class TranslationRequest(BaseModel):
    source_text: str
    target_language: str
    output_format: str  # 'web' or 'pdf' or 'json'
    layout: str         # 'continuous' or 'side-by-side'


class AudioRequest(BaseModel):
    bilingual_text_hash: int
    output_format: AudioOutputFormat


class LemmatizeRequest(BaseModel):
    text: str
    language: str
    filter_out_stop_words: bool = False