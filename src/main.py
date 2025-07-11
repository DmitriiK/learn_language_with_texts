import json
import os
import logging
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from src.text_processing.nlp import lemmatize
from src.data_classes.lemma_index import LemmasIndex
from src.data_classes.bilingual_text import BilingualText
from src.tts.tts_generator import TTS_GEN, AudioOutputFormat
from src.pdf_gen.pdf_generator import generate_bilingual_pdf
from src.api.data_classes import TranslationRequest, LemmatizeRequest

from src.api.utils import (
    save_to_session_store,
    read_from_session_store,
    validate_translation_request,
    get_bilingual_text
)
import src.config as cfg
from src.authentication import get_current_user


TEST_MODE = False  # if True, we are using test instance of BilingualText from file instead of LLM-generated data
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


@app.get("/")
def index():
    with open("src/static/index.html") as f:
        return HTMLResponse(f.read())


@app.post("/api/make_bilingual2")
def make_bilingual2(req: TranslationRequest, user=Depends(get_current_user)):
    # This is a stub for the make_bilingual endpoint
    validation_response = validate_translation_request(req, user)
    if validation_response:
        return validation_response
    print("Received request for stub data")
    with open("src/tests/test_data/outputs/billing_text.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        bt: BilingualText = BilingualText.model_validate(data)
        bt_hash = save_to_session_store(bt)
        data["data_hash"] = bt_hash

    print("Returning stub data")
    return JSONResponse(content=data)


@app.post("/api/make_bilingual")
def make_bilingual(req: TranslationRequest, user=Depends(get_current_user)):
    try:
        result = get_bilingual_text(req, is_test_mode=TEST_MODE)
        # Only return JSON for both 'web' and 'json' output formats
        if req.output_format in ('web', 'json'):
            content = result.model_dump()
            content["data_hash"] = hash(result)
            return JSONResponse(content=content)
        else:
            return JSONResponse(content={"error": f"not valid output_format: {req.output_format}"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/api/make-pdf", response_class=Response)
def make_pdf(req: TranslationRequest, user=Depends(get_current_user)):
    """Endpoint to generate PDF from bilingual text data"""
    try:
        bilingual_text_instance = get_bilingual_text(req, is_test_mode=TEST_MODE)
        pdf_buffer = generate_bilingual_pdf(bilingual_text_instance)
        return Response(content=pdf_buffer, media_type="application/pdf")
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
        bilingual_text_instance = read_from_session_store(bilingual_text_hash, output_dir)
        audio_file_name = f"audio_{bilingual_text_hash}_{output_format}"
        output_audio_file_path = os.path.join(output_dir, audio_file_name)
        logging.info(f"Generating audio for bilingual text with hash {bilingual_text_hash} to {output_audio_file_path}")
        tts = TTS_GEN()
        tts.binlingual_to_audio(bln=bilingual_text_instance, break_time=f'{break_time_ms}ms', 
                                output_file_name=output_audio_file_path, aof=output_format)
        # Generate the URL relative to the static mount
        audio_url = f"/static/data/{bilingual_text_hash}/{audio_file_name}.mp3"
        return JSONResponse(content={"audio_url": audio_url})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


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


@app.get("/api/current_user")
def get_user_info(user=Depends(get_current_user)):
    return {"username": user.username, "role": user.role}


@app.post("/api/logout")
def logout():
    return Response(headers={"WWW-Authenticate": "Basic", "Clear-Site-Data": "*"})

@app.get("/login")
def login():
    with open("src/static/login.html") as f:
        return HTMLResponse(f.read())


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # uvicorn src.main:app --reload

