
import json
import os
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from src.pdf_gen.pdf_generator import generate_bilingual_pdf
from src.text_processing.llm_communicator import create_bilingual_text
from src.text_processing.nlp import lemmatize
from src.data_classes.lemma_index import LemmasIndex
from src.data_classes.bilingual_text import BilingualText
from src.tts.tts_generator import TTS_GEN, AudioOutputFormat
import src.config as cfg

# Import authentication utilities
from src.authentication import get_current_user, UserRole

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
def make_bilingual2(req: TranslationRequest, user=Depends(get_current_user)):
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
def make_audio(bilingual_text_hash: int, output_format: AudioOutputFormat, break_time_ms: int = cfg.AUDIO_PAUSE_BREAK, user=Depends(get_current_user)):
    """
    Endpoint to generate audio for a given bilingual text hash and output format (GET method).
    Returns a JSON with audio_url or error.
    """
    try:
        output_dir = os.path.join(cfg.SESSION_DATA_FILE_PATH, str(bilingual_text_hash))
        bilingual_text_instance = read_from_session_store(bilingual_text_hash, output_dir=output_dir)
        audio_file_name = f"audio_{bilingual_text_hash}{output_format}"
        output_audio_file_path = os.path.join(output_dir, audio_file_name)
        logging.info(f"Generating audio for bilingual text with hash {bilingual_text_hash} to {output_audio_file_path}")
        tts = TTS_GEN()
        tts.binlingual_to_audio(bln=bilingual_text_instance,
                                break_time=f'{break_time_ms}ms',
                                output_file_name=output_audio_file_path, 
                                aof=output_format)
        # Generate the URL relative to the static mount
        audio_url = f"/static/data/{bilingual_text_hash}/{audio_file_name}.mp3"
        return JSONResponse(content={"audio_url": audio_url})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/make_bilingual")
def make_bilingual(req: TranslationRequest, user=Depends(get_current_user)):
    # This is a stub for the make_bilingual endpoint
    validation_response = validate_translation_request(req, user)
    if validation_response:
        return validation_response
    print("Received request for stub data")
    bt = get_test_blt()  # This should be replaced with actual logic to create BilingualText
    data = bt.model_dump()  
    bt_hash = save_to_session_store(bt)
    data["data_hash"] = bt_hash
    print("Returning stub data")
    return JSONResponse(content=data)


@app.post("/api/make-pdf", response_class=Response)
def make_pdf(req: TranslationRequest, user=Depends(get_current_user)):
    """Endpoint to generate PDF from bilingual text data"""
    try:
        bilingual_text_instance = get_test_blt()  # This should be replaced with actual logic to get BilingualText
        pdf_buffer = generate_bilingual_pdf(bilingual_text_instance)
        return Response(content=pdf_buffer, media_type="application/pdf")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/")
def index():
    with open("src/static/index.html") as f:
        return HTMLResponse(f.read())


@app.post("/api/lemmatize")
def lemmatize_endpoint(req: LemmatizeRequest, user=Depends(get_current_user)):
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


# utilities
def save_to_session_store(bt):
    bt_hash = hash(bt)
    output_dir = os.path.join(cfg.SESSION_DATA_FILE_PATH, str(bt_hash))
    os.makedirs(output_dir, exist_ok=True)
    # Write the JSON to a file in the output directory
    output_path = os.path.join(output_dir, "bilingual_text.json")
    with open(output_path, "w", encoding="utf-8") as out_f:
        out_f.write(bt.to_json())
    return bt_hash


def read_from_session_store(bilingual_text_hash: int, output_dir: str) -> BilingualText:
    bt_file_path = os.path.join(output_dir, "bilingual_text.json")
    if not os.path.exists(bt_file_path):
        raise FileNotFoundError(f"Bilingual text with hash {bilingual_text_hash} not found.")
    return BilingualText.from_json_file(bt_file_path)


def validate_translation_request(req: TranslationRequest, user):
    # Validate user role and text length
    role2maxlen = {UserRole.Admin: 100000,
                   UserRole.SupeAdmin: 50000, 
                   UserRole.User: 10000, UserRole.Guest: 1000} # TODO - move to config
    if role2maxlen.get(user.role, 200) < len(req.source_text):
        return JSONResponse(content={"error": "Text too long for your role"},
                            status_code=400)
    return None   


def get_test_blt():
    # This is a stub for the data for testing get_test_bilingual_text endpoint
    with open("src/tests/test_data/outputs/billing_text.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        bt: BilingualText = BilingualText.model_validate(data)
        return bt


# Serve the frontend static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # uvicorn src.main:app --reload
