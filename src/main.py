import json
import os
import logging
from enum  import StrEnum

from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from src.text_processing.llm_communicator import create_bilingual_text
from src.text_processing.nlp import lemmatize
from src.data_classes.lemma_index import LemmasIndex
from src.data_classes.bilingual_text import BilingualText
from src.tts.tts_generator import TTS_GEN

import src.config as cfg

app = FastAPI()

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

class AudioOutputFormat(StrEnum):
    bilingual = "bilingual"
    source_language = "source_language"
    target_language = "target_language"

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

@app.post("/api/make_bilingual2")
def make_bilingual2(req: TranslationRequest):
    try:
        result = create_bilingual_text(req.source_text, req.target_language)
        # Only return JSON for both 'web' and 'json' output formats
        if req.output_format in ('web', 'json'):
            content = result.model_dump
            content["data_hash"] = hash(result)
            return JSONResponse(content=content)
        elif req.output_format == 'pdf':
            # TODO: Implement PDF export
            return JSONResponse(content={"error": "PDF export not implemented yet."}, status_code=501)
        else:
            return JSONResponse(content={"error": "Unknown output_format"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)




@app.get("/api/make_audio")
def make_audio(bilingual_text_hash: int, output_format: AudioOutputFormat):
    """
    Endpoint to generate audio for a given bilingual text hash and output format (GET method).
    Returns a JSON with audio_url or error.
    """
    try:
        output_dir = os.path.join(cfg.SESSION_DATA_FILE_PATH, str(bilingual_text_hash))
        bt_file_path = os.path.join(output_dir, "bilingual_text.json")
        if not os.path.exists(bt_file_path):
            return JSONResponse(content={"error": f"Bilingual text with hash {bilingual_text_hash} not found."}, status_code=404)
        bilingual_text_instance = BilingualText.from_json_file(bt_file_path)
        output_audio_file_path = os.path.join(output_dir, f"audio_{bilingual_text_hash}{output_format}")
        break_time = "750ms" # to configure in the future
        logging.info(f"Generating audio for bilingual text with hash {bilingual_text_hash} to {output_audio_file_path}")
        tts = TTS_GEN()
        tts.binlingual_to_audio(bln=bilingual_text_instance, break_time=break_time, output_file_name=output_audio_file_path)
        # Generate the URL relative to the static mount
        audio_url = f"/static/data/{bilingual_text_hash}/audio_{bilingual_text_hash}{output_format}.mp3"
        return JSONResponse(content={"audio_url": audio_url})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@app.post("/api/make_bilingual")
def make_bilingual(req: TranslationRequest):
    # This is a stub for the make_bilingual endpoint
    # It returns the contents of a test JSON file for testing purposes
    print("Received request for stub data")
    with open("src/tests/test_data/outputs/billing_text.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        bt: BilingualText = BilingualText.model_validate(data)
        bt_hash = save_to_session_store(bt)
        data["data_hash"] = bt_hash

    print("Returning stub data")
    return JSONResponse(content=data)

def save_to_session_store(bt):
    bt_hash = hash(bt)
    output_dir = os.path.join(cfg.SESSION_DATA_FILE_PATH, str(bt_hash))
    os.makedirs(output_dir, exist_ok=True)
    # Write the JSON to a file in the output directory
    output_path = os.path.join(output_dir, "bilingual_text.json")
    with open(output_path, "w", encoding="utf-8") as out_f:
        out_f.write(bt.to_json())
    return bt_hash

@app.get("/")
def index():
    with open("src/static/index.html") as f:
        return HTMLResponse(f.read())
    

@app.post("/api/lemmatize")
def lemmatize_endpoint(req: LemmatizeRequest):
    result: LemmasIndex = lemmatize(text=req.text, lang=req.language, filter_out_stop_words=req.filter_out_stop_words)
    frequency_list = sorted(result.lemmas, key=lambda lemma: lemma.number_of_occurrences, reverse=True)

    # Only include lemma, number_of_words, and number_of_occurencs in the response
    for_fe = [
        {
            "lemma": lemma.lemma,
            "number_of_words": lemma.number_of_words,
            "number_of_occurrences": lemma.number_of_occurrences
        }
        for lemma in frequency_list
    ]
    return JSONResponse(content={"lemmas": for_fe})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # uvicorn src.main:app --reload

